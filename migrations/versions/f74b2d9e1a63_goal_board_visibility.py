"""add per-goal board visibility

Revision ID: f74b2d9e1a63
Revises: e62a9c4f8b31
"""
from alembic import op
import sqlalchemy as sa


revision = 'f74b2d9e1a63'
down_revision = 'e62a9c4f8b31'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('goal', schema=None) as batch_op:
        batch_op.add_column(sa.Column('show_on_board', sa.Boolean(), nullable=False, server_default=sa.true()))


def downgrade():
    with op.batch_alter_table('goal', schema=None) as batch_op:
        batch_op.drop_column('show_on_board')
