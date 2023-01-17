from flask import Blueprint, abort, flash, redirect, render_template, request, session
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash

from api.models.message import MessageModel
from api.models.user import UserModel
from api.utils.validation import NotValidDataException, validate_email

admin_login_view = Blueprint("admin_login_bp", __name__, url_prefix="/mfr-admin")


@admin_login_view.route("/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            validate_email(email)
        except NotValidDataException as e:
            flash(str(e), category="error")
        user = UserModel.find_by_email(email)
        if user and check_password_hash(user.password, password):
            if user.is_admin:  # 사용자가 admin 이면 로그인
                session.permanent = True
                login_user(user)
                return redirect("/mfr-admin/")
            else:  # 아니면
                flash("관리자 권한이 없습니다.", category="error")
                return abort(403)
        flash("이메일과 비밀번호를 확인하세요.", category="error")
        return redirect("/mfr-admin/login")
    elif request.method == "GET":
        return render_template("admin-login.html")


@admin_login_view.route("/logout")
@login_required
def admin_logout():
    logout_user()
    return redirect("/mfr-admin/login")


class AdminPermissionMixin:
    def is_accessible(self):
        return current_user.is_admin


class HomeAdminView(AdminPermissionMixin, AdminIndexView):
    @login_required
    def is_accessible(self):
        return super().is_accessible()

    def is_visible(self):
        return True

    @expose("/")
    def index(self):
        user_count = len(UserModel.query.all())
        message_count = len(MessageModel.find_all())
        return self.render(
            "admin-indexview.html",
            user_count=user_count,
            message_count=message_count,
        )


class UserAdminView(AdminPermissionMixin, ModelView):
    @login_required
    def is_accessible(self):
        return super().is_accessible()

    can_create = False
    column_filters = ["email_confirmed"]
    column_searchable_list = ["username", "email", "id"]
    column_list = ["id", "username", "email", "email_confirmed", "is_admin"]


class MessageAdminView(AdminPermissionMixin, ModelView):
    @login_required
    def is_accessible(self):
        return super().is_accessible()

    can_create = False
    column_filters = ["is_moneybag"]
    column_searchable_list = ["message", "amount", "id"]
    column_list = [
        "id",
        "message",
        "amount",
        "is_moneybag",
        "from",
        "to",
    ]

    def get_author_email(view, context, model, name):
        return model.author.email if model.user else None

    def get_reciepient_email(view, context, model, name):
        return model.user.email if model.user else None

    column_formatters = {
        "from": get_author_email,
        "to": get_reciepient_email,
    }
