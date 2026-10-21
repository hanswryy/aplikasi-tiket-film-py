import uuid
from datetime import datetime

from extensions import db


class Studio(db.Model):
    __tablename__ = "Studio"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    capacity = db.Column(db.Integer, nullable=False, default=100)
    total_rows = db.Column("totalRows", db.Integer, nullable=False, default=10)
    total_cols = db.Column("totalCols", db.Integer, nullable=False, default=10)
    created_at = db.Column("createdAt", db.DateTime, nullable=False, default=datetime.utcnow)

    showtimes = db.relationship("Showtime", back_populates="studio", cascade="all, delete-orphan")

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "name": self.name,
            "capacity": self.capacity,
            "totalRows": self.total_rows,
            "totalCols": self.total_cols,
            "createdAt": self.created_at.isoformat(),
        }

    def to_detail_dict(self) -> dict[str, object]:
        data = self.to_dict()
        data["showtimes"] = [
            {
                **showtime.to_dict(),
                "movie": showtime.movie.to_dict(),
            }
            for showtime in sorted(self.showtimes, key=lambda item: item.start_time)
        ]
        return data
