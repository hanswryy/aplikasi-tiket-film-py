import uuid
from datetime import datetime

from extensions import db


class Showtime(db.Model):
    __tablename__ = "Showtime"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    movie_id = db.Column("movieId", db.String(36), db.ForeignKey("Movie.id", ondelete="CASCADE"), nullable=False)
    studio_id = db.Column("studioId", db.String(36), db.ForeignKey("Studio.id", ondelete="CASCADE"), nullable=False)
    price = db.Column(db.Float, nullable=False)
    start_time = db.Column("startTime", db.DateTime, nullable=False)
    end_time = db.Column("endTime", db.DateTime, nullable=False)
    created_at = db.Column("createdAt", db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column("updatedAt", db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    movie = db.relationship("Movie", back_populates="showtimes")
    studio = db.relationship("Studio", back_populates="showtimes")
    bookings = db.relationship("Booking", back_populates="showtime", cascade="all, delete-orphan")
    booked_seats = db.relationship("BookedSeat", back_populates="showtime", cascade="all, delete-orphan")

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "movieId": self.movie_id,
            "studioId": self.studio_id,
            "price": self.price,
            "startTime": self.start_time.isoformat(),
            "endTime": self.end_time.isoformat(),
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat(),
        }

    def to_detail_dict(self) -> dict[str, object]:
        data = self.to_dict()
        booked_seats = [
            {"id": seat.id, "row": seat.row, "number": seat.number, "createdAt": seat.created_at.isoformat()}
            for seat in self.booked_seats
        ]
        data.update(
            movie=self.movie.to_dict(),
            studio=self.studio.to_dict(),
            bookedSeats=booked_seats,
            totalSeats=self.studio.capacity,
            bookedSeatCount=len(booked_seats),
            availableSeats=max(self.studio.capacity - len(booked_seats), 0),
        )
        return data
