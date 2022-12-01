from flask import Flask, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from marshmallow import ValidationError

from .models.user import UserModel, MessageModel

from .resources.deploy import DeployServer
from .resources.user import UserLogin, UserRegister, RefreshToken
from .resources.message import MessageList, MessageDetail, AdminMessageList


from .db import db
from .ma import ma


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"*": {"origins": "*"}})
    load_dotenv(".env", verbose=True)
    app.config.from_envvar("APPLICATION_SETTINGS")

    api = Api(app)
    jwt = JWTManager(app)
    migrate = Migrate(app, db)
    admin = Admin(
        app,
        url="/mfr-admin/",
        base_template="admin-home.html",
        name="money for rabbit",
        template_mode="bootstrap3",
    )
    admin.add_view(ModelView(UserModel, db.session))
    admin.add_view(ModelView(MessageModel, db.session))

    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)

    def create_tables():
        db.create_all()

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

    @app.route("/")
    def api_root():
        urls = [rule for rule in app.url_map.iter_rules()]
        url = [str(url) for url in urls][1:]
        return render_template("index.html")

    # 유저 관련 API
    api.add_resource(UserRegister, "/api/user/register")
    api.add_resource(UserLogin, "/api/user/login")
    api.add_resource(RefreshToken, "/api/user/refresh")

    # 쪽지 관련 API
    api.add_resource(MessageList, "/api/user/<int:user_id>/messages")
    api.add_resource(
        MessageDetail, "/api/user/<int:user_id>/messages/<int:message_id>"
    )

    # 배포 web hook 을 위한 엔드포인트
    api.add_resource(DeployServer, "/update-server")

    return app
