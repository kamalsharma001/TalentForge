"""Marshmallow schemas for MockInterview serialisation / validation."""

from marshmallow import Schema, fields, validate


class MockInterviewCreateSchema(Schema):
    """Input schema for POST /api/mock-interviews."""
    job_role      = fields.Str(allow_none=True)
    difficulty    = fields.Str(
        validate=validate.OneOf(["easy", "medium", "hard"]),
        load_default="medium",
    )
    category      = fields.Str(
        validate=validate.OneOf(["behavioral", "technical", "system_design"]),
        load_default="behavioral",
    )
    duration_mins = fields.Int(
        validate=validate.Range(min=10, max=120),
        load_default=30,
    )


class MockInterviewSubmitSchema(Schema):
    """Input schema for POST /api/mock-interviews/<id>/submit."""
    answer_text = fields.Str(required=True, validate=validate.Length(min=1))


class MockInterviewSchema(Schema):
    """Full serialiser for outbound mock interview responses."""
    id                   = fields.UUID(dump_only=True)
    candidate_id         = fields.UUID()
    practice_question_id = fields.UUID(allow_none=True)
    job_role             = fields.Str(allow_none=True)
    difficulty           = fields.Str()
    category             = fields.Str()
    question_text        = fields.Str()
    answer_text          = fields.Str(allow_none=True)
    duration_mins        = fields.Int()
    status               = fields.Str()
    ai_summary           = fields.Str(allow_none=True)
    ai_strengths         = fields.Str(allow_none=True)
    ai_weaknesses        = fields.Str(allow_none=True)
    ai_score             = fields.Int(allow_none=True)
    ai_generated_at      = fields.DateTime(allow_none=True)
    completed_at         = fields.DateTime(allow_none=True)
    created_at           = fields.DateTime(dump_only=True)
    updated_at           = fields.DateTime(dump_only=True)
