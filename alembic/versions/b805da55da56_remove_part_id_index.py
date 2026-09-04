"""remove part_id index

Revision ID: b805da55da56
Revises: d3e89c402e4c
Create Date: 2026-09-04 21:05:17.286702

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b805da55da56'
down_revision: Union[str, Sequence[str], None] = 'd3e89c402e4c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("spare_parts") as batch_op:

        batch_op.create_unique_constraint("uq_spare_parts_part_id", ["part_id"])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("spare_parts") as batch_op:
        batch_op.drop_constraint("uq_spare_parts_part_id", type_="unique")
        batch_op.create_index(
            op.f("ix_spare_parts_part_id"), ["part_id"], unique=True
        )