import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import git

from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from marshmallow import ValidationError

from .resources.user import UserLogin, UserRegister, RefreshToken
from .schemas.user import UserRegisterSchema

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

    @app.errorhandler(ValidationError)
    def handle_marshmallow_validation(err):
        return jsonify(err.messages), 400

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (jsonify({"Error": "토큰이 만료되었습니다."}), 401)

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (jsonify({"Error": "잘못된 토큰입니다."}), 401)

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "Error": "토큰 정보가 필요합니다.",
                }
            ),
            401,
        )

    # register Resources...
    api.add_resource(UserRegister, "/api/user/register")
    api.add_resource(UserLogin, "/api/user/login")
    api.add_resource(RefreshToken, "/api/user/refresh")

    # for web hook ...
    @app.route("/update-server", methods=["POST"])
    def webhook():
        if request.method == "POST":
            BASE_DIR = os.path.dirname(os.path.dirname(__file__))
            repo = git.Repo(BASE_DIR)
            origin = repo.remotes.origin
            origin.pull()
            return "Pythonanywhere 서버에 성공적으로 업로드되었습니다!", 200
        else:
            return "유효하지 않은 이벤트 타입입니다.", 400

    @app.route("/")
    def welcome():
        return "Pythonanywhere 과 webhook 를 이용한 자동배포 성공!"

    return app
