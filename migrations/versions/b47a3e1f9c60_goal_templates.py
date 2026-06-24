"""add reusable goal templates

Revision ID: b47a3e1f9c60
Revises: d2c71eaf901b
"""
from alembic import op
import sqlalchemy as sa


revision = 'b47a3e1f9c60'
down_revision = 'd2c71eaf901b'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'goal_template',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=160), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('link_url', sa.String(length=2048), nullable=True),
        sa.Column('time', sa.Time(), nullable=True),
        sa.Column('show_on_board', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('priority', sa.String(length=10), nullable=False, server_default='media'),
        sa.Column('category', sa.String(length=30), nullable=False, server_default='pessoal'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_goal_template_user_id', 'goal_template', ['user_id'], unique=False)


def downgrade():
    op.drop_index('ix_goal_template_user_id', table_name='goal_template')
    op.drop_table('goal_template')
