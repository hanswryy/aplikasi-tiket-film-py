import uuid
from datetime import datetime

from extensions import db


class Movie(db.Model):
    __tablename__ = "Movie"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    poster_url = db.Column("posterUrl", db.String(2048), nullable=False)
    duration_min = db.Column("durationMin", db.Integer, nullable=False)
    created_at = db.Column("createdAt", db.DateTime, nullable=False, default=datetime.utcnow)

    showtimes = db.relationship("Showtime", back_populates="movie", cascade="all, delete-orphan")

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "posterUrl": self.poster_url,
            "durationMin": self.duration_min,
            "createdAt": self.created_at.isoformat(),
        }

    def to_detail_dict(self) -> dict[str, object]:
        data = self.to_dict()
        data["showtimes"] = [
            {
                **showtime.to_dict(),
                "studio": showtime.studio.to_dict(),
            }
            for showtime in self.showtimes
        ]
        return data
