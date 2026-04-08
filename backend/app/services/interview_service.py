"""
InterviewService — all interview lifecycle business logic.
"""

from datetime import datetime, timezone
from typing import Optional

from app import db
from app.models.interview import Interview, InterviewStatus
from app.models.interview_score import InterviewScore
from app.models.interviewer import Interviewer
from app.models.candidate import Candidate
from app.models.availability_slot import AvailabilitySlot
from app.models.user import User
from app.schemas.interview_schema import InterviewSchema
from app.utils.errors import NotFoundError, ConflictError, ForbiddenError
from app.utils.pagination import paginate_query

_schema = InterviewSchema()
_schema_list = InterviewSchema(many=True)


class InterviewService:

    # ── Create ────────────────────────────────────────────────────────────
    @staticmethod
    def create(data: dict, requested_by_id: str) -> dict:

        candidate = None

        # Case 1 — candidate_id provided
        if data.get("candidate_id"):
            candidate = Candidate.query.get(data["candidate_id"])

        # Case 2 — candidate_email provided
        elif data.get("candidate_email"):

            user = User.query.filter_by(email=data["candidate_email"]).first()

            if user:
                candidate = Candidate.query.filter_by(user_id=user.id).first()

            # Create candidate if not found
            if not candidate:

                user = User(
                    email=data["candidate_email"],
                    role="candidate"
                )
                db.session.add(user)
                db.session.flush()

                candidate = Candidate(
                    user_id=user.id
                )
                db.session.add(candidate)
                db.session.flush()

        if not candidate:
            raise NotFoundError("Candidate not found.")

        data["candidate_id"] = candidate.id

        # Remove candidate_email before creating interview
        data.pop("candidate_email", None)

        interview = Interview(
            title=data["title"],
            job_role=data.get("job_role"),
            organization_id=data["organization_id"],
            candidate_id=data["candidate_id"],
            requested_by_id=requested_by_id,
            tech_stack=data.get("tech_stack", []),
            difficulty=data.get("difficulty", "medium"),
            duration_mins=data.get("duration_mins", 60),
            instructions=data.get("instructions"),
            scheduled_at=data.get("scheduled_at"),
            timezone=data.get("timezone", "UTC"),
            status=InterviewStatus.pending,
        )

        db.session.add(interview)
        db.session.commit()

        return _schema.dump(interview)

    # ── List ──────────────────────────────────────────────────────────────
    @staticmethod
    def list_interviews(
        *,
        organization_id: Optional[str] = None,
        candidate_id: Optional[str] = None,
        interviewer_id: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:

        q = Interview.query

        if organization_id:
            q = q.filter_by(organization_id=organization_id)

        if candidate_id:
            q = q.filter_by(candidate_id=candidate_id)

        if interviewer_id:
            q = q.filter_by(interviewer_id=interviewer_id)

        if status:
            q = q.filter_by(status=InterviewStatus(status))

        q = q.order_by(Interview.created_at.desc())

        return paginate_query(q, page, per_page, _schema)

    # ── Get one ───────────────────────────────────────────────────────────
    @staticmethod
    def get_by_id(interview_id: str) -> dict:

        interview = Interview.query.get(interview_id)

        if not interview:
            raise NotFoundError("Interview not found.")

        return _schema.dump(interview)

    # ── Update ────────────────────────────────────────────────────────────
    @staticmethod
    def update(interview_id: str, data: dict, requesting_user_id: str) -> dict:

        interview = Interview.query.get(interview_id)

        if not interview:
            raise NotFoundError("Interview not found.")

        for field, value in data.items():
            setattr(interview, field, value)

        db.session.commit()

        return _schema.dump(interview)

    # ── Assign interviewer + slot ─────────────────────────────────────────
    @staticmethod
    def assign_interviewer(interview_id: str, interviewer_id: str, slot_id: str) -> dict:

        interview = Interview.query.get(interview_id)

        if not interview:
            raise NotFoundError("Interview not found.")

        if interview.status not in (InterviewStatus.pending, InterviewStatus.scheduled):
            raise ConflictError(
                f"Cannot assign interviewer to an interview with status '{interview.status}'."
            )

        interviewer = Interviewer.query.get(interviewer_id)

        if not interviewer or not interviewer.is_approved:
            raise NotFoundError("Approved interviewer not found.")

        slot = AvailabilitySlot.query.get(slot_id)

        if not slot or slot.interviewer_id != interviewer.id:
            raise NotFoundError("Availability slot not found for this interviewer.")

        if slot.is_booked:
            raise ConflictError("This slot is already booked.")

        # Commit assignment atomically
        interview.interviewer_id = interviewer.id
        interview.scheduled_at = slot.start_time
        
        interview.status = InterviewStatus.scheduled
        interview.meeting_link = f"https://meet.jit.si/talentforge-{str(interview.id)[:8]}"

        slot.is_booked = True
        slot.interview_id = interview.id

        db.session.commit()

        return _schema.dump(interview)

    # ── Complete interview + submit scores ────────────────────────────────
    @staticmethod
    def complete(interview_id: str, data: dict, interviewer_user_id: str) -> dict:

        interview = Interview.query.get(interview_id)

        if not interview:
            raise NotFoundError("Interview not found.")

        if interview.status != InterviewStatus.scheduled:
            raise ConflictError("Only scheduled interviews can be completed.")

        interviewer = Interviewer.query.filter_by(user_id=interviewer_user_id).first()

        if not interviewer or str(interview.interviewer_id) != str(interviewer.id):
            raise ForbiddenError("You are not the assigned interviewer for this interview.")

        # Persist scores
        for score_data in data.get("scores", []):

            existing = InterviewScore.query.filter_by(
                interview_id=interview.id,
                dimension=score_data["dimension"],
            ).first()

            if existing:
                existing.score = score_data["score"]
                existing.notes = score_data.get("notes")

            else:
                db.session.add(
                    InterviewScore(
                        interview_id=interview.id,
                        interviewer_id=interviewer.id,
                        dimension=score_data["dimension"],
                        score=score_data["score"],
                        max_score=score_data.get("max_score", 10),
                        notes=score_data.get("notes"),
                    )
                )

        # Update recording info if provided
        if data.get("recording_url"):
            interview.recording_url = data["recording_url"]
            interview.recording_cloudinary_id = data.get("recording_cloudinary_id")
            interview.recording_duration_s = data.get("recording_duration_s")

        interview.status = InterviewStatus.report_pending
        interview.completed_at = datetime.now(timezone.utc)

        # Update interviewer stats
        interviewer.total_interviews += 1

        db.session.commit()

        return _schema.dump(interview)

    # ── Cancel ────────────────────────────────────────────────────────────
    @staticmethod
    def cancel(interview_id: str, reason: Optional[str], requesting_user_id: str) -> dict:

        interview = Interview.query.get(interview_id)

        if not interview:
            raise NotFoundError("Interview not found.")

        if interview.status == InterviewStatus.completed:
            raise ConflictError("Completed interviews cannot be cancelled.")

        # Free the slot if one was booked
        if interview.interviewer_id:

            slot = AvailabilitySlot.query.filter_by(
                interview_id=interview.id
            ).first()

            if slot:
                slot.is_booked = False
                slot.interview_id = None

        interview.status = InterviewStatus.cancelled
        interview.cancellation_reason = reason

        db.session.commit()

        return _schema.dump(interview)