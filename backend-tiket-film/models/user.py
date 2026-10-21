import enum
import uuid
from datetime import datetime

import bcrypt
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db


class Role(enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class User(db.Model):
    __tablename__ = "User"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(Role), nullable=False, default=Role.USER)
    created_at = db.Column("createdAt", db.DateTime, nullable=False, default=datetime.utcnow)

    bookings = db.relationship("Booking", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, value: str) -> None:
        self.password = bcrypt.hashpw(value.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, value: str) -> bool:
        if self.password.startswith(("$2a$", "$2b$", "$2y$")):
            try:
                return bcrypt.checkpw(value.encode("utf-8"), self.password.encode("utf-8"))
            except ValueError:
                return False
        return check_password_hash(self.password, value)

    def to_dict(self) -> dict[str, object]:
        return {"id": self.id, "email": self.email, "name": self.name, "role": self.role.value}
