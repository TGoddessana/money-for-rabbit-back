import hashlib


class NotValidConfrimationException(Exception):
    def __init__(self):
        super().__init__("유효하지 않은 이메일 검증입니다.")


def check_user(user_email, hashed_email):
    if not hashlib.sha256(user_email.encode()).hexdigest() == hashed_email:
        raise NotValidConfrimationException
