from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView
from flask_admin import expose, AdminIndexView
from api.models.user import UserModel
from api.models.message import MessageModel


class HomeAdminView(AdminIndexView):
    def is_visible(self):
        return True

    @expose("/")
    def index(self):
        user_count = len(UserModel.query.all())
        message_count = len(MessageModel.find_all())
        return self.render(
            "admin-home.html",
            user_count=user_count,
            message_count=message_count,
        )


class UserAdminView(ModelView):
    can_create = False
    column_filters = ["is_active"]
    column_searchable_list = ["username", "email", "id"]
    column_list = ["id", "username", "email", "is_active"]


class MessageAdminView(ModelView):
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
        return model.author.email

    def get_reciepient_email(view, context, model, name):
        return model.user.email

    column_formatters = {
        "from": get_author_email,
        "to": get_reciepient_email,
    }
