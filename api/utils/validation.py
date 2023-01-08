import re
import string


class NotValidDataException(Exception):
    def __init__(self, type):
        super().__init__(f"유효한 {type} 값이 아닙니다.")


def validate_password(password):
    """12 ~ 16자, 대문자 1개, 소문자 1개, 숫자 1개 및 특수 문자 1개"""
    regex = r"(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[{}])[A-Za-z0-9{}]{{12,16}}".format(
        re.escape(string.punctuation), re.escape(string.punctuation)
    )
    if re.search(regex, password):
        pass
    else:
        raise NotValidDataException("비밀번호")


def validate_email(email):
    regex = r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?"
    if re.search(regex, email):
        pass
    else:
        raise NotValidDataException("이메일")
