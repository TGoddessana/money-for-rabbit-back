import unittest
from api.db import db
from app import app
from flask import current_app


class CommonTestCaseSetting(unittest.TestCase):
    def setUp(self):
        self.url = "http://127.0.0.1:5000"
        self.client = app.test_client()
        self.client.application.config.from_object("config.test")
        with self.client.application.app_context():
            import warnings
            warnings.simplefilter('ignore', category=DeprecationWarning)
            db.create_all()

    def tearDown(self):
        with self.client.application.app_context():
            db.session.remove()
            db.drop_all()
