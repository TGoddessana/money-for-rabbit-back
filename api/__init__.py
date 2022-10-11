from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from .db import db
from .ma import ma


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"*": {"origins": "*"}})
    load_dotenv(".env", verbose=True)
    app.config.from_object("config.default")
    app.config.from_envvar("APPLICATION_SETTINGS")

    api = Api(app)
    jwt = JWTManager(app)
    migrate = Migrate(app, db)

    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)
    return app
