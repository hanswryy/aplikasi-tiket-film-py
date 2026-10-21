from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from auth.guards import admin_required
from extensions import db
from models import Studio
from studios.schemas import StudioCreateSchema, StudioUpdateSchema

studios_bp = Blueprint("studios", __name__)
create_schema = StudioCreateSchema()
update_schema = StudioUpdateSchema()


@studios_bp.get("", strict_slashes=False)
def find_all():
    return jsonify([studio.to_dict() for studio in Studio.query.order_by(Studio.name.asc()).all()])


@studios_bp.get("/<string:studio_id>")
def find_one(studio_id: str):
    studio = Studio.query.filter_by(id=studio_id).first()
    if studio is None:
        return jsonify(error=f"Studio with ID {studio_id} not found"), 404
    return jsonify(studio.to_detail_dict())


@studios_bp.post("")
@admin_required
def create():
    try:
        payload = create_schema.load(request.get_json(silent=True) or {})
    except ValidationError as error:
        return jsonify(error=error.messages), 400
    studio = Studio(**payload)
    db.session.add(studio)
    db.session.commit()
    return jsonify(studio.to_dict()), 201


@studios_bp.patch("/<string:studio_id>")
@admin_required
def update(studio_id: str):
    studio = Studio.query.filter_by(id=studio_id).first()
    if studio is None:
        return jsonify(error=f"Studio with ID {studio_id} not found"), 404
    try:
        payload = update_schema.load(request.get_json(silent=True) or {})
    except ValidationError as error:
        return jsonify(error=error.messages), 400
    for field, value in payload.items():
        setattr(studio, field, value)
    db.session.commit()
    return jsonify(studio.to_detail_dict())


@studios_bp.delete("/<string:studio_id>")
@admin_required
def remove(studio_id: str):
    studio = Studio.query.filter_by(id=studio_id).first()
    if studio is None:
        return jsonify(error=f"Studio with ID {studio_id} not found"), 404
    try:
        db.session.delete(studio)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(error="Studio cannot be deleted while it has showtimes"), 409
    return "", 204
