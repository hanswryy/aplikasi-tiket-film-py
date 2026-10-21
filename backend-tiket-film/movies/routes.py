from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from models import Movie
from movies.schemas import MovieQuerySchema

movies_bp = Blueprint("movies", __name__)
movie_query_schema = MovieQuerySchema()


@movies_bp.get("", strict_slashes=False)
def find_all():
    try:
        query_params = movie_query_schema.load(request.args.to_dict())
    except ValidationError as error:
        return jsonify(error=error.messages), 400
    search = (query_params.get("search") or "").strip()
    query = Movie.query
    if search:
        query = query.filter(Movie.title.ilike(f"%{search}%"))
    return jsonify([movie.to_dict() for movie in query.order_by(Movie.title.asc()).all()])


@movies_bp.get("/<string:movie_id>")
def find_one(movie_id: str):
    movie = Movie.query.filter_by(id=movie_id).first()
    if movie is None:
        return jsonify(error=f"Movie with ID {movie_id} not found"), 404
    return jsonify(movie.to_detail_dict())
