from marshmallow import fields, validate

from schemas.common import BaseSchema


class StudioCreateSchema(BaseSchema):
    name = fields.String(required=True, validate=validate.Length(min=1, max=255))
    capacity = fields.Integer(load_default=100, validate=validate.Range(min=1))
    total_rows = fields.Integer(required=True, data_key="totalRows", validate=validate.Range(min=1))
    total_cols = fields.Integer(required=True, data_key="totalCols", validate=validate.Range(min=1))


class StudioUpdateSchema(BaseSchema):
    name = fields.String(validate=validate.Length(min=1, max=255))
    capacity = fields.Integer(validate=validate.Range(min=1))
    total_rows = fields.Integer(data_key="totalRows", validate=validate.Range(min=1))
    total_cols = fields.Integer(data_key="totalCols", validate=validate.Range(min=1))
