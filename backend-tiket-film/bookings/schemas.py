from marshmallow import fields, validate, validates_schema, ValidationError

from schemas.common import BaseSchema


class SeatItemSchema(BaseSchema):
    row = fields.String(required=True, validate=validate.Length(min=1, max=10))
    number = fields.Integer(required=True, validate=validate.Range(min=1))


class BookingCreateSchema(BaseSchema):
    showtime_id = fields.String(
        required=True,
        data_key="showtimeId",
        validate=validate.Length(min=1),
    )
    seats = fields.List(
        fields.Nested(SeatItemSchema),
        required=True,
        validate=validate.Length(min=1),
    )

    @validates_schema
    def validate_unique_seats(self, data: dict[str, object], **_: object) -> None:
        seats = data["seats"]
        seat_keys = {(seat["row"].upper(), seat["number"]) for seat in seats}
        if len(seat_keys) != len(seats):
            raise ValidationError({"seats": ["must not contain duplicate seats"]})
