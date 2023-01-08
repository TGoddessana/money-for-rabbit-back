from api.config.default import *

TESTING = True

SQLALCHEMY_DATABASE_URI = "sqlite:///{}".format(os.path.join(BASE_DIR, "test.db"))
