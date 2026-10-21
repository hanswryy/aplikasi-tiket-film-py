from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import User


def register_user(email: str, name: str, password: str) -> dict[str, object]:
    normalized_email = email.strip().lower()
    if User.query.filter_by(email=normalized_email).first() is not None:
        raise ValueError("Email already exists")

    user = User(email=normalized_email, name=name.strip())
    user.set_password(password)
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError as error:
        db.session.rollback()
        raise ValueError("Email already exists") from error
    return _authentication_response(user, "User registered successfully")


def login_user(email: str, password: str) -> dict[str, object]:
    user = User.query.filter_by(email=email.strip().lower()).first()
    if user is None or not user.check_password(password):
        raise PermissionError("Invalid credentials")
    return _authentication_response(user, "Login successful")


def _authentication_response(user: User, message: str) -> dict[str, object]:
    return {
        "message": message,
        "accesstoken": create_access_token(
            identity=user.id,
            additional_claims={"email": user.email, "role": user.role.value},
        ),
        "user": user.to_dict(),
    }
