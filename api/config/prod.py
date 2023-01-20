from api.config.default import *

DEBUG = False

JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=3)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DBNAME = os.getenv("DB_DBNAME")
DB_ADDRESS = os.getenv("DB_ADDRESS")

SQLALCHEMY_DATABASE_URI = (
    f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_ADDRESS}/{DB_DBNAME}"
)
SQLALCHEMY_ENGINE_OPTIONS = {"pool_recycle": 280}
