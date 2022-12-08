from flask_admin.contrib.sqla import ModelView

from api.models.user import UserModel


class AView(ModelView):
    def __init__(self, session, **kwargs):
        super(AView, self).__init__(UserModel, session, **kwargs)
