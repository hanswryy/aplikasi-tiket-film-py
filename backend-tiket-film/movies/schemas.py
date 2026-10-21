from marshmallow import fields, validate

from schemas.common import BaseSchema


class MovieCreateSchema(BaseSchema):
    title = fields.String(required=True, validate=validate.Length(min=1, max=255))
    description = fields.String(required=True, validate=validate.Length(min=1))
    poster_url = fields.String(required=True, data_key="posterUrl", validate=validate.Length(min=1, max=2048))
    duration_min = fields.Integer(required=True, data_key="durationMin", validate=validate.Range(min=1))


class MovieUpdateSchema(BaseSchema):
    title = fields.String(validate=validate.Length(min=1, max=255))
    description = fields.String(validate=validate.Length(min=1))
    poster_url = fields.String(data_key="posterUrl", validate=validate.Length(min=1, max=2048))
    duration_min = fields.Integer(data_key="durationMin", validate=validate.Range(min=1))


class MovieQuerySchema(BaseSchema):
    search = fields.String(load_default=None, allow_none=True, validate=validate.Length(max=255))
