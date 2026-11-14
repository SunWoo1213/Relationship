"""Refs: P9-infra D17 R14 CR-005 U3b security §1 §3 §4 원칙8 -- Terraform 선언(`infra/`) 텍스트 검사.

`terraform` 바이너리가 없어도 돈다(이 Mac 에는 없다). `infra/*.tf`·`user_data.sh`·`terraform.tfvars.example`·
`.gitignore` 의 계약 값을 **텍스트로** 단언한다. DB·AWS·네트워크는 쓰지 않는다(skip 0).
`terraform fmt -check`·`validate` 는 설치 뒤에 따로 돌린다(03-log 에 남긴다).

HCL 은 파서를 쓰지 않고 중괄호 블록을 잘라 본다. 주석(`#`·`//`)과 빈 줄은 값 검사에서 뺀다.
변이 시험(V3-1~)은 이 파일과 `infra/`·`.gitignore` 를 스크래치패드 사본에 복사해 한 줄씩 어긋나게 만든 뒤 돌린다
-- 그래서 저장소 루트는 이 파일 위치(`<루트>/tests/`)에서 계산한다.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MAIN = "infra/main.tf"
VARIABLES = "infra/variables.tf"
OUTPUTS = "infra/outputs.tf"
USER_DATA = "infra/user_data.sh"
TFVARS_EXAMPLE = "infra/terraform.tfvars.example"
README = "infra/README.md"
GITIGNORE = ".gitignore"

TF_FILES = (MAIN, VARIABLES, OUTPUTS)

# 5종 자원 + 3종 조회만 허용 -- IAM·S3·Route 53·추가 보안 그룹 규칙 자원 등이 슬그머니 들어오는 것을 막는다.
ALLOWED_RESOURCES = {
    "aws_security_group",
    "aws_key_pair",
    "aws_instance",
    "aws_eip",
    "aws_eip_association",
}
ALLOWED_DATA = {"aws_vpc", "aws_subnets", "aws_ami"}


def _read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def _code_lines(text: str) -> list[str]:
    """주석(`#`·`//` 로 시작하는 줄)과 빈 줄을 뺀 줄 목록. 줄 끝 공백은 지운다."""
    out = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("//"):
            continue
        out.append(line.rstrip())
    return out


def _code_text(relpath: str) -> str:
    return "\n".join(_code_lines(_read(relpath)))


def _all_tf_code() -> str:
    return "\n".join(_code_text(p) for p in TF_FILES)


def _brace_blocks(text: str, header_regex: str) -> list[str]:
    """`header_regex` 로 시작해 `{` 로 여는 블록들의 중괄호 안쪽 본문을 모두 돌려준다(없으면 빈 목록)."""
    blocks = []
    for m in re.finditer(header_regex + r"\s*\{", text):
        depth = 1
        i = m.end()
        start = i
        while i < len(text) and depth:
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            i += 1
        blocks.append(text[start : i - 1])
    return blocks


def _resource_block(name: str, label: str = "app") -> str:
    blocks = _brace_blocks(_code_text(MAIN), rf'resource\s+"{name}"\s+"{label}"')
    assert len(blocks) == 1, f'resource "{name}" "{label}" 블록이 정확히 하나여야 한다(지금 {len(blocks)})'
    return blocks[0]


def _variable_block(name: str) -> str:
    blocks = _brace_blocks(_code_text(VARIABLES), rf'variable\s+"{name}"')
    assert len(blocks) == 1, f'variable "{name}" 블록이 정확히 하나여야 한다(지금 {len(blocks)})'
    return blocks[0]


def _attr(block: str, key: str) -> str | None:
    """블록 본문에서 한 줄짜리 `key = value` 의 value(문자열 그대로)를 돌려준다. 없으면 None."""
    m = re.search(rf"^\s*{re.escape(key)}\s*=\s*(.+?)\s*$", block, re.M)
    return m.group(1) if m else None


def _ingress_blocks() -> list[str]:
    return _brace_blocks(_resource_block("aws_security_group"), r"ingress")


def _gitignore_lines() -> list[str]:
    return [ln.strip() for ln in _read(GITIGNORE).splitlines() if ln.strip() and not ln.strip().startswith("#")]


# --- 비밀 탐지: 자격 증명 모양 문자열 -------------------------------------------------------------
_CRED_PATTERNS: dict[str, str] = {
    "aws-access-key-id": r"\b(AKIA|ASIA)[0-9A-Z]{16}\b",
    "aws-secret-like": r"(?i)aws_secret_access_key\s*=",
    "pem-private-key": "-----BEGIN " + "[A-Z ]*" + "PRIVATE KEY-----",
    "ssh-public-key-body": r"ssh-(ed25519|rsa)\s+AAAA[0-9A-Za-z+/=]{20,}",
    "12-digit-account-id": r"\b\d{12}\b",
}


# Canonical 의 AWS 계정 id 는 공개값이다(공식 Ubuntu AMI 소유자) -- 12자리 검사에서만 뺀다.
CANONICAL_OWNER_ID = "099720109477"


def _cred_hits(text: str) -> list[str]:
    text = text.replace(CANONICAL_OWNER_ID, "")
    return [name for name, pat in _CRED_PATTERNS.items() if re.search(pat, text)]


# ① -------------------------------------------------------------------------------------------
def test_infra_files_exist():
    """① 선언 파일 7개(`main.tf`·`variables.tf`·`outputs.tf`·`user_data.sh`·`tfvars.example`·`README.md`)가 있다."""
    for rel in (MAIN, VARIABLES, OUTPUTS, USER_DATA, TFVARS_EXAMPLE, README):
        assert (ROOT / rel).is_file(), f"{rel} 가 없다"


# ② -------------------------------------------------------------------------------------------
def test_only_allowed_resources_and_data_sources():
    """② 자원은 SG·키 페어·인스턴스·EIP·EIP 연결 5종, 조회는 VPC·서브넷·AMI 3종뿐 -- IAM·S3·Route 53 등은 없다."""
    code = _all_tf_code()
    resources = set(re.findall(r'^resource\s+"([A-Za-z0-9_]+)"', code, re.M))
    data = set(re.findall(r'^data\s+"([A-Za-z0-9_]+)"', code, re.M))
    assert resources == ALLOWED_RESOURCES, f"허용 밖 자원: {resources ^ ALLOWED_RESOURCES}"
    assert data == ALLOWED_DATA, f"허용 밖 조회: {data ^ ALLOWED_DATA}"


# ③ -------------------------------------------------------------------------------------------
def test_security_group_inbound_is_80_443_22_only():
    """③ 인바운드 규칙은 정확히 셋 -- 포트 집합 {80,443,22} (규칙 추가·포트 바뀜 모두 FAIL)."""
    blocks = _ingress_blocks()
    assert len(blocks) == 3, f"ingress 블록은 3개여야 한다(지금 {len(blocks)})"
    ports = []
    for b in blocks:
        frm, to = _attr(b, "from_port"), _attr(b, "to_port")
        assert frm == to, "한 규칙이 포트 범위를 열면 안 된다(from_port == to_port)"
        assert _attr(b, "protocol") == '"tcp"'
        ports.append(int(frm))  # type: ignore[arg-type]
    assert sorted(ports) == [22, 80, 443]


def test_security_group_http_https_open_ipv4_and_ipv6():
    """③b 80·443 은 `0.0.0.0/0` 과 `::/0` 둘 다(IPv6 가 빠지면 FAIL)."""
    for b in _ingress_blocks():
        if _attr(b, "from_port") in ("80", "443"):
            assert _attr(b, "cidr_blocks") == '["0.0.0.0/0"]'
            assert _attr(b, "ipv6_cidr_blocks") == '["::/0"]'


def test_security_group_ssh_cidr_is_the_variable_only():
    """③c 22 는 `var.ssh_cidr` 하나만 -- 리터럴 cidr 이나 IPv6 개방이 끼면 FAIL."""
    ssh = [b for b in _ingress_blocks() if _attr(b, "from_port") == "22"]
    assert len(ssh) == 1
    assert _attr(ssh[0], "cidr_blocks") == "[var.ssh_cidr]"
    assert _attr(ssh[0], "ipv6_cidr_blocks") is None
    assert not re.search(r"\d+\.\d+\.\d+\.\d+/\d+", ssh[0]), "22 규칙에 cidr 리터럴이 있다"


def test_no_db_or_backend_port_anywhere_in_main():
    """④ 5432·8000 은 `main.tf` 어디에도 없다(규칙·주석 아닌 코드 줄 기준)."""
    code = _code_text(MAIN)
    assert not re.search(r"\b(5432|8000)\b", code)


def test_egress_is_all_traffic():
    """⑤ 아웃바운드는 전체 허용(프로토콜 -1, 0.0.0.0/0, ::/0) -- apt·Docker 이미지 받기에 필요하다."""
    eg = _brace_blocks(_resource_block("aws_security_group"), r"egress")
    assert len(eg) == 1
    assert _attr(eg[0], "protocol") == '"-1"'
    assert _attr(eg[0], "from_port") == "0" and _attr(eg[0], "to_port") == "0"
    assert _attr(eg[0], "cidr_blocks") == '["0.0.0.0/0"]'
    assert _attr(eg[0], "ipv6_cidr_blocks") == '["::/0"]'


# ⑥ -------------------------------------------------------------------------------------------
def test_ssh_cidr_and_key_path_have_no_default():
    """⑥ `ssh_cidr`·`ssh_public_key_path` 는 기본값이 없다 -- 사용자가 tfvars 로 줘야 하고 `0.0.0.0/0` 기본이 생기면 FAIL."""
    for name in ("ssh_cidr", "ssh_public_key_path"):
        block = _variable_block(name)
        assert _attr(block, "default") is None, f"{name} 에 default 가 있다"
        assert _attr(block, "type") == "string"


def test_variable_defaults_are_the_decided_values():
    """⑦ 결정 A·C 의 값 -- region `ap-northeast-2`·`t4g.small`·`arm64`·gp3 20GB·태그 `relationship-demo`."""
    assert _attr(_variable_block("region"), "default") == '"ap-northeast-2"'
    assert _attr(_variable_block("instance_type"), "default") == '"t4g.small"'
    assert _attr(_variable_block("ami_architecture"), "default") == '"arm64"'
    assert _attr(_variable_block("root_volume_gb"), "default") == "20"
    assert _attr(_variable_block("project_tag"), "default") == '"relationship-demo"'


def test_variables_declared_are_exactly_the_planned_set():
    """⑧ 변수는 계획 목록 7개뿐 -- `aws_profile` 같은 자격 증명 변수가 생기면 FAIL."""
    names = set(re.findall(r'^variable\s+"([A-Za-z0-9_]+)"', _code_text(VARIABLES), re.M))
    assert names == {
        "region",
        "instance_type",
        "ami_architecture",
        "ssh_public_key_path",
        "ssh_cidr",
        "root_volume_gb",
        "project_tag",
    }


# ⑨ -------------------------------------------------------------------------------------------
def test_root_volume_gp3_delete_on_termination_true():
    """⑨ 루트 볼륨 gp3 · 크기는 변수 · `delete_on_termination = true`(종료 때 볼륨이 남아 과금되지 않게, 12 문서 4번)."""
    inst = _resource_block("aws_instance")
    root = _brace_blocks(inst, r"root_block_device")
    assert len(root) == 1
    assert _attr(root[0], "volume_type") == '"gp3"'
    assert _attr(root[0], "volume_size") == "var.root_volume_gb"
    assert _attr(root[0], "delete_on_termination") == "true"


def test_instance_uses_variable_type_security_group_key_and_static_user_data():
    """⑩ 인스턴스: 유형은 변수 · 보안 그룹·키 페어는 이 파일의 자원 · user-data 는 정적 파일(templatefile 아님)."""
    inst = _resource_block("aws_instance")
    assert _attr(inst, "instance_type") == "var.instance_type"
    assert _attr(inst, "vpc_security_group_ids") == "[aws_security_group.app.id]"
    assert _attr(inst, "key_name") == "aws_key_pair.app.key_name"
    assert _attr(inst, "user_data") == 'file("${path.module}/user_data.sh")'
    assert "templatefile" not in _all_tf_code()


def test_ami_is_looked_up_from_canonical_not_hardcoded():
    """⑪ AMI 는 `data "aws_ami"`(Canonical 099720109477, ubuntu-noble-24.04 gp3 이미지 최신) -- `ami-xxxx` 리터럴이면 FAIL."""
    code = _all_tf_code()
    assert not re.search(r"\bami-[0-9a-f]{8,}\b", code), "AMI id 가 하드코딩됐다"
    ami = _brace_blocks(code, r'data\s+"aws_ami"\s+"ubuntu"')
    assert len(ami) == 1
    assert _attr(ami[0], "most_recent") == "true"
    assert _attr(ami[0], "owners") == '["099720109477"]'
    assert "ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-${var.ami_architecture}-server-*" in ami[0]
    assert _attr(_resource_block("aws_instance"), "ami") == "data.aws_ami.ubuntu.id"


def test_default_vpc_and_default_subnets_are_used():
    """⑫ 기본 VPC(`default = true`)·기본 서브넷(`default-for-az`)을 조회해 쓴다 -- 새 VPC·서브넷을 만들지 않는다."""
    code = _code_text(MAIN)
    vpc = _brace_blocks(code, r'data\s+"aws_vpc"\s+"default"')
    assert len(vpc) == 1 and _attr(vpc[0], "default") == "true"
    assert '"default-for-az"' in code
    assert _attr(_resource_block("aws_instance"), "subnet_id") == "sort(data.aws_subnets.default.ids)[0]"


def test_key_pair_registers_public_key_from_variable_path():
    """⑬ 키 페어는 `file(pathexpand(var.ssh_public_key_path))` 의 공개키만 등록한다(개인키는 코드에 없다)."""
    kp = _resource_block("aws_key_pair")
    assert _attr(kp, "public_key") == "file(pathexpand(var.ssh_public_key_path))"
    assert "private_key" not in _all_tf_code()


def test_elastic_ip_is_associated_with_the_instance():
    """⑭ Elastic IP 를 만들고 인스턴스에 연결한다(호스트명이 IP 에 묶인다)."""
    assert _attr(_resource_block("aws_eip"), "domain") == '"vpc"'
    assoc = _resource_block("aws_eip_association")
    assert _attr(assoc, "instance_id") == "aws_instance.app.id"
    assert _attr(assoc, "allocation_id") == "aws_eip.app.id"


def test_tags_project_and_shutdown_by():
    """⑮ 태그 `Project = var.project_tag` · `ShutdownBy = 2026-11-19T18:00+09:00`(종료 시한, 12 문서)."""
    code = _code_text(MAIN)
    locals_ = _brace_blocks(code, r"locals")
    assert len(locals_) == 1
    tags = _brace_blocks(locals_[0], r"tags\s*=")
    assert len(tags) == 1
    assert _attr(tags[0], "Project") == "var.project_tag"
    assert _attr(tags[0], "ShutdownBy") == '"2026-11-19T18:00+09:00"'
    for res in ("aws_security_group", "aws_key_pair", "aws_eip"):
        assert _attr(_resource_block(res), "tags") == "local.tags"


def test_lifecycle_ignores_ami_and_user_data_changes():
    """⑯ 인스턴스 `lifecycle.ignore_changes` 가 ami·user_data -- 재 plan 이 인스턴스를 교체(DB 볼륨 소실)하지 않게 한다."""
    lc = _brace_blocks(_resource_block("aws_instance"), r"lifecycle")
    assert len(lc) == 1
    assert _attr(lc[0], "ignore_changes") == "[ami, user_data]"


# ⑰ -------------------------------------------------------------------------------------------
def test_provider_pinned_and_has_no_credentials():
    """⑰ provider 는 `region` 만 -- `access_key`·`secret_key`·`profile`·`token`·자격 증명 파일 속성이 없다(security §1)."""
    code = _all_tf_code()
    prov = _brace_blocks(code, r'provider\s+"aws"')
    assert len(prov) == 1
    keys = set(re.findall(r"^\s*([A-Za-z_]+)\s*=", prov[0], re.M))
    assert keys == {"region"}, f"provider 에 region 밖 속성이 있다: {keys}"
    for forbidden in ("access_key", "secret_key", "profile", "token", "shared_credentials", "shared_config"):
        assert not re.search(rf"\b{forbidden}\w*\s*=", code), f"{forbidden} 속성이 있다"


def test_terraform_and_provider_versions_are_pinned():
    """⑱ `required_version >= 1.5` · aws provider `~> 5.0`."""
    code = _code_text(MAIN)
    tf = _brace_blocks(code, r"terraform")
    assert len(tf) == 1
    assert _attr(tf[0], "required_version") == '">= 1.5"'
    assert re.search(r'source\s*=\s*"hashicorp/aws"', tf[0])
    assert re.search(r'version\s*=\s*"~> 5\.0"', tf[0])


def test_no_credential_shaped_strings_in_infra_files():
    """⑲ `infra/` 의 모든 파일에 액세스 키 id·PEM·공개키 본문·12자리 계정 ID 모양 문자열이 없다."""
    for rel in (*TF_FILES, USER_DATA, TFVARS_EXAMPLE, README):
        assert _cred_hits(_read(rel)) == [], f"{rel}: {_cred_hits(_read(rel))}"


def test_credential_detector_catches_samples():
    """⑲-전제 탐지기가 표본 4종을 실제로 잡는다(탐지기가 죽어 있으면 ⑲ 가 항상 통과한다)."""
    samples = {
        "aws-access-key-id": "AKIA" + "ABCDEFGHIJKLMNOP",
        "pem-private-key": "-----BEGIN " + "OPENSSH PRIVATE KEY-----",
        "ssh-public-key-body": "ssh-ed25519 " + "AAAA" + "C3NzaC1lZDI1NTE5AAAAIabcdefghijklmnop",
        "12-digit-account-id": "123456789012",
    }
    for name, sample in samples.items():
        assert name in _cred_hits(sample), name
    assert _cred_hits("ssh_cidr = \"YOUR.IP.HERE/32\"") == []


# ⑳ -------------------------------------------------------------------------------------------
def test_outputs_declared_with_expected_values():
    """⑳ 출력 4개 -- `public_ip`·`ssh_command`·`sslip_hostname`·`instance_id` (sslip 는 `.`→`-` 치환 + `.sslip.io`)."""
    code = _code_text(OUTPUTS)
    names = set(re.findall(r'^output\s+"([A-Za-z0-9_]+)"', code, re.M))
    assert names == {"public_ip", "ssh_command", "sslip_hostname", "instance_id"}
    blocks = {n: _brace_blocks(code, rf'output\s+"{n}"')[0] for n in names}
    assert _attr(blocks["public_ip"], "value") == "aws_eip.app.public_ip"
    assert _attr(blocks["instance_id"], "value") == "aws_instance.app.id"
    assert _attr(blocks["sslip_hostname"], "value") == '"${replace(aws_eip.app.public_ip, ".", "-")}.sslip.io"'


def test_ssh_command_output_has_no_private_key_path():
    """⑳b `ssh_command` 는 `ubuntu@<ip>` 모양이고 개인키 경로(`.pem`·`~/`·`/Users/`·`/home/`)를 담지 않는다."""
    block = _brace_blocks(_code_text(OUTPUTS), r'output\s+"ssh_command"')[0]
    value = _attr(block, "value")
    assert value is not None
    assert value.startswith('"ssh -i ') and "ubuntu@${aws_eip.app.public_ip}" in value
    for bad in (".pem", "~/", "/Users/", "/home/", "id_ed25519"):
        assert bad not in value


# 21 ------------------------------------------------------------------------------------------
def test_user_data_installs_docker_from_apt_repository():
    """21 user-data 가 Docker 를 공식 apt 저장소 방식으로 설치한다 -- 키링 파일·sources list·패키지 5종."""
    code = _code_text(USER_DATA)
    assert "/etc/apt/keyrings/docker.asc" in code
    assert "https://download.docker.com/linux/ubuntu/gpg" in code
    assert "/etc/apt/sources.list.d/docker.list" in code
    assert re.search(
        r"apt-get install -y docker-ce docker-ce-cli containerd\.io docker-buildx-plugin docker-compose-plugin\b",
        code,
    )
    assert "get.docker.com" not in code


def test_user_data_has_no_download_pipe_to_shell():
    """22 user-data 에 `curl|wget … | sh/bash`·`iex(DownloadString)` 가 없다 -- 파일로 받아 저장소 등록 (security §3)."""
    code = _code_text(USER_DATA)
    assert not re.search(r"\b(curl|wget)\b[^\n|]*\|\s*(sudo\s+)?(ba|z|da)?sh\b", code)
    assert not re.search(r"(?i)DownloadString", code)
    assert not re.search(r"<\(\s*(curl|wget)", code), "프로세스 치환 실행도 같은 위험이다"


def test_user_data_docker_group_clone_and_no_env_file():
    """23 `ubuntu` 를 docker 그룹에 · 공개 저장소를 ubuntu 소유로 clone · `.env` 는 만들지 않는다(security §1)."""
    code = _code_text(USER_DATA)
    assert re.search(r"^usermod -aG docker ubuntu$", code, re.M)
    assert "git clone https://github.com/SunWoo1213/Relationship.git /home/ubuntu/Relationship" in code
    assert re.search(r"runuser -l ubuntu -c ", code), "clone 은 ubuntu 사용자로 해야 소유권이 맞다"
    assert not re.search(r"\.env\b", code), "user-data 가 .env 를 건드린다"
    assert not re.search(r"\bchown\b|\bchmod\s+-R\b|\brm\s+-r", code)
    assert code.splitlines()[0] == "set -euxo pipefail", "첫 실행 줄이 set -euxo pipefail 이 아니다(실패해도 계속 달린다)"


def test_user_data_starts_with_bash_shebang():
    """24 cloud-init 이 스크립트로 읽도록 첫 줄이 `#!/bin/bash`(주석 제거 전 원문 기준)."""
    assert _read(USER_DATA).splitlines()[0] == "#!/bin/bash"


# 25 ------------------------------------------------------------------------------------------
def test_gitignore_blocks_state_vars_and_plugin_cache():
    """25 `.gitignore` 가 tfstate·`.terraform/`·tfvars 를 막고 example 만 예외로 둔다 -- 줄 하나라도 지우면 FAIL."""
    lines = _gitignore_lines()
    for needed in (
        "infra/.terraform/",
        "infra/*.tfstate",
        "infra/*.tfstate.*",
        "infra/*.tfvars",
        "!infra/terraform.tfvars.example",
    ):
        assert needed in lines, f".gitignore 에 `{needed}` 가 없다"
    assert lines.index("!infra/terraform.tfvars.example") > lines.index("infra/*.tfvars"), (
        "예외 줄이 ignore 줄보다 앞이면 효과가 없다"
    )


def test_gitignore_does_not_ignore_lock_file_or_tf_sources():
    """26 `.terraform.lock.hcl` 은 커밋 대상 -- ignore 줄이 없고 `infra/` 통째로·`*.tf`·`*.hcl` 을 막지도 않는다."""
    for ln in _gitignore_lines():
        if ln.startswith("!"):
            continue
        assert "lock.hcl" not in ln and ".hcl" not in ln, f"lock 파일을 막는 줄: {ln}"
        assert ln.rstrip("/") != "infra", "infra/ 통째로 ignore"
        assert ln not in ("*.tf", "infra/*.tf", "infra/*", "*.sh", "infra/*.sh"), f"소스를 막는 줄: {ln}"


def test_no_state_or_vars_files_are_present_in_tree():
    """27 `infra/` 에 tfstate·tfvars(example 제외)·`.terraform/` 가 놓여 있지 않다 -- 에이전트는 apply 한 적이 없다."""
    infra = ROOT / "infra"
    names = {p.name for p in infra.iterdir()}
    assert ".terraform" not in names
    for n in names:
        assert ".tfstate" not in n, n
        if n.endswith(".tfvars"):
            raise AssertionError(f"{n}: 실제 변수 파일이 있다")


# 28 ------------------------------------------------------------------------------------------
def test_tfvars_example_has_placeholders_only():
    """28 example 은 값이 자리표뿐 -- 활성 줄은 필수 두 변수(`ssh_cidr`·`ssh_public_key_path`)이고 값에 `YOUR` 가 든다."""
    active = {}
    for line in _code_lines(_read(TFVARS_EXAMPLE)):
        m = re.match(r'^(\w+)\s*=\s*"(.*)"$', line.strip())
        assert m, f"예상 밖 줄: {line}"
        active[m.group(1)] = m.group(2)
    assert set(active) == {"ssh_cidr", "ssh_public_key_path"}
    for key, value in active.items():
        assert "YOUR" in value, f"{key} 값이 자리표가 아니다: {value}"
    assert not re.search(r"\b\d+\.\d+\.\d+\.\d+\b", _read(TFVARS_EXAMPLE).replace("YOUR.IP.HERE", "")), (
        "example 에 실제 IP 모양이 있다"
    )
    declared = set(re.findall(r'^variable\s+"(\w+)"', _code_text(VARIABLES), re.M))
    assert set(active) <= declared


# 29 ------------------------------------------------------------------------------------------
def test_readme_documents_order_and_guards():
    """29 README 에 실행 순서(init·validate·plan·apply·output)·`AWS_PROFILE`·destroy 는 사용자 몫·상태 파일 커밋 금지가 있다."""
    text = _read(README)
    for needed in (
        "AWS_PROFILE=<프로필 이름> terraform -chdir=infra init",
        "terraform -chdir=infra validate",
        "terraform -chdir=infra plan -var-file=terraform.tfvars",
        "terraform -chdir=infra apply -var-file=terraform.tfvars",
        "terraform -chdir=infra output",
        "terraform -chdir=infra destroy",
        "11 문서 §3-4",
        "12 문서",
        "infra/terraform.tfstate",
    ):
        assert needed in text, f"README 에 `{needed}` 가 없다"
    assert "사용자가 직접" in text and "safety-guard" in text
    assert "-auto-approve" not in re.sub(r"`apply -auto-approve`[^\n]*", "", text), (
        "README 가 auto-approve 를 권하는 명령으로 쓴다"
    )
