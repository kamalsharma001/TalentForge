"""add time and competency tracking fields to mock_interviews

Revision ID: 9a1b2c3d4e5f
Revises: 8f2a1b9c3d4e
Create Date: 2026-09-22 12:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a1b2c3d4e5f'
down_revision = '8f2a1b9c3d4e'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('mock_interviews', sa.Column('duration_mode', sa.String(length=20), server_default='30', nullable=True))
    op.add_column('mock_interviews', sa.Column('started_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('mock_interviews', sa.Column('actual_duration_secs', sa.Integer(), nullable=True))
    op.add_column('mock_interviews', sa.Column('completion_reason', sa.String(length=50), nullable=True))
    op.add_column('mock_interviews', sa.Column('blueprint', sa.Text(), nullable=True))
    op.add_column('mock_interviews', sa.Column('live_competency_state', sa.Text(), nullable=True))
    op.add_column('mock_interviews', sa.Column('live_claims_state', sa.Text(), nullable=True))


def downgrade():
    op.drop_column('mock_interviews', 'live_claims_state')
    op.drop_column('mock_interviews', 'live_competency_state')
    op.drop_column('mock_interviews', 'blueprint')
    op.drop_column('mock_interviews', 'completion_reason')
    op.drop_column('mock_interviews', 'actual_duration_secs')
    op.drop_column('mock_interviews', 'started_at')
    op.drop_column('mock_interviews', 'duration_mode')
