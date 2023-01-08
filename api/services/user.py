from api.schemas.user import UserInformationSchema, UserRegisterSchema
from api.utils.response import get_response
from api.utils.response import EMAIL_DUPLICATED, WELCOME_NEWBIE
from api.utils.validation import (
    validate_password,
    validate_email,
    NotValidDataException,
)
from api.models.user import UserModel
from werkzeug.security import generate_password_hash, check_password_hash


class UserService:
    """
    사용자:
        - 정보조회
        - 정보수정
        - 회원가입
        - 회원탈퇴
        - 로그인
    """

    def __init__(self, user=None):
        self.user = user

    def get_info(self):
        return {"user_info": UserInformationSchema().dump(self.user)}

    def update_info(self, data):
        validate_result = UserInformationSchema().validate(data)
        if validate_result:
            return get_response(False, validate_result, 400)
        self.user.update_user_info(data["username"])
        return get_response(True, f"닉네임이 {self.user.username} 으로 변경되었습니다.", 200)

    def register(self, data):
        validate_result = UserRegisterSchema().validate(data)
        if validate_result:
            return validate_result, 400
        try:
            validate_password(data.get("password"))
        except NotValidDataException as e:
            return get_response(False, str(e), 400)
        try:
            validate_email(data.get("email"))
        except NotValidDataException as e:
            return get_response(False, str(e), 400)
        if UserModel.find_by_email(data["email"]):
            return get_response(False, EMAIL_DUPLICATED, 400)
        else:
            password = generate_password_hash(data["password"])
            user = UserRegisterSchema().load(
                {
                    "username": data["username"],
                    "email": data["email"],
                    "password": password,
                }
            )
        user.save_to_db()
        user.send_email()
        return get_response(True, WELCOME_NEWBIE.format(user.username), 201)

    def withdraw(self):
        pass

    def login(self, refresh: bool):
        pass
