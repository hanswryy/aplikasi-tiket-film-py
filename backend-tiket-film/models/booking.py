import enum
import uuid
from datetime import datetime

from extensions import db


class BookingStatus(enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"


class Booking(db.Model):
    __tablename__ = "Booking"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column("userId", db.String(36), db.ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    showtime_id = db.Column("showtimeId", db.String(36), db.ForeignKey("Showtime.id", ondelete="CASCADE"), nullable=False)
    total_amount = db.Column("totalAmount", db.Float, nullable=False)
    status = db.Column(db.Enum(BookingStatus), nullable=False, default=BookingStatus.PENDING)
    created_at = db.Column("createdAt", db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column("updatedAt", db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", back_populates="bookings")
    showtime = db.relationship("Showtime", back_populates="bookings")
    booked_seats = db.relationship("BookedSeat", back_populates="booking", cascade="all, delete-orphan")

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "userId": self.user_id,
            "showtimeId": self.showtime_id,
            "totalAmount": self.total_amount,
            "status": self.status.value,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
            "showtime": {
                **self.showtime.to_dict(),
                "movie": self.showtime.movie.to_dict(),
                "studio": self.showtime.studio.to_dict(),
            },
            "bookedSeats": [
                {"row": seat.row, "number": seat.number}
                for seat in self.booked_seats
            ],
        }


class BookedSeat(db.Model):
    __tablename__ = "BookedSeat"
    __table_args__ = (db.UniqueConstraint("showtimeId", "row", "number"),)

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    showtime_id = db.Column("showtimeId", db.String(36), db.ForeignKey("Showtime.id", ondelete="CASCADE"), nullable=False)
    booking_id = db.Column("bookingId", db.String(36), db.ForeignKey("Booking.id", ondelete="CASCADE"), nullable=False)
    row = db.Column(db.String(10), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    created_at = db.Column("createdAt", db.DateTime, nullable=False, default=datetime.utcnow)

    showtime = db.relationship("Showtime", back_populates="booked_seats")
    booking = db.relationship("Booking", back_populates="booked_seats")
