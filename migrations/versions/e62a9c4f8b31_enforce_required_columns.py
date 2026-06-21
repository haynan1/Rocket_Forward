"""enforce required columns on legacy databases

Revision ID: e62a9c4f8b31
Revises: c43f7a8d1e22
"""
from alembic import op
import sqlalchemy as sa


revision = 'e62a9c4f8b31'
down_revision = 'c43f7a8d1e22'
branch_labels = None
depends_on = None


REQUIRED_COLUMNS = {
    'achievement': [('key', sa.String(80)), ('title', sa.String(100)), ('description', sa.String(255)), ('icon', sa.String(40)), ('group', sa.String(40))],
    'goal': [('priority', sa.String(10)), ('category', sa.String(30)), ('status', sa.String(20)), ('created_at', sa.DateTime()), ('recurrence_type', sa.String(15))],
    'notification': [('user_id', sa.Integer()), ('goal_id', sa.Integer()), ('scheduled_for', sa.DateTime())],
    'user': [('theme_mode', sa.String(10)), ('motivational_phrases_enabled', sa.Boolean()), ('is_premium', sa.Boolean()), ('notifications_enabled', sa.Boolean()), ('created_at', sa.DateTime())],
    'user_achievement': [('user_id', sa.Integer()), ('achievement_id', sa.Integer()), ('unlocked_at', sa.DateTime())],
}


def _alter(nullable):
    for table, columns in REQUIRED_COLUMNS.items():
        with op.batch_alter_table(table, schema=None) as batch_op:
            for name, column_type in columns:
                batch_op.alter_column(name, existing_type=column_type, nullable=nullable)


def upgrade():
    _alter(False)


def downgrade():
    _alter(True)
