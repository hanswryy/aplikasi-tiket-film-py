from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from auth.schemas import LoginSchema, RegisterSchema
from auth.service import login_user, register_user

auth_bp = Blueprint("auth", __name__)
register_schema = RegisterSchema()
login_schema = LoginSchema()


@auth_bp.post("/register")
def register():
    try:
        payload = register_schema.load(request.get_json(silent=True) or {})
        return jsonify(register_user(**payload)), 201
    except ValidationError as error:
        return jsonify(error=error.messages), 400
    except ValueError as error:
        return jsonify(error=str(error)), 409


@auth_bp.post("/login")
def login():
    try:
        payload = login_schema.load(request.get_json(silent=True) or {})
        return jsonify(login_user(**payload))
    except ValidationError as error:
        return jsonify(error=error.messages), 400
    except PermissionError as error:
        return jsonify(error=str(error)), 401
