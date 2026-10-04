"""add mock interview messages and multi-turn fields

Revision ID: e5c89201f9ab
Revises: cf1162c2b3ec
Create Date: 2026-09-21 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'e5c89201f9ab'
down_revision = 'cf1162c2b3ec'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Add new columns to mock_interviews
    op.add_column('mock_interviews', sa.Column('interview_id', sa.UUID(), nullable=True))
    op.add_column('mock_interviews', sa.Column('tech_stack', sa.ARRAY(sa.String()), nullable=True))
    op.add_column('mock_interviews', sa.Column('evaluation_rubric', sa.Text(), nullable=True))
    op.add_column('mock_interviews', sa.Column('recommendations', sa.Text(), nullable=True))
    op.create_foreign_key(
        'fk_mock_interviews_interview_id',
        'mock_interviews',
        'interviews',
        ['interview_id'],
        ['id'],
        ondelete='SET NULL'
    )
    op.create_index(
        op.f('ix_mock_interviews_interview_id'),
        'mock_interviews',
        ['interview_id'],
        unique=False
    )

    # 2. Create mock_interview_messages table
    op.create_table(
        'mock_interview_messages',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('mock_interview_id', sa.UUID(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('sequence', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['mock_interview_id'],
            ['mock_interviews.id'],
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        op.f('ix_mock_interview_messages_mock_interview_id'),
        'mock_interview_messages',
        ['mock_interview_id'],
        unique=False
    )


def downgrade():
    op.drop_index(op.f('ix_mock_interview_messages_mock_interview_id'), table_name='mock_interview_messages')
    op.drop_table('mock_interview_messages')

    op.drop_index(op.f('ix_mock_interviews_interview_id'), table_name='mock_interviews')
    op.drop_constraint('fk_mock_interviews_interview_id', 'mock_interviews', type_='foreignkey')
    op.drop_column('mock_interviews', 'recommendations')
    op.drop_column('mock_interviews', 'evaluation_rubric')
    op.drop_column('mock_interviews', 'tech_stack')
    op.drop_column('mock_interviews', 'interview_id')
