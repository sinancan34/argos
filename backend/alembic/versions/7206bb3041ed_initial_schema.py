"""initial schema

Revision ID: 7206bb3041ed
Revises: 
Create Date: 2026-04-01 00:45:05.548268

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7206bb3041ed'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('devices',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('meta', sa.JSON(), nullable=False),
    sa.Column('status', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.String(), nullable=False),
    sa.Column('updated_at', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('scenarios',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('status', sa.Boolean(), nullable=False),
    sa.Column('step_timeout', sa.Integer(), nullable=False),
    sa.Column('validation_timeout', sa.Integer(), nullable=False),
    sa.Column('steps', sa.JSON(), nullable=False),
    sa.Column('validations', sa.JSON(), nullable=False),
    sa.Column('device_id', sa.String(), nullable=False),
    sa.Column('created_at', sa.String(), nullable=False),
    sa.Column('updated_at', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['device_id'], ['devices.id'], name='fk_scenarios_device_id_devices'),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('scenarios')
    op.drop_table('devices')
