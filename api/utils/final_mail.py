from flask import current_app, render_template
from flask_mail import Message, Mail

from api.models.message import MessageModel
from api.models.user import UserModel


def send_final_mail():
    """
    회원가입한 모든 사용자에 대해서,
    1. 쪽지를 받은 사람 : 몇 명에게, 얼마를 받았는지
    2. 쪽지를 안 받은 사람 : 템플릿 그대로 뿌려줌
    """
    from dev_app import app

    app.app_context().push()
    for user in UserModel.query.all():
        if user.message_set.all():
            author_count = len(
                set([message.author_id for message in user.message_set.all()])
            )
            total_amount = user.total_amount
            msg = Message(
                f"[Money For Rabbit] {user.username}님, 쪽지를 확인해 보세요!",
                sender="moneyforrabbit@5nonymous.tk",
                recipients=[user.email],
            )
            msg.html = render_template(
                "received-alert-template.html",
                author_count=author_count,
                total_amount=user.total_amount,
            )
            with current_app.app_context():
                mail = Mail()
                mail.send(msg)
        else:
            msg = Message(
                f"[Money For Rabbit] {user.username}님, 쪽지 링크를 공유해 보세요!",
                sender="moneyforrabbit@5nonymous.tk",
                recipients=[user.email],
            )
            msg.html = render_template(
                "no-received-alert-template.html",
            )
            with current_app.app_context():
                mail = Mail()
                mail.send(msg)
