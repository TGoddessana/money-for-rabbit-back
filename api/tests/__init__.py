import unittest

from api import create_app
from api.db import db

app = create_app(is_production=False)


class CommonTestCaseSetting(unittest.TestCase):
    def setUp(self):
        self.url = "http://127.0.0.1:5000"
        self.client = app.test_client()
        with self.client.application.app_context():
            import warnings

            warnings.simplefilter("ignore", category=DeprecationWarning)
            db.create_all()

    def tearDown(self):
        with self.client.application.app_context():
            db.session.remove()
            db.drop_all()
