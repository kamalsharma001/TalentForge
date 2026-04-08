"""Marshmallow schemas for User serialisation / validation."""

from marshmallow import Schema, fields, validate, validates, ValidationError, pre_load
from app.utils.validators import validate_password_strength


class UserSchema(Schema):
    """Read-only serialiser — never exposes password_hash."""
    id          = fields.UUID(dump_only=True)
    email       = fields.Email(dump_only=True)
    role        = fields.Str(dump_only=True)
    first_name  = fields.Str(dump_only=True)
    last_name   = fields.Str(dump_only=True)
    full_name   = fields.Method("get_full_name", dump_only=True)
    avatar_url  = fields.Str(dump_only=True, allow_none=True)
    phone       = fields.Str(dump_only=True, allow_none=True)
    is_active   = fields.Bool(dump_only=True)
    is_verified = fields.Bool(dump_only=True)
    created_at  = fields.DateTime(dump_only=True)

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class UserRegistrationSchema(Schema):
    """Input schema for POST /api/auth/register."""
    email      = fields.Email(required=True)
    password   = fields.Str(required=True, load_only=True)
    role       = fields.Str(
        required=True,
        validate=validate.OneOf(["recruiter", "interviewer", "candidate"]),
    )
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    last_name  = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    phone      = fields.Str(load_only=True, allow_none=True)

    @pre_load
    def strip_whitespace(self, data, **kwargs):
        for key in ("email", "first_name", "last_name"):
            if key in data and isinstance(data[key], str):
                data[key] = data[key].strip()
        return data

    @validates("password")
    def validate_password(self, value):
        error = validate_password_strength(value)
        if error:
            raise ValidationError(error)


class UserLoginSchema(Schema):
    """Input schema for POST /api/auth/login."""
    email    = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)


class UserUpdateSchema(Schema):
    """Input schema for PATCH /api/users/me."""
    first_name = fields.Str(validate=validate.Length(min=1, max=100))
    last_name  = fields.Str(validate=validate.Length(min=1, max=100))
    phone      = fields.Str(allow_none=True)
    avatar_url = fields.Str(allow_none=True)
