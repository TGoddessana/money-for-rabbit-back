from dotenv import load_dotenv
from flask import Flask, jsonify, render_template
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_restful import Api

from .db import db
from .ma import ma
from .models.user import MessageModel, RefreshTokenModel, UserModel
from .resources.deploy import DeployServer
from .resources.index import IndexPage
from .resources.message import MessageDetail, MessageList
from .resources.user import RefreshToken, UserConfirm, UserLogin, UserRegister


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"*": {"origins": "*"}})
    load_dotenv(".env", verbose=True)
    app.config.from_envvar("APPLICATION_SETTINGS")

    mail = Mail(app)
    api = Api(app)
    jwt = JWTManager(app)
    migrate = Migrate(app, db)
    admin = Admin()
    admin.add_view(ModelView(UserModel, db.session))
    admin.add_view(ModelView(MessageModel, db.session))
    admin.add_view(ModelView(RefreshTokenModel, db.session))

    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        db.create_all()
        from api.resources import error

    # API 명세
    api.add_resource(IndexPage, "/")

    # 유저 관련 API
    api.add_resource(UserRegister, "/api/user/register")
    api.add_resource(UserLogin, "/api/user/login")
    api.add_resource(RefreshToken, "/api/user/refresh")
    api.add_resource(
        UserConfirm, "/api/confirm-user/<int:user_id>/<string:hashed_email>"
    )

    # 쪽지 관련 API
    api.add_resource(MessageList, "/api/user/<int:user_id>/messages")
    api.add_resource(
        MessageDetail, "/api/user/<int:user_id>/messages/<int:message_id>"
    )

    # 배포 web hook 을 위한 엔드포인트
    api.add_resource(DeployServer, "/update-server")

    return app
