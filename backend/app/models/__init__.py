# models package — re-export everything so Alembic detects all tables
from app.models.user import User, UserRole
from app.models.organization import Organization
from app.models.org_member import OrgMember, OrgRole
from app.models.candidate import Candidate
from app.models.resume import Resume
from app.models.interviewer import Interviewer
from app.models.interview import Interview, InterviewStatus
from app.models.interview_score import InterviewScore
from app.models.interview_report import InterviewReport, ReportDecision
from app.models.availability_slot import AvailabilitySlot
from app.models.notification import Notification

__all__ = [
    "User", "UserRole",
    "Organization",
    "OrgMember", "OrgRole",
    "Candidate",
    "Resume",
    "Interviewer",
    "Interview", "InterviewStatus",
    "InterviewScore",
    "InterviewReport", "ReportDecision",
    "AvailabilitySlot",
    "Notification",
]
