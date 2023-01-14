import re
import string


class NotValidDataException(Exception):
    def __init__(self, type, additional_message=None):
        if additional_message:
            super().__init__(f"유효한 {type} 값이 아닙니다. {additional_message}")
        else:
            super().__init__(f"유효한 {type} 값이 아닙니다.")


def validate_password(password):
    """12 ~ 16자, 대문자 1개, 소문자 1개, 숫자 1개 및 특수 문자 1개"""
    regex = re.compile(
        r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[!@#$%^&*])[A-Za-z0-9!@#$%^&*]{12,16}$"
    )
    if re.search(regex, password):
        pass
    else:
        raise NotValidDataException(
            type="비밀번호",
            additional_message="12 ~ 16자, 대문자 1개, 소문자 1개, 숫자 1개 및 특수 문자 1개를 포함해야 합니다.",
        )


def validate_email(email):
    regex = r"\"?([-a-zA-Z0-9.`?{}]+@\w+\.\w+)\"?"
    if re.search(regex, email):
        pass
    else:
        raise NotValidDataException("이메일")
