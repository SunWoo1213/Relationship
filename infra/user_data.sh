#!/bin/bash
# P9-infra U3b — EC2 첫 부팅 때 cloud-init 이 root 로 한 번 실행한다(정적 파일, templatefile 아님).
# 11 문서 §3-1~§3-4 를 대신한다: Docker 공식 apt 저장소 방식 설치 · ubuntu 를 docker 그룹에 · 저장소 clone.
# `curl … | sh` 식 설치는 쓰지 않는다(security §3) — 키 파일을 내려받아 저장소로 등록하고 apt 로 설치한다.
# .env 는 만들지 않는다 — 비밀은 사용자가 서버에서 직접 쓴다(security §1, 11 문서 §4).
# 진행 로그: /var/log/cloud-init-output.log  ·  끝났는지: cloud-init status --wait
set -euxo pipefail

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get upgrade -y
apt-get install -y ca-certificates curl git

# Docker 공식 문서 "Install using the apt repository" (Ubuntu) 그대로.
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

. /etc/os-release
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu ${UBUNTU_CODENAME:-$VERSION_CODENAME} stable" > /etc/apt/sources.list.d/docker.list

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

systemctl enable --now docker
usermod -aG docker ubuntu

# 공개 저장소를 ubuntu 사용자로 받는다(소유권이 처음부터 ubuntu). 이미 있으면 건너뛴다.
if [ ! -d /home/ubuntu/Relationship ]; then
  runuser -l ubuntu -c 'git clone https://github.com/SunWoo1213/Relationship.git /home/ubuntu/Relationship'
fi
