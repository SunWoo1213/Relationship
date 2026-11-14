# P9-infra U3b — apply 뒤 `terraform -chdir=infra output` 로 보는 값. 비밀은 없다(IP 는 비밀이 아니다).

output "public_ip" {
  description = "Elastic IP — 11 문서 §5 의 A 레코드 대상"
  value       = aws_eip.app.public_ip
}

# 개인키 경로는 사용자만 안다 — 자리표로 둔다.
output "ssh_command" {
  description = "SSH 접속 명령 (개인키 경로를 채워서 쓴다)"
  value       = "ssh -i <PRIVATE_KEY_PATH> ubuntu@${aws_eip.app.public_ip}"
}

# 도메인이 아직 없을 때 SITE_ADDRESS 로 쓰는 호스트명(결정 B). DNS 는 Terraform 이 하지 않는다.
output "sslip_hostname" {
  description = "도메인 준비 전 임시 호스트명 (<EIP 를 대시로>.sslip.io)"
  value       = "${replace(aws_eip.app.public_ip, ".", "-")}.sslip.io"
}

output "instance_id" {
  description = "EC2 인스턴스 id"
  value       = aws_instance.app.id
}
