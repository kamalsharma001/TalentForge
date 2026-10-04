"""add resume analysis and mock coverage fields

Revision ID: 8f2a1b9c3d4e
Revises: e5c89201f9ab
Create Date: 2026-09-22 11:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8f2a1b9c3d4e'
down_revision = 'e5c89201f9ab'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Add extracted_text and parsed_data to resumes
    op.add_column('resumes', sa.Column('extracted_text', sa.Text(), nullable=True))
    op.add_column('resumes', sa.Column('parsed_data', sa.Text(), nullable=True))

    # 2. Add resume tracking & coverage columns to mock_interviews
    op.add_column('mock_interviews', sa.Column('resume_id', sa.UUID(), nullable=True))
    op.add_column('mock_interviews', sa.Column('resume_snapshot', sa.Text(), nullable=True))
    op.add_column('mock_interviews', sa.Column('competency_coverage', sa.Text(), nullable=True))
    op.add_column('mock_interviews', sa.Column('validated_claims', sa.Text(), nullable=True))

    op.create_foreign_key(
        'fk_mock_interviews_resume_id',
        'mock_interviews',
        'resumes',
        ['resume_id'],
        ['id'],
        ondelete='SET NULL'
    )
    op.create_index(
        op.f('ix_mock_interviews_resume_id'),
        'mock_interviews',
        ['resume_id'],
        unique=False
    )


def downgrade():
    op.drop_index(op.f('ix_mock_interviews_resume_id'), table_name='mock_interviews')
    op.drop_constraint('fk_mock_interviews_resume_id', 'mock_interviews', type_='foreignkey')
    op.drop_column('mock_interviews', 'validated_claims')
    op.drop_column('mock_interviews', 'competency_coverage')
    op.drop_column('mock_interviews', 'resume_snapshot')
    op.drop_column('mock_interviews', 'resume_id')

    op.drop_column('resumes', 'parsed_data')
    op.drop_column('resumes', 'extracted_text')
