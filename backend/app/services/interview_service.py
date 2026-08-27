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

        if not candidate or candidate.user.role.value != "candidate":
            raise NotFoundError("Candidate not found. Please select a registered candidate from TalentForge.")

        data["candidate_id"] = candidate.id
        data.pop("candidate_email", None)

        # Resolve organization_id dynamically if not provided
        if not data.get("organization_id"):
            from app.models.org_member import OrgMember
            org_member = db.query(OrgMember).filter(OrgMember.user_id == requested_by_id).first()
            if org_member:
                data["organization_id"] = org_member.organization_id
            else:
                from app.models.organization import Organization
                first_org = db.query(Organization).first()
                if first_org:
                    data["organization_id"] = first_org.id
                else:
                    raise NotFoundError("No organization found for recruiter.")

        # Validate scheduled_at is in the future
        scheduled_at = data.get("scheduled_at")
        if scheduled_at:
            if isinstance(scheduled_at, str):
                from dateutil import parser
                try:
                    scheduled_dt = parser.isoparse(scheduled_at)
                except ValueError:
                    scheduled_dt = parser.parse(scheduled_at)
            else:
                scheduled_dt = scheduled_at

            if scheduled_dt.tzinfo is None:
                scheduled_dt = scheduled_dt.replace(tzinfo=timezone.utc)
            
            # Compare with current server time
            current_time = datetime.now(timezone.utc)
            if scheduled_dt <= current_time:
                from app.utils.errors import ValidationError
                raise ValidationError("Interview must be scheduled for a future date and time.")
            data["scheduled_at"] = scheduled_dt

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
        requested_by_id: Optional[str] = None,
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
        if requested_by_id:
            query = query.filter(Interview.requested_by_id == requested_by_id)
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
        from datetime import timedelta
        interview = db.query(Interview).get(interview_id)
        if not interview:
            raise NotFoundError("Interview not found.")

        data = InterviewResponse.model_validate(interview).model_dump()

        # Enforce 5-minute join window on backend
        if interview.scheduled_at:
            current_time = datetime.now(timezone.utc)
            scheduled_at_aware = interview.scheduled_at
            if scheduled_at_aware.tzinfo is None:
                scheduled_at_aware = scheduled_at_aware.replace(tzinfo=timezone.utc)

            join_allowed_from = scheduled_at_aware - timedelta(minutes=5)

            # If not within the window, or if not scheduled status, hide meeting_link
            if current_time < join_allowed_from or interview.status != InterviewStatus.scheduled:
                data["meeting_link"] = None
        else:
            data["meeting_link"] = None

        return data

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
        from app.utils.errors import ValidationError
        from datetime import timedelta

        # Select for update to prevent concurrent double-booking race conditions
        interview = db.query(Interview).filter(Interview.id == interview_id).with_for_update().first()
        if not interview:
            raise NotFoundError("Interview not found.")

        if interview.status not in (InterviewStatus.pending, InterviewStatus.scheduled):
            raise ConflictError(
                f"Cannot assign interviewer to an interview with status '{interview.status}'."
            )

        interviewer = db.query(Interviewer).get(interviewer_id)
        if not interviewer or not interviewer.is_approved:
            raise NotFoundError("Approved interviewer not found.")

        slot = db.query(AvailabilitySlot).filter(AvailabilitySlot.id == slot_id).with_for_update().first()
        if not slot or str(slot.interviewer_id) != str(interviewer.id):
            raise NotFoundError("Availability slot not found for this interviewer.")

        if slot.is_booked:
            raise ConflictError("This slot is already booked.")

        # Determine target interview time range
        interview_start = interview.scheduled_at if interview.scheduled_at else slot.start_time
        interview_end = interview_start + timedelta(minutes=interview.duration_mins)

        # Make sure timezone offsets match for comparison
        slot_start_aware = slot.start_time
        if slot_start_aware.tzinfo is None:
            slot_start_aware = slot_start_aware.replace(tzinfo=timezone.utc)
        slot_end_aware = slot.end_time
        if slot_end_aware.tzinfo is None:
            slot_end_aware = slot_end_aware.replace(tzinfo=timezone.utc)

        iv_start_aware = interview_start
        if iv_start_aware.tzinfo is None:
            iv_start_aware = iv_start_aware.replace(tzinfo=timezone.utc)
        iv_end_aware = interview_end
        if iv_end_aware.tzinfo is None:
            iv_end_aware = iv_end_aware.replace(tzinfo=timezone.utc)

        if not (slot_start_aware <= iv_start_aware and slot_end_aware >= iv_end_aware):
            raise ValidationError("This interviewer is not available for the full duration of this interview.")

        # Conflict check with other assigned interviews
        conflicting_interview = db.query(Interview).filter(
            Interview.interviewer_id == interviewer.id,
            Interview.id != interview.id,
            Interview.status.in_([InterviewStatus.scheduled, InterviewStatus.report_pending]),
        ).all()

        for conf in conflicting_interview:
            conf_start = conf.scheduled_at
            if conf_start.tzinfo is None:
                conf_start = conf_start.replace(tzinfo=timezone.utc)
            conf_end = conf_start + timedelta(minutes=conf.duration_mins)

            if iv_start_aware < conf_end and iv_end_aware > conf_start:
                raise ValidationError("This interviewer already has a conflicting interview during this time.")

        # Commit assignment atomically
        interview.interviewer_id = interviewer.id
        interview.scheduled_at = iv_start_aware
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

        if interview.status not in (InterviewStatus.scheduled, InterviewStatus.report_pending):
            raise ConflictError("Only scheduled or pending-report interviews can be completed.")

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

        if interview.status == InterviewStatus.scheduled:
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

    @staticmethod
    def delete_interview(db: Session, interview_id: str) -> None:
        interview = db.query(Interview).get(interview_id)
        if not interview:
            raise NotFoundError("Interview not found.")

        # Free the slot if one was booked
        db.query(AvailabilitySlot).filter(AvailabilitySlot.interview_id == interview.id).update(
            {AvailabilitySlot.interview_id: None, AvailabilitySlot.is_booked: False},
            synchronize_session=False
        )

        db.delete(interview)
        db.commit()