# P9-infra U3b — 입력 변수. 기본값이 없는 것(ssh_cidr · ssh_public_key_path)은 사용자가 terraform.tfvars 로 준다.
# 자격 증명 변수는 없다 — 환경변수 AWS_PROFILE 로만 받는다(security §1).

variable "region" {
  description = "AWS 리전 (결정 C — 서울)"
  type        = string
  default     = "ap-northeast-2"
}

variable "instance_type" {
  description = "EC2 인스턴스 유형 (결정 A — ARM 2GB)"
  type        = string
  default     = "t4g.small"
}

variable "ami_architecture" {
  description = "Ubuntu AMI 아키텍처. t4g 같은 Graviton 은 arm64, t3 같은 Intel 은 amd64"
  type        = string
  default     = "arm64"

  validation {
    condition     = contains(["arm64", "amd64"], var.ami_architecture)
    error_message = "ami_architecture must be arm64 or amd64."
  }
}

variable "ssh_public_key_path" {
  description = "EC2 에 등록할 ed25519 공개키 파일 경로 (예: ~/.ssh/relationship-deploy.pub). 개인키는 사용자 PC 에만 둔다"
  type        = string
}

variable "ssh_cidr" {
  description = "SSH(22) 를 허용할 내 공인 IP 의 cidr (예: 203.0.113.7/32). 기동 당일 다시 확인한다 — 13 문서 A-9"
  type        = string
}

variable "root_volume_gb" {
  description = "루트 볼륨(gp3) 크기 GB (결정 A)"
  type        = number
  default     = 20
}

variable "project_tag" {
  description = "모든 자원에 붙는 Project 태그이자 자원 이름 접두사"
  type        = string
  default     = "relationship-demo"
}
