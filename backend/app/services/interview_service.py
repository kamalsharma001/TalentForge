"""
InterviewService — all interview lifecycle business logic.
Fully native FastAPI and legacy SQLAlchemy ORM service.
"""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models.interview import Interview, InterviewStatus
from app.models.interview_score import InterviewScore
from app.models.interviewer import Interviewer
from app.models.candidate import Candidate
from app.models.availability_slot import AvailabilitySlot
from app.models.user import User
from app.schemas.interview_schema import InterviewResponse
from app.utils.errors import NotFoundError, ConflictError, ForbiddenError
from app.utils.pagination import paginate_query

class InterviewService:

    # ── Create ────────────────────────────────────────────────────────────
    @staticmethod
    def create(db: Session, data: dict, requested_by_id: str) -> dict:
        candidate = None

        # Case 1 — candidate_id provided
        if data.get("candidate_id"):
            candidate = db.query(Candidate).get(data["candidate_id"])

        # Case 2 — candidate_email provided
        elif data.get("candidate_email"):
            user = db.query(User).filter(User.email == data["candidate_email"]).first()
            if user:
                candidate = db.query(Candidate).filter(Candidate.user_id == user.id).first()

            # Create candidate if not found
            if not candidate:
                user = User(
                    email=data["candidate_email"],
                    role="candidate"
                )
                db.add(user)
                db.flush()

                candidate = Candidate(
                    user_id=user.id
                )
                db.add(candidate)
                db.flush()

        if not candidate:
            raise NotFoundError("Candidate not found.")

        data["candidate_id"] = candidate.id
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

        db.add(interview)
        db.commit()
        db.refresh(interview)

        return InterviewResponse.model_validate(interview).model_dump()

    # ── List ──────────────────────────────────────────────────────────────
    @staticmethod
    def list_interviews(
        db: Session,
        *,
        organization_id: Optional[str] = None,
        candidate_id: Optional[str] = None,
        interviewer_id: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        query = db.query(Interview)

        if organization_id:
            query = query.filter(Interview.organization_id == organization_id)
        if candidate_id:
            query = query.filter(Interview.candidate_id == candidate_id)
        if interviewer_id:
            query = query.filter(Interview.interviewer_id == interviewer_id)
        if status:
            query = query.filter(Interview.status == InterviewStatus(status))

        query = query.order_by(Interview.created_at.desc())

        res = paginate_query(query, page, per_page)
        # Serialize response items
        items_serialized = [InterviewResponse.model_validate(item).model_dump() for item in res["items"]]
        return {
            "items":    items_serialized,
            "total":    res["total"],
            "page":     res["page"],
            "pages":    res["pages"],
            "per_page": res["per_page"],
            "has_next": res["has_next"],
            "has_prev": res["has_prev"],
        }

    # ── Get one ───────────────────────────────────────────────────────────
    @staticmethod
    def get_by_id(db: Session, interview_id: str) -> dict:
        interview = db.query(Interview).get(interview_id)
        if not interview:
            raise NotFoundError("Interview not found.")
        return InterviewResponse.model_validate(interview).model_dump()

    # ── Update ────────────────────────────────────────────────────────────
    @staticmethod
    def update(db: Session, interview_id: str, data: dict, requesting_user_id: str) -> dict:
        interview = db.query(Interview).get(interview_id)
        if not interview:
            raise NotFoundError("Interview not found.")

        for field, value in data.items():
            setattr(interview, field, value)

        db.commit()
        db.refresh(interview)
        return InterviewResponse.model_validate(interview).model_dump()

    # ── Assign interviewer + slot ─────────────────────────────────────────
    @staticmethod
    def assign_interviewer(db: Session, interview_id: str, interviewer_id: str, slot_id: str) -> dict:
        interview = db.query(Interview).get(interview_id)
        if not interview:
            raise NotFoundError("Interview not found.")

        if interview.status not in (InterviewStatus.pending, InterviewStatus.scheduled):
            raise ConflictError(
                f"Cannot assign interviewer to an interview with status '{interview.status}'."
            )

        interviewer = db.query(Interviewer).get(interviewer_id)
        if not interviewer or not interviewer.is_approved:
            raise NotFoundError("Approved interviewer not found.")

        slot = db.query(AvailabilitySlot).get(slot_id)
        if not slot or str(slot.interviewer_id) != str(interviewer.id):
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

        db.commit()
        db.refresh(interview)
        return InterviewResponse.model_validate(interview).model_dump()

    # ── Complete interview + submit scores ────────────────────────────────
    @staticmethod
    def complete(db: Session, interview_id: str, data: dict, interviewer_user_id: str) -> dict:
        interview = db.query(Interview).get(interview_id)
        if not interview:
            raise NotFoundError("Interview not found.")

        if interview.status != InterviewStatus.scheduled:
            raise ConflictError("Only scheduled interviews can be completed.")

        interviewer = db.query(Interviewer).filter(Interviewer.user_id == interviewer_user_id).first()
        if not interviewer or str(interview.interviewer_id) != str(interviewer.id):
            raise ForbiddenError("You are not the assigned interviewer for this interview.")

        # Persist scores
        for score_data in data.get("scores", []):
            existing = db.query(InterviewScore).filter(
                InterviewScore.interview_id == interview.id,
                InterviewScore.dimension == score_data["dimension"],
            ).first()

            if existing:
                existing.score = score_data["score"]
                existing.notes = score_data.get("notes")
            else:
                db.add(
                    InterviewScore(
                        interview_id=interview.id,
                        interviewer_id=interviewer.id,
                        dimension=score_data["dimension"],
                        score=score_data["score"],
                        max_score=score_data.get("max_score", 10),
                        notes=score_data.get("notes"),
                    )
                )

        if data.get("recording_url"):
            interview.recording_url = data["recording_url"]
            interview.recording_cloudinary_id = data.get("recording_cloudinary_id")
            interview.recording_duration_s = data.get("recording_duration_s")

        interview.status = InterviewStatus.report_pending
        interview.completed_at = datetime.now(timezone.utc)
        interviewer.total_interviews += 1

        db.commit()
        db.refresh(interview)
        return InterviewResponse.model_validate(interview).model_dump()

    # ── Cancel ────────────────────────────────────────────────────────────
    @staticmethod
    def cancel(db: Session, interview_id: str, reason: Optional[str], requesting_user_id: str) -> dict:
        interview = db.query(Interview).get(interview_id)
        if not interview:
            raise NotFoundError("Interview not found.")

        if interview.status == InterviewStatus.completed:
            raise ConflictError("Completed interviews cannot be cancelled.")

        # Free the slot if one was booked
        if interview.interviewer_id:
            slot = db.query(AvailabilitySlot).filter(AvailabilitySlot.interview_id == interview.id).first()
            if slot:
                slot.is_booked = False
                slot.interview_id = None

        interview.status = InterviewStatus.cancelled
        interview.cancellation_reason = reason

        db.commit()
        db.refresh(interview)
        return InterviewResponse.model_validate(interview).model_dump()