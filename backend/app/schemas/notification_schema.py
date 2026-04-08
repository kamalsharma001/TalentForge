"""Marshmallow schemas for Notification."""

from marshmallow import Schema, fields


class NotificationSchema(Schema):
    id           = fields.UUID(dump_only=True)
    user_id      = fields.UUID(dump_only=True)
    title        = fields.Str()
    body         = fields.Str()
    type         = fields.Str(allow_none=True)
    action_url   = fields.Str(allow_none=True)
    interview_id = fields.UUID(allow_none=True)
    is_read      = fields.Bool()
    read_at      = fields.DateTime(allow_none=True)
    sent_email   = fields.Bool(dump_only=True)
    created_at   = fields.DateTime(dump_only=True)
