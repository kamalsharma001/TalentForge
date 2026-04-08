"""Marshmallow schemas for Interview serialisation / validation."""

from marshmallow import Schema, fields, validate, validates, ValidationError
from app.models.interview import InterviewStatus


class InterviewScoreSchema(Schema):
    id           = fields.UUID(dump_only=True)
    dimension    = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    score        = fields.Int(required=True, validate=validate.Range(min=1, max=10))
    max_score    = fields.Int(dump_default=10)
    notes        = fields.Str(allow_none=True)
    created_at   = fields.DateTime(dump_only=True)


class InterviewCreateSchema(Schema):
    """Input schema for POST /api/interviews."""

    title           = fields.Str(required=True, validate=validate.Length(min=2, max=200))
    job_role        = fields.Str(allow_none=True)

    candidate_id    = fields.UUID(required=False)
    candidate_email = fields.Email(required=False)

    organization_id = fields.UUID(required=True)

    tech_stack      = fields.List(fields.Str(), load_default=[])

    difficulty      = fields.Str(
        validate=validate.OneOf(["easy", "medium", "hard"]),
        load_default="medium",
    )

    duration_mins   = fields.Int(validate=validate.Range(min=15, max=240), load_default=60)

    instructions    = fields.Str(allow_none=True)

    scheduled_at    = fields.DateTime(allow_none=True)

    timezone        = fields.Str(load_default="UTC")


class InterviewUpdateSchema(Schema):
    """Input schema for PATCH /api/interviews/<id>."""
    title         = fields.Str(validate=validate.Length(min=2, max=200))
    job_role      = fields.Str(allow_none=True)
    tech_stack    = fields.List(fields.Str())
    difficulty    = fields.Str(validate=validate.OneOf(["easy", "medium", "hard"]))
    duration_mins = fields.Int(validate=validate.Range(min=15, max=240))
    instructions  = fields.Str(allow_none=True)
    scheduled_at  = fields.DateTime(allow_none=True)
    timezone      = fields.Str()
    meeting_link  = fields.Str(allow_none=True)
    status        = fields.Str(
        validate=validate.OneOf([s.value for s in InterviewStatus])
    )
    cancellation_reason = fields.Str(allow_none=True)


class InterviewSchema(Schema):
    """Full serialiser for outbound interview responses."""
    id               = fields.UUID(dump_only=True)
    title            = fields.Str()
    job_role         = fields.Str(allow_none=True)
    tech_stack       = fields.List(fields.Str())
    difficulty       = fields.Str()
    duration_mins    = fields.Int()
    instructions     = fields.Str(allow_none=True)
    scheduled_at     = fields.DateTime(allow_none=True)
    timezone         = fields.Str()
    meeting_link     = fields.Str(allow_none=True)
    status           = fields.Str()
    cancellation_reason = fields.Str(allow_none=True)
    recording_url    = fields.Str(allow_none=True)
    recording_duration_s = fields.Int(allow_none=True)
    completed_at     = fields.DateTime(allow_none=True)
    created_at       = fields.DateTime(dump_only=True)
    updated_at       = fields.DateTime(dump_only=True)

    # Nested relations (light)
    organization_id  = fields.UUID()
    candidate_id     = fields.UUID()
    interviewer_id   = fields.UUID(allow_none=True)
    requested_by_id  = fields.UUID(allow_none=True)

    scores           = fields.List(fields.Nested(InterviewScoreSchema), dump_only=True)


class InterviewAssignSchema(Schema):
    """Body for assigning an interviewer to an interview."""
    interviewer_id = fields.UUID(required=True)
    slot_id        = fields.UUID(required=True)


class InterviewCompleteSchema(Schema):
    """Body for marking an interview complete + uploading scores."""
    recording_url          = fields.Str(allow_none=True)
    recording_cloudinary_id = fields.Str(allow_none=True)
    recording_duration_s   = fields.Int(allow_none=True)
    scores = fields.List(fields.Nested(InterviewScoreSchema), load_default=[])
