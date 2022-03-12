import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")

    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URI") or "sqlite:///../data.sqlite"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class TestConfig(Config):
    SECRET_KEY = "test_secret_key"
    SQLALCHEMY_DATABASE_URI = "sqlite://"


config = {"default": Config, "testing": TestConfig}
