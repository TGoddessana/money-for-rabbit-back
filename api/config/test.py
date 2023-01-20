from api.config.default import *

TESTING = False

JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=1)

SQLALCHEMY_DATABASE_URI = "sqlite:///{}".format(os.path.join(BASE_DIR, "test.db"))
