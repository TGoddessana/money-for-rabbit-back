from flask_admin.contrib.sqla import ModelView


class UserAdminView(ModelView):
    column_list = ("id", "username", "email", "is_active")


class MessageAdminView(ModelView):
    column_list = ("id", "message", "amount", "is_moneybag")
