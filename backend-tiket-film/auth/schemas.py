from marshmallow import fields, validate

from schemas.common import BaseSchema


class RegisterSchema(BaseSchema):
    email = fields.Email(required=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=255))
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=6, max=255))


class LoginSchema(BaseSchema):
    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=1, max=255))
