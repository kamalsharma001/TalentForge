"""Marshmallow schemas for AvailabilitySlot."""

from marshmallow import Schema, fields, validates, ValidationError
from datetime import timezone


class AvailabilitySlotSchema(Schema):
    id             = fields.UUID(dump_only=True)
    interviewer_id = fields.UUID(dump_only=True)
    start_time     = fields.DateTime(required=True)
    end_time       = fields.DateTime(required=True)
    timezone       = fields.Str(load_default="UTC")
    is_booked      = fields.Bool(dump_only=True)
    interview_id   = fields.UUID(dump_only=True, allow_none=True)
    is_recurring   = fields.Bool(load_default=False)
    recurrence_rule = fields.Str(allow_none=True)
    created_at     = fields.DateTime(dump_only=True)

    @validates("end_time")
    def validate_end_after_start(self, value):
        # Full cross-field validation is done in the service layer
        pass


class SlotQuerySchema(Schema):
    """Query params for GET /api/scheduling/slots."""
    interviewer_id = fields.UUID(allow_none=True)
    from_date      = fields.Date(allow_none=True)
    to_date        = fields.Date(allow_none=True)
    available_only = fields.Bool(load_default=True)
    page           = fields.Int(load_default=1, validate=lambda n: n >= 1)
    per_page       = fields.Int(load_default=20, validate=lambda n: 1 <= n <= 100)
