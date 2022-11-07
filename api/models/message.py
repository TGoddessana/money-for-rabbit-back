from api.db import db


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    is_moneybag = db.Column(db.Boolean)