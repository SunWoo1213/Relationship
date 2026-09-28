"""${message}

Refs: TODO-패키지-태그
<%doc>
생성 직후 이 줄을 그 패키지 태그로 바꾼다(예: 해당 작업의 P/D/R/S 태그 나열).
고정 문자열로 두면 이후 만드는 모든 revision 이 같은 태그를 갖게 되어
`git log --grep` 추적이 틀어진다(FIX-007 F-c7078e).
</%doc>
Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, Sequence[str], None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    """Upgrade schema."""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """Downgrade schema."""
    ${downgrades if downgrades else "pass"}
