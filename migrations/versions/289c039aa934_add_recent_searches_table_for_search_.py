"""Add recent_searches table for search history

Revision ID: 289c039aa934
Revises: 578f42f280ed
Create Date: 2026-03-08 19:47:51.569116

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '289c039aa934'
down_revision = '578f42f280ed'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('recent_searches',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('query', sa.String(length=200), nullable=False),
    sa.Column('creado_en', sa.DateTime(), nullable=False),
    sa.Column('actualizado_en', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('recent_searches', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_recent_searches_user_id'), ['user_id'], unique=False)


def downgrade():
    with op.batch_alter_table('recent_searches', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_recent_searches_user_id'))

    op.drop_table('recent_searches')
