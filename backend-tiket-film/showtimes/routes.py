from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from auth.guards import admin_required
from extensions import db
from models import Movie, Showtime, Studio
from showtimes.schemas import ShowtimeCreateSchema, ShowtimeUpdateSchema

showtimes_bp = Blueprint("showtimes", __name__)
create_schema = ShowtimeCreateSchema()
update_schema = ShowtimeUpdateSchema()


@showtimes_bp.get("", strict_slashes=False)
def find_all():
    return jsonify([showtime.to_detail_dict() for showtime in Showtime.query.order_by(Showtime.start_time.asc()).all()])


@showtimes_bp.get("/<string:showtime_id>")
def find_one(showtime_id: str):
    showtime = Showtime.query.filter_by(id=showtime_id).first()
    if showtime is None:
        return jsonify(error="Showtime not found"), 404
    return jsonify(showtime.to_detail_dict())


def _overlap_exists(studio_id: str, start_time: object, end_time: object, excluded_id: str | None = None) -> bool:
    query = Showtime.query.filter(
        Showtime.studio_id == studio_id,
        Showtime.start_time < end_time,
        Showtime.end_time > start_time,
    )
    if excluded_id is not None:
        query = query.filter(Showtime.id != excluded_id)
    return query.first() is not None


def _references_exist(movie_id: str, studio_id: str) -> str | None:
    if Movie.query.filter_by(id=movie_id).first() is None:
        return "Movie not found"
    if Studio.query.filter_by(id=studio_id).first() is None:
        return "Studio not found"
    return None


@showtimes_bp.post("")
@admin_required
def create():
    try:
        payload = create_schema.load(request.get_json(silent=True) or {})
    except ValidationError as error:
        return jsonify(error=error.messages), 400
    missing_reference = _references_exist(str(payload["movie_id"]), str(payload["studio_id"]))
    if missing_reference:
        return jsonify(error=missing_reference), 404
    if _overlap_exists(str(payload["studio_id"]), payload["start_time"], payload["end_time"]):
        return jsonify(error="Showtime overlaps another showtime in this studio"), 409
    showtime = Showtime(
        **{
            **payload,
            "movie_id": str(payload["movie_id"]),
            "studio_id": str(payload["studio_id"]),
        }
    )
    db.session.add(showtime)
    db.session.commit()
    return jsonify(showtime.to_detail_dict()), 201


@showtimes_bp.patch("/<string:showtime_id>")
@admin_required
def update(showtime_id: str):
    showtime = Showtime.query.filter_by(id=showtime_id).first()
    if showtime is None:
        return jsonify(error="Showtime not found"), 404
    try:
        payload = update_schema.load(request.get_json(silent=True) or {})
    except ValidationError as error:
        return jsonify(error=error.messages), 400
    movie_id = str(payload.get("movie_id", showtime.movie_id))
    studio_id = str(payload.get("studio_id", showtime.studio_id))
    start_time = payload.get("start_time", showtime.start_time)
    end_time = payload.get("end_time", showtime.end_time)
    missing_reference = _references_exist(movie_id, studio_id)
    if missing_reference:
        return jsonify(error=missing_reference), 404
    if end_time <= start_time:
        return jsonify(error={"endTime": ["must be after startTime"]}), 400
    if _overlap_exists(studio_id, start_time, end_time, showtime.id):
        return jsonify(error="Showtime overlaps another showtime in this studio"), 409
    for field, value in payload.items():
        if field in {"movie_id", "studio_id"}:
            value = str(value)
        setattr(showtime, field, value)
    db.session.commit()
    return jsonify(showtime.to_detail_dict())


@showtimes_bp.delete("/<string:showtime_id>")
@admin_required
def remove(showtime_id: str):
    showtime = Showtime.query.filter_by(id=showtime_id).first()
    if showtime is None:
        return jsonify(error="Showtime not found"), 404
    db.session.delete(showtime)
    db.session.commit()
    return "", 204
