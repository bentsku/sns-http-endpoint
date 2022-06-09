from flask import Flask
from flask_redis import FlaskRedis
from app.config_app import Config

__version__ = "0.0.1"

user_store = FlaskRedis(decode_responses=True)


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    user_store.init_app(app)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix="/api/v1/sns-endpoint")

    return app
