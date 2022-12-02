from datetime import timedelta
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DEBUG = True

SQLALCHEMY_DATABASE_URI = "sqlite:///{}".format(
    os.path.join(BASE_DIR, "moneyforrabit.db")
)

SQLALCHEMY_TRACK_MODIFICATIONS = False
PROPGATE_EXECPTIONS = True
JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
SECRET_KEY = os.environ["APP_SECRET_KEY"]
JWT_BLACKLIST_ENABLED = True
JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
JSON_AS_ASCII = False
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
RESTFUL_JSON = dict(ensure_ascii=False)
FLASK_ADMIN_SWATCH = "journal"


MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 465
MAIL_USERNAME = os.environ["MAIL_USERNAME"]
MAIL_PASSWORD = os.environ["MAIL_PASSWORD"]
MAIL_USE_TLS = False
MAIL_USE_SSL = True
