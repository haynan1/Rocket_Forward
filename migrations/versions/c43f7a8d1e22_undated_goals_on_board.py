"""choose whether undated goals appear on board

Revision ID: c43f7a8d1e22
Revises: a91d3f5b7c20
"""
from alembic import op
import sqlalchemy as sa


revision = 'c43f7a8d1e22'
down_revision = 'a91d3f5b7c20'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('show_undated_on_board', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('show_undated_on_board')
