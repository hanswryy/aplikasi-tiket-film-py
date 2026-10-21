import os

from flask import Flask, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from config import CONFIG_BY_NAME
from extensions import db, jwt


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)
    selected_config = config_name or os.getenv("FLASK_ENV", "development")
    app.config.from_object(CONFIG_BY_NAME.get(selected_config, CONFIG_BY_NAME["development"]))

    db.init_app(app)
    jwt.init_app(app)
    Migrate(app, db)
    CORS(app)

    from auth.routes import auth_bp
    from bookings.routes import bookings_bp
    from movies.routes import movies_bp
    from showtimes.routes import showtimes_bp
    from studios.routes import studios_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(movies_bp, url_prefix="/movies")
    app.register_blueprint(studios_bp, url_prefix="/studios")
    app.register_blueprint(showtimes_bp, url_prefix="/showtimes")
    app.register_blueprint(bookings_bp, url_prefix="/bookings")

    @app.get("/")
    def health():
        return jsonify(message="Hello World!")

    with app.app_context():
        import models
        from seed import seed_database

        @app.cli.command("seed")
        def seed_command() -> None:
            """Reset and seed the database with the JS sample data."""
            seed_database()
            print("Database seed completed successfully.")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "3000")))
