# D7 · CloudFront → EC2 TLS 는 Caddy

상태: 유효 | 해결하는 검증: R14 | 원문: `docs/resolution-plan.md` §1 D7

**결정** EC2에 Caddy(자동 Let's Encrypt) 리버스 프록시, CloudFront 오리진 HTTPS. ALB 미사용. RDS 프라이빗 서브넷(NAT 없음), EC2만 퍼블릭. CloudFront용 ACM은 us-east-1.

**적용 시점** P9-infra.
