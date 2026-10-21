from marshmallow import fields, validate, validates_schema, ValidationError

from schemas.common import BaseSchema


class ShowtimeCreateSchema(BaseSchema):
    movie_id = fields.UUID(required=True, data_key="movieId")
    studio_id = fields.UUID(required=True, data_key="studioId")
    price = fields.Float(required=True, validate=validate.Range(min=0))
    start_time = fields.DateTime(required=True, data_key="startTime")
    end_time = fields.DateTime(required=True, data_key="endTime")

    @validates_schema
    def validate_time_range(self, data: dict[str, object], **_: object) -> None:
        if data["end_time"] <= data["start_time"]:
            raise ValidationError({"endTime": ["must be after startTime"]})


class ShowtimeUpdateSchema(BaseSchema):
    movie_id = fields.UUID(data_key="movieId")
    studio_id = fields.UUID(data_key="studioId")
    price = fields.Float(validate=validate.Range(min=0))
    start_time = fields.DateTime(data_key="startTime")
    end_time = fields.DateTime(data_key="endTime")

    @validates_schema
    def validate_time_range(self, data: dict[str, object], **_: object) -> None:
        if "start_time" in data and "end_time" in data and data["end_time"] <= data["start_time"]:
            raise ValidationError({"endTime": ["must be after startTime"]})
