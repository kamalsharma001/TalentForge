"""Marshmallow schemas for InterviewReport."""

from marshmallow import Schema, fields, validate


class InterviewReportSchema(Schema):
    """Full serialiser."""
    id               = fields.UUID(dump_only=True)
    interview_id     = fields.UUID(dump_only=True)
    summary          = fields.Str(allow_none=True)
    strengths        = fields.Str(allow_none=True)
    weaknesses       = fields.Str(allow_none=True)
    recommendation   = fields.Str(allow_none=True)
    private_notes    = fields.Str(allow_none=True)   # stripped for candidate
    ai_summary       = fields.Str(dump_only=True, allow_none=True)
    ai_strengths     = fields.Str(dump_only=True, allow_none=True)
    ai_weaknesses    = fields.Str(dump_only=True, allow_none=True)
    ai_generated_at  = fields.DateTime(dump_only=True, allow_none=True)
    decision         = fields.Str(allow_none=True)
    overall_score    = fields.Decimal(as_string=True, allow_none=True)
    is_published     = fields.Bool(dump_only=True)
    published_at     = fields.DateTime(dump_only=True, allow_none=True)
    created_at       = fields.DateTime(dump_only=True)
    updated_at       = fields.DateTime(dump_only=True)


class ReportCreateSchema(Schema):
    """Input for POST /api/reports (interviewer submits report)."""
    summary        = fields.Str(allow_none=True)
    strengths      = fields.Str(allow_none=True)
    weaknesses     = fields.Str(allow_none=True)
    recommendation = fields.Str(allow_none=True)
    private_notes  = fields.Str(allow_none=True)
    decision       = fields.Str(
        validate=validate.OneOf(["hire", "hold", "no_hire"]),
        allow_none=True,
    )


class ReportUpdateSchema(ReportCreateSchema):
    """PATCH — same fields, all optional."""
    pass


class CandidateReportSchema(Schema):
    """Stripped view shown to the candidate — no private_notes."""
    id             = fields.UUID(dump_only=True)
    interview_id   = fields.UUID(dump_only=True)
    summary        = fields.Str(allow_none=True)
    strengths      = fields.Str(allow_none=True)
    weaknesses     = fields.Str(allow_none=True)
    recommendation = fields.Str(allow_none=True)
    ai_summary     = fields.Str(allow_none=True)
    decision       = fields.Str(allow_none=True)
    overall_score  = fields.Decimal(as_string=True, allow_none=True)
    published_at   = fields.DateTime(allow_none=True)
