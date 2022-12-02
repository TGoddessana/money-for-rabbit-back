import hashlib
from api.db import db
from api.models.message import MessageModel
from flask_mail import Message, Mail
from flask import current_app, render_template


class UserModel(db.Model):
    __tablename__ = "User"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=False)  # 중복가능
    password = db.Column(db.String(102), nullable=False)
    email = db.Column(db.String(80), nullable=False, unique=True)  # 중복불가능
    date_joined = db.Column(db.DateTime, server_default=db.func.now())
    message_set = db.relationship(
        "MessageModel", backref="user", passive_deletes=True, lazy="dynamic"
    )
    is_active = db.Column(db.Boolean, default=False)

    def send_email(self):
        msg = Message(
            f"[Money For Rabbit] - {self.username} 님, 인증을 완료해 주세요.",
            sender="twicegoddessana1229@gmail.com",
            recipients=[self.email],
        )
        hashed_email = hashlib.sha256(self.email.encode()).hexdigest()
        msg.html = render_template(
            "confirmation_email.html",
            hashed_email=hashed_email,
            user_id=self.id,
        )
        with current_app.app_context():
            mail = Mail()
            mail.send(msg)

    @classmethod
    def find_by_username(cls, username):
        """
        데이터베이스에서 이름으로 특정 사용자 찾기
        """
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email):
        """
        데이터베이스에서 이메일로 특정 사용자 찾기
        """
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, id):
        """
        데이터베이스에서 id 로 특정 사용자 찾기
        """
        return cls.query.filter_by(id=id).first()

    def save_to_db(self):
        """
        사용자를 데이터베이스에 저장
        """
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        """
        사용자를 데이터베이스에서 삭제
        """
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f"<User Object : {self.username}>"


class RefreshTokenModel(db.Model):
    __tablename__ = "RefreshToken"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("User.id", ondelete="CASCADE"),
        nullable=False,
    )
    user = db.relationship("UserModel", backref="token")
    refresh_token_value = db.Column(
        db.String(512), nullable=False, unique=True
    )

    def save_to_db(self):
        """
        토큰을 데이터베이스에 저장
        """
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        """
        토큰을 데이터베이스에서 삭제
        """
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_user_by_token(cls, token):
        """
        리프레시 토큰 값으로 user 객체를 얻어옴
        """
        try:
            user_id = (
                cls.query.filter_by(refresh_token_value=token).first().user_id
            )
        except AttributeError:
            return None
        user = UserModel.find_by_id(id=user_id)
        return user
