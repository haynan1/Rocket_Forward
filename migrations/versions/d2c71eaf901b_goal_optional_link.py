"""add optional link to goals

Revision ID: d2c71eaf901b
Revises: b85c1e4d2f70
"""
from alembic import op
import sqlalchemy as sa


revision = 'd2c71eaf901b'
down_revision = 'b85c1e4d2f70'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('goal', schema=None) as batch_op:
        batch_op.add_column(sa.Column('link_url', sa.String(length=2048), nullable=True))


def downgrade():
    with op.batch_alter_table('goal', schema=None) as batch_op:
        batch_op.drop_column('link_url')
