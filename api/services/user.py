from api.schemas.user import (
    UserInformationSchema,
    UserRegisterSchema,
    UserLoginSchema,
    UserWithdrawSchema,
)
from api.utils.auth import create_username_access_token, create_userid_refresh_token
from api.utils.response import (
    get_response,
    EMAIL_NOT_CONFIRMED,
    ACCOUNT_INFORMATION_NOT_MATCH,
)
from api.utils.response import EMAIL_DUPLICATED, WELCOME_NEWBIE
from api.utils.validation import (
    validate_password,
    validate_email,
    NotValidDataException,
)
from api.models.user import UserModel, RefreshTokenModel
from werkzeug.security import generate_password_hash, check_password_hash

from flask_jwt_extended import create_access_token, create_refresh_token


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

    def withdraw(self, data):
        validate_result = UserWithdrawSchema().validate(data)
        if validate_result:
            return validate_result, 400
        if self.user.username == data["username"]:
            self.user.delete_from_db()
            return "", 204
        else:
            return get_response(False, "잘못된 접근입니다.", 400)

    def login(self, data):
        validate_result = UserLoginSchema().validate(data)
        if validate_result:
            return validate_result, 400
        if not check_password_hash(self.user.password, data["password"]):
            return get_response(False, ACCOUNT_INFORMATION_NOT_MATCH, 401)
        if not self.user.is_active:
            return get_response(False, EMAIL_NOT_CONFIRMED, 400)
        new_access_token = create_username_access_token(self.user)
        new_refresh_token = create_userid_refresh_token(self.user)
        if self.user.token:
            token = self.user.token[0]
            token.refresh_token_value = new_refresh_token
            token.save_to_db()
        else:
            new_token = RefreshTokenModel(
                user_id=self.user.id, refresh_token_value=new_refresh_token
            )
            new_token.save_to_db()
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
        }, 200

    def refresh_login(self):
        new_access_token = create_username_access_token(self.user)
        new_refresh_token = create_userid_refresh_token(self.user)
        token = self.user.token[0]
        token.refresh_token_value = new_refresh_token
        token.save_to_db()
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
        }, 200
