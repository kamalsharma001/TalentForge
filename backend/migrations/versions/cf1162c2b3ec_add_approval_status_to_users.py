"""add approval_status to users

Revision ID: cf1162c2b3ec
Revises: a7b3e1f29d04
Create Date: 2026-08-18 16:04:08.982722

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cf1162c2b3ec'
down_revision = 'a7b3e1f29d04'
branch_labels = None
depends_on = None


def upgrade():
    # Add column with server default 'APPROVED' so all existing records get a value.
    op.add_column('users', sa.Column('approval_status', sa.String(length=50), nullable=False, server_default='APPROVED'))
    
    # 1. Update recruiters: set approval_status to 'PENDING' unless email is recruiter123@gmail.com
    op.execute(
        "UPDATE users SET approval_status = 'PENDING' WHERE role = 'recruiter' AND email != 'recruiter123@gmail.com'"
    )
    
    # 2. Update interviewers: set approval_status to 'PENDING' if they are not approved in interviewers table
    op.execute(
        "UPDATE users SET approval_status = 'PENDING' WHERE role = 'interviewer' AND id NOT IN (SELECT user_id FROM interviewers WHERE is_approved = true)"
    )


def downgrade():
    op.drop_column('users', 'approval_status')

