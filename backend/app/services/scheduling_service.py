"""
SchedulingService — availability slot management and interviewer matching.
Fully native FastAPI and legacy SQLAlchemy ORM service.
"""

from datetime import datetime, timezone, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.availability_slot import AvailabilitySlot
from app.models.interviewer import Interviewer
from app.schemas.availability_schema import AvailabilitySlotResponse
from app.utils.errors import NotFoundError, ConflictError, ForbiddenError, ValidationError
from app.utils.pagination import paginate_query

class SchedulingService:

    # ── Add slot ──────────────────────────────────────────────────────────
    @staticmethod
    def add_slot(db: Session, data: dict, interviewer_user_id: str) -> dict:
        interviewer = db.query(Interviewer).filter(
            Interviewer.user_id == interviewer_user_id
        ).first()
        if not interviewer:
            raise NotFoundError("Interviewer profile not found.")

        start = data["start_time"]
        end   = data["end_time"]

        if end <= start:
            raise ValidationError("end_time must be after start_time.")

        duration = (end - start).total_seconds() / 60
        if duration < 15:
            raise ValidationError("Slot must be at least 15 minutes long.")

        # Overlap check
        overlap = db.query(AvailabilitySlot).filter(
            AvailabilitySlot.interviewer_id == interviewer.id,
            AvailabilitySlot.is_booked == False,
            AvailabilitySlot.start_time < end,
            AvailabilitySlot.end_time > start,
        ).first()
        if overlap:
            raise ConflictError("This slot overlaps with an existing availability window.")

        slot = AvailabilitySlot(
            interviewer_id=interviewer.id,
            start_time=start,
            end_time=end,
            timezone=data.get("timezone", "UTC"),
            is_recurring=data.get("is_recurring", False),
            recurrence_rule=data.get("recurrence_rule"),
        )
        db.add(slot)
        db.commit()
        db.refresh(slot)
        return AvailabilitySlotResponse.model_validate(slot).model_dump()

    # ── Delete slot ───────────────────────────────────────────────────────
    @staticmethod
    def delete_slot(db: Session, slot_id: str, interviewer_user_id: str) -> None:
        interviewer = db.query(Interviewer).filter(
            Interviewer.user_id == interviewer_user_id
        ).first()
        if not interviewer:
            raise NotFoundError("Interviewer profile not found.")

        slot = db.query(AvailabilitySlot).get(slot_id)
        if not slot:
            raise NotFoundError("Slot not found.")
        if str(slot.interviewer_id) != str(interviewer.id):
            raise ForbiddenError("You can only delete your own slots.")
        if slot.is_booked:
            raise ConflictError("Cannot delete a booked slot.")

        db.delete(slot)
        db.commit()

    # ── List slots ────────────────────────────────────────────────────────
    @staticmethod
    def list_slots(
        db: Session,
        *,
        interviewer_id: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        available_only: bool = True,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        query = db.query(AvailabilitySlot)

        if interviewer_id:
            query = query.filter(AvailabilitySlot.interviewer_id == interviewer_id)
        if available_only:
            query = query.filter(AvailabilitySlot.is_booked == False)
        if from_date:
            query = query.filter(AvailabilitySlot.start_time >= from_date)
        if to_date:
            query = query.filter(AvailabilitySlot.end_time <= to_date)

        query = query.order_by(AvailabilitySlot.start_time.asc())

        res = paginate_query(query, page, per_page)
        # Serialize response items
        items_serialized = [AvailabilitySlotResponse.model_validate(item).model_dump() for item in res["items"]]
        return {
            "items":    items_serialized,
            "total":    res["total"],
            "page":     res["page"],
            "pages":    res["pages"],
            "per_page": res["per_page"],
            "has_next": res["has_next"],
            "has_prev": res["has_prev"],
        }

    # ── Find matching interviewers ────────────────────────────────────────
    @staticmethod
    def find_available_interviewers(
        db: Session,
        *,
        tech_stack: list,
        requested_at: datetime,
        duration_mins: int = 60,
    ) -> list:
        """
        Return approved interviewers who have a free slot covering
        [requested_at, requested_at + duration_mins].
        """
        end_time = requested_at + timedelta(minutes=duration_mins)

        # Find interviewers with a qualifying slot
        slots = db.query(AvailabilitySlot).filter(
            AvailabilitySlot.is_booked == False,
            AvailabilitySlot.start_time <= requested_at,
            AvailabilitySlot.end_time >= end_time,
        ).all()

        interviewer_ids = {slot.interviewer_id for slot in slots}
        if not interviewer_ids:
            return []

        query = db.query(Interviewer).filter(
            Interviewer.id.in_(interviewer_ids),
            Interviewer.is_approved == True,
            Interviewer.is_available == True,
        )

        # Filter by tech stack if provided (PostgreSQL array overlap)
        if tech_stack:
            query = query.filter(Interviewer.tech_stack.overlap(tech_stack))

        interviewers = query.all()

        # Attach the matching slot for each interviewer
        slot_map = {slot.interviewer_id: slot for slot in slots}
        result = []
        for iv in interviewers:
            matching_slot = slot_map.get(iv.id)
            result.append({
                "interviewer_id": str(iv.id),
                "user_id":        str(iv.user_id),
                "domains":        iv.domains,
                "tech_stack":     iv.tech_stack,
                "avg_rating":     float(iv.avg_rating) if iv.avg_rating else None,
                "total_interviews": iv.total_interviews,
                "slot_id":        str(matching_slot.id) if matching_slot else None,
                "slot_start":     matching_slot.start_time.isoformat() if matching_slot else None,
                "slot_end":       matching_slot.end_time.isoformat() if matching_slot else None,
            })

        return result
