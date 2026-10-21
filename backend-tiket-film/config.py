import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///cinema.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv(
        "JWT_SECRET",
        "development-only-secret-change-me-32-chars",
    )
    MIDTRANS_SERVER_KEY = os.getenv("MIDTRANS_SERVER_KEY")
    MIDTRANS_CLIENT_KEY = os.getenv("MIDTRANS_CLIENT_KEY")
    MIDTRANS_IS_PRODUCTION = os.getenv("MIDTRANS_IS_PRODUCTION", "false").lower() == "true"


class DevelopmentConfig(Config):
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


CONFIG_BY_NAME = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": Config,
}
