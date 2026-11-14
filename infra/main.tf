# P9-infra U3b — EC2 한 대 + 보안 그룹 + 키 페어 + Elastic IP 를 Terraform 으로 선언한다.
# Refs: P9-infra D17 R14 CR-005 결정 A(t4g.small·gp3 20GB) B(DNS 는 Terraform 밖) C(ap-northeast-2) D(SSH 22 는 변수 cidr)
#
# 이 파일이 대신하는 것 = docs/user-setup/11-ec2-minimal-deploy.md §1~§2 (콘솔 작업).
# 이 파일이 하지 않는 것 = .env 생성(비밀은 사용자 손, security §1) · Route 53 · IAM · S3 백엔드 · 모듈화.
#
# 자격 증명은 이 코드 어디에도 없다. provider 에 access_key/secret_key/profile 속성을 쓰지 않고,
# 실행할 때 환경변수 AWS_PROFILE(과 AWS_REGION 또는 변수 region)로만 받는다 — security §1.
# 에이전트는 init·validate·plan 까지만 돌린다. apply 와 destroy 는 둘 다 사용자가 직접 실행한다
# (security §4 "apply/destroy 는 사용자"; apply -auto-approve·destroy 는 safety-guard 가 막는다) — README.md.

terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

locals {
  # 모든 자원에 같은 태그 — Project 로 콘솔에서 이 배포의 자원만 골라 보고, ShutdownBy 로 종료 시한을 남긴다(12 문서).
  tags = {
    Project    = var.project_tag
    ShutdownBy = "2026-11-19T18:00+09:00"
  }
}

# --- 조회 전용(data) -------------------------------------------------------------------------

# 기본 VPC — 새 VPC 를 만들지 않는다(결정 S).
data "aws_vpc" "default" {
  default = true
}

# 기본 VPC 의 기본 서브넷(AZ 마다 하나, 퍼블릭). 이름순 첫 번째를 쓴다.
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }

  filter {
    name   = "default-for-az"
    values = ["true"]
  }
}

# Canonical(099720109477) 공식 Ubuntu 24.04 LTS 이미지 중 최신. AMI id 를 코드에 박지 않는다 — 리전마다 다르고 낡는다.
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-${var.ami_architecture}-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# --- 자원 ------------------------------------------------------------------------------------

# 인바운드는 80·443(전체) + 22(var.ssh_cidr 만). 5432·8000 규칙은 없다 — DB 와 백엔드는 compose 내부망에만 있다(U1 ③④).
# 설명 문자열은 AWS 가 ASCII 만 받는다.
resource "aws_security_group" "app" {
  name        = "${var.project_tag}-sg"
  description = "relationship demo: 80/443 public, 22 from ssh_cidr only"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description      = "HTTP (Caddy redirects to https)"
    from_port        = 80
    to_port          = 80
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  ingress {
    description      = "HTTPS (Caddy)"
    from_port        = 443
    to_port          = 443
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  ingress {
    description = "SSH from ssh_cidr only"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.ssh_cidr]
  }

  egress {
    description      = "all outbound"
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = local.tags
}

# 공개키만 등록한다. 개인키는 사용자 PC 에만 있고 이 코드·상태 파일에 들어오지 않는다.
# file() 은 ~ 를 풀지 않아서 pathexpand 를 거친다.
resource "aws_key_pair" "app" {
  key_name   = "${var.project_tag}-key"
  public_key = file(pathexpand(var.ssh_public_key_path))
  tags       = local.tags
}

resource "aws_instance" "app" {
  ami                         = data.aws_ami.ubuntu.id
  instance_type               = var.instance_type
  subnet_id                   = sort(data.aws_subnets.default.ids)[0]
  vpc_security_group_ids      = [aws_security_group.app.id]
  key_name                    = aws_key_pair.app.key_name
  associate_public_ip_address = true
  user_data                   = file("${path.module}/user_data.sh")

  root_block_device {
    volume_type           = "gp3"
    volume_size           = var.root_volume_gb
    delete_on_termination = true
  }

  # 기동 뒤 plan 이 AMI 최신화·user-data 수정만으로 인스턴스를 교체하려 들면(= 루트 볼륨의 DB 소실) 막는다.
  # 보안 그룹 규칙 변경(예: 22 의 cidr, 13 문서 D-2)은 원래 인스턴스를 건드리지 않는다 — 이 블록은 그와 별개로
  # 같은 apply 에서 AMI 가 바뀌어 있어도 인스턴스가 교체되지 않게 하는 안전장치다.
  lifecycle {
    ignore_changes = [ami, user_data]
  }

  tags = merge(local.tags, { Name = "${var.project_tag}-app" })
}

# 호스트명이 IP 에 묶이므로 Elastic IP 가 필수다(11 문서 2-2). 종료 때 해제하지 않으면 과금된다(12 문서).
resource "aws_eip" "app" {
  domain = "vpc"
  tags   = local.tags
}

resource "aws_eip_association" "app" {
  instance_id   = aws_instance.app.id
  allocation_id = aws_eip.app.id
}
