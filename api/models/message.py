from sqlalchemy.orm import validates

from api.db import db


class MessageModel(db.Model):
    """
    money for rabit 서비스를 위한 쪽지 모델

    user_id = 해당 쪽지가 달려있는 유저의 id
    author_id = 해당 쪽지를 작성한 유저의 id
    message = 쪽지의 내용
    amount = 돈의 양
    is_moneybag = 봉투 여부 (사용자는 봉투와 함게 5000원을 전달할 수도 있고,
                            봉투와 함께 5001원을 전달할 수 있음)
    """

    __tablename__ = "Message"

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    is_moneybag = db.Column(db.Boolean(), nullable=False)
    # 쪽지 쓴 사람
    author_id = db.Column(
        db.Integer,
        db.ForeignKey("User.id", ondelete="CASCADE"),
        nullable=True,
    )
    author = db.relationship(
        "UserModel",
        backref=db.backref("recieved_messages", cascade="all, delete-orphan"),
        foreign_keys=author_id,
    )
    # 쪽지 받은 사람
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("User.id", ondelete="CASCADE"),
        nullable=True,
    )

    def __init__(self, **kwargs):
        super(MessageModel, self).__init__(**kwargs)
        MONEY_TYPES = [100, 500, 1000, 5000, 10000, 50000, 99999]
        if self.is_moneybag == False and not self.amount in MONEY_TYPES:
            raise ValueError("화폐단위에 벗어난 액수를 선택하려면 돈봉투를 사용하세요.")

    @property
    def money_image_name(self):
        if self.is_moneybag:
            return "Money_99999.png"
        else:
            return f"Money_{self.amount}.png"

    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def find_by_id(cls, id):
        """
        데이터베이스에서 id 로 특정 쪽지 찾기
        """
        return cls.query.filter_by(id=id).first()

    def save_to_db(self):
        """
        쪽지를 데이터베이스에 저장
        """
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        """
        쪽지를 데이터베이스에서 삭제
        """
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f"<Message Object : {self.message}>"
