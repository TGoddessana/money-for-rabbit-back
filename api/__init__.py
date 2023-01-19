import os
from datetime import datetime

#
# from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from flask import Flask
from flask_admin import Admin
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_restful import Api

from api.resources.admin import admin_login_view
from cli import create_admin_user

from .db import db
from .ma import ma
from .models.user import MessageModel, UserModel
from .resources.admin import HomeAdminView, MessageAdminView, UserAdminView
from .resources.deploy import DeployServer
from .resources.message import MessageDetail, MessageList
from .resources.user import (
    RefreshToken,
    UserConfirm,
    UserInformation,
    UserLogin,
    UserRegister,
    UserWithdraw,
)


def create_app(is_production=True):
    app = Flask(__name__)
    CORS(
        app,
        supports_credentials=True,
        resources={
            r"*": {
                "origins": [
                    "https://money-for-rabbit.netlify.app/",
                    "http://localhost:3000",
                ]
            }
        },
    )
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

    # DB 생성
    with app.app_context():
        db.create_all()
        from api.resources import error

    # Flask-Login
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

    # from api.utils.final_mail import send_final_mail

    # schedule = BackgroundScheduler(daemon=True, timezone="Asia/Seoul")
    # schedule.add_job(send_final_mail, "date", run_date=datetime(2023, 1, 22))
    # schedule.start()

    return app
