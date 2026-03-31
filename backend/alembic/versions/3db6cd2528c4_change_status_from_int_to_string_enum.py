"""change status from int to string enum

Revision ID: 3db6cd2528c4
Revises: 8b25e0a1bbde
Create Date: 2026-03-31 18:48:25.070737

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3db6cd2528c4'
down_revision: Union[str, None] = '8b25e0a1bbde'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite doesn't support ALTER COLUMN — use batch mode
    with op.batch_alter_table("scenarios") as batch_op:
        batch_op.alter_column(
            "status",
            existing_type=sa.INTEGER(),
            type_=sa.String(),
            existing_nullable=False,
        )

    # Convert existing data: 1 -> 'active', 0 -> 'inactive'
    op.execute(
        "UPDATE scenarios SET status = CASE "
        "WHEN status = '1' THEN 'active' "
        "WHEN status = '0' THEN 'inactive' "
        "ELSE 'active' END"
    )


def downgrade() -> None:
    # Convert back: 'active' -> 1, 'inactive' -> 0
    op.execute(
        "UPDATE scenarios SET status = CASE "
        "WHEN status = 'active' THEN '1' "
        "WHEN status = 'inactive' THEN '0' "
        "ELSE '1' END"
    )

    with op.batch_alter_table("scenarios") as batch_op:
        batch_op.alter_column(
            "status",
            existing_type=sa.String(),
            type_=sa.INTEGER(),
            existing_nullable=False,
        )
