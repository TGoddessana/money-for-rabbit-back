from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from flask_admin import Admin
from flask_login import LoginManager
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from api.resources.admin import admin_login_view
from cli import create_admin_user
from .models.user import UserModel, MessageModel
from .resources.deploy import DeployServer
from .resources.user import (
    UserLogin,
    UserRegister,
    UserWithdraw,
    RefreshToken,
    UserConfirm,
    UserInformation,
)
from .resources.message import MessageList, MessageDetail
from .resources.admin import (
    UserAdminView,
    MessageAdminView,
    HomeAdminView,
)

from flask_mail import Mail
from .db import db
from .ma import ma

import os


def create_app(is_production=True):
    app = Flask(__name__)
    CORS(app, resources={r"*": {"origins": "*"}})
    load_dotenv(".env", verbose=True)
    if is_production:
        config = os.getenv("APPLICATION_SETTINGS_PROD")
    else:
        config = os.getenv("APPLICATION_SETTINGS_TEST")
    app.config.from_object(config)

    # Command line interface
    app.cli.add_command(create_admin_user)

    login_manager = LoginManager()
    mail = Mail(app)
    api = Api(app)
    jwt = JWTManager(app)
    migrate = Migrate(app, db)
    admin = Admin(
        app,
        url="/mfr-admin/",
        base_template="admin-modelview.html",
        name="money for rabbit",
        template_mode="bootstrap3",
        index_view=HomeAdminView(url="/mfr-admin/"),
    )

    login_manager.init_app(app)
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        db.create_all()
        from api.resources import error

    @login_manager.user_loader
    def load_user(user_id):
        return UserModel.find_by_id(user_id)

    # ADMIN Page
    admin.add_view(UserAdminView(model=UserModel, session=db.session, name="Users"))
    admin.add_view(
        MessageAdminView(model=MessageModel, session=db.session, name="Messages")
    )
    app.register_blueprint(admin_login_view)

    # 유저 관련 API
    api.add_resource(UserRegister, "/api/user/register")
    api.add_resource(UserWithdraw, "/api/user/withdraw")
    api.add_resource(UserLogin, "/api/user/login")
    api.add_resource(UserInformation, "/api/user/<int:user_id>")
    api.add_resource(RefreshToken, "/api/user/refresh")
    api.add_resource(
        UserConfirm, "/api/confirm-user/<int:user_id>/<string:hashed_email>"
    )

    # 쪽지 관련 API
    api.add_resource(MessageList, "/api/user/<int:user_id>/messages")
    api.add_resource(MessageDetail, "/api/user/<int:user_id>/messages/<int:message_id>")

    # 배포 web hook 을 위한 엔드포인트
    api.add_resource(DeployServer, "/update-server")

    return app
