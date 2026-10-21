from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from auth.guards import user_required
from extensions import db
from models import Booking, BookingStatus, BookedSeat, Showtime
from bookings.schemas import BookingCreateSchema
from bookings.payment import (
    PaymentConfigurationError,
    PaymentGatewayError,
    create_transaction,
    verify_notification,
)

bookings_bp = Blueprint("bookings", __name__)
create_schema = BookingCreateSchema()


@bookings_bp.post("")
@user_required
def create():
    try:
        payload = create_schema.load(request.get_json(silent=True) or {})
    except ValidationError as error:
        return jsonify(error=error.messages), 400

    showtime_id = str(payload["showtime_id"])
    user_id = str(get_jwt_identity())
    seats = payload["seats"]

    try:
        # PostgreSQL locks the selected showtime until this transaction ends.
        showtime = (
            Showtime.query.with_for_update()
            .filter_by(id=showtime_id)
            .first()
        )
        if showtime is None:
            return jsonify(error="Showtime not found"), 404

        normalized_seats = []
        for seat in seats:
            row = seat["row"].upper()
            number = seat["number"]
            if len(row) != 1 or ord(row) - ord("A") >= showtime.studio.total_rows:
                return jsonify(error=f"Seat {row}{number} has an invalid row"), 400
            if number > showtime.studio.total_cols:
                return jsonify(
                    error=(
                        f"Seat {row}{number} exceeds studio limit "
                        f"({showtime.studio.total_cols})"
                    )
                ), 400
            normalized_seats.append((row, number))

        total_amount = showtime.price * len(normalized_seats)
        booking = Booking(
            user_id=user_id,
            showtime_id=showtime_id,
            total_amount=total_amount,
            status=BookingStatus.PENDING,
        )
        db.session.add(booking)
        db.session.flush()

        for row, number in normalized_seats:
            db.session.add(
                BookedSeat(
                    showtime_id=showtime_id,
                    booking_id=booking.id,
                    row=row,
                    number=number,
                )
            )
        db.session.commit()
    except IntegrityError as error:
        db.session.rollback()
        if "BookedSeat" in str(error.orig) or "bookedseat" in str(error.orig).lower():
            return jsonify(error="One or more selected seats were just taken by another user!"), 409
        raise

    return jsonify(
        {
            "message": "Booking created successfully. Proceed to payment.",
            "bookingId": booking.id,
            "totalAmount": total_amount,
            "seats": [f"{row}{number}" for row, number in normalized_seats],
        }
    ), 201


@bookings_bp.get("/my-bookings")
@user_required
def find_my_bookings():
    user_id = str(get_jwt_identity())
    bookings = (
        Booking.query.filter_by(user_id=user_id)
        .order_by(Booking.created_at.desc())
        .all()
    )
    return jsonify([booking.to_dict() for booking in bookings])


@bookings_bp.post("/<string:booking_id>/pay")
@user_required
def pay(booking_id: str):
    user_id = str(get_jwt_identity())
    booking = Booking.query.filter_by(id=booking_id, user_id=user_id).first()
    if booking is None:
        return jsonify(error="Booking transaction not found"), 404
    if booking.status != BookingStatus.PENDING:
        return jsonify(error="Booking is not pending payment"), 400
    try:
        transaction = create_transaction(booking)
    except PaymentConfigurationError as error:
        return jsonify(error=str(error)), 503
    except PaymentGatewayError as error:
        return jsonify(error=str(error)), 502
    return jsonify(
        {
            "success": True,
            "bookingId": booking.id,
            "token": transaction["token"],
            "redirectUrl": transaction["redirect_url"],
        }
    )


@bookings_bp.post("/midtrans/notification")
def midtrans_notification():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="Notification payload must be a JSON object"), 400
    try:
        notification = verify_notification(payload)
    except PaymentConfigurationError as error:
        return jsonify(error=str(error)), 503
    except PaymentGatewayError as error:
        return jsonify(error=str(error)), 400

    booking = Booking.query.filter_by(id=str(notification["order_id"])).first()
    if booking is None:
        return jsonify(error="Booking transaction not found"), 404
    try:
        if float(notification["gross_amount"]) != booking.total_amount:
            return jsonify(error="Payment amount does not match booking"), 400
    except (TypeError, ValueError):
        return jsonify(error="Payment amount does not match booking"), 400

    if booking.status == BookingStatus.PAID:
        return jsonify(received=True, status=booking.status.value)

    status_map = {
        "settlement": BookingStatus.PAID,
        "capture": BookingStatus.PAID,
        "expire": BookingStatus.EXPIRED,
        "cancel": BookingStatus.CANCELLED,
        "deny": BookingStatus.CANCELLED,
        "failure": BookingStatus.CANCELLED,
    }
    next_status = status_map.get(str(notification["transaction_status"]))
    if next_status and next_status != booking.status:
        booking.status = next_status
        db.session.commit()
    return jsonify(received=True, status=(next_status or booking.status).value)
