"""premium motivational phrases

Revision ID: a91d3f5b7c20
Revises: 68fd20daf906
"""
from alembic import op
import sqlalchemy as sa


revision = 'a91d3f5b7c20'
down_revision = '68fd20daf906'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('phrase_interval_minutes', sa.Integer(), nullable=False, server_default='30'))
    op.create_table(
        'motivational_phrase',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('motivational_phrase', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_motivational_phrase_user_id'), ['user_id'], unique=False)


def downgrade():
    with op.batch_alter_table('motivational_phrase', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_motivational_phrase_user_id'))
    op.drop_table('motivational_phrase')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('phrase_interval_minutes')
