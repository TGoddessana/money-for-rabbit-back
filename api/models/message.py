from api.db import db


class MessageModel(db.Model):
    """
    money for rabit 서비스를 위한 쪽지 모델

    user_id = 해당 쪽지가 달려있는 유저의 id
    nickname = 닉네임
    message = 쪽지의 내용
    amount = 돈의 양
    is_moneybag = 봉투 여부 (사용자는 봉투와 함게 5000원을 전달할 수도 있고,
                            봉투와 함께 5001원을 전달할 수 있음)
    """

    __tablename__ = "Message"

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(10))  # 중복가능
    message = db.Column(db.String(150))
    amount = db.Column(db.Integer)
    is_moneybag = db.Column(db.Boolean())

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("User.id", ondelete="CASCADE"),
        nullable=False,
    )
