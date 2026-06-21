"""store the user's interface language

Revision ID: b85c1e4d2f70
Revises: f74b2d9e1a63
"""
from alembic import op
import sqlalchemy as sa


revision = 'b85c1e4d2f70'
down_revision = 'f74b2d9e1a63'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('locale', sa.String(length=10), nullable=False, server_default='pt-BR'))


def downgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('locale')
