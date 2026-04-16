"""Marshmallow schemas for PracticeQuestion serialisation / validation."""

from marshmallow import Schema, fields, validate


class PracticeQuestionCreateSchema(Schema):
    """Input schema for POST /api/practice (admin only)."""
    question      = fields.Str(required=True, validate=validate.Length(min=5))
    job_role      = fields.Str(required=True, validate=validate.Length(min=2, max=150))
    difficulty    = fields.Str(
        required=True,
        validate=validate.OneOf(["easy", "medium", "hard"]),
    )
    category      = fields.Str(
        required=True,
        validate=validate.OneOf(["behavioral", "technical", "system_design"]),
    )
    hint          = fields.Str(allow_none=True)
    sample_answer = fields.Str(allow_none=True)


class PracticeQuestionSchema(Schema):
    """Full serialiser for outbound practice question responses."""
    id            = fields.UUID(dump_only=True)
    question      = fields.Str()
    job_role      = fields.Str()
    difficulty    = fields.Str()
    category      = fields.Str()
    hint          = fields.Str(allow_none=True)
    sample_answer = fields.Str(allow_none=True)
    is_active     = fields.Bool()
    created_at    = fields.DateTime(dump_only=True)
    updated_at    = fields.DateTime(dump_only=True)
