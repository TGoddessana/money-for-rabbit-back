from api.models.user import UserModel, RefreshTokenModel
from flask_restful import Resource, request
from api.schemas.user import UserRegisterSchema
from werkzeug.security import generate_password_hash
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from flask.views import MethodView
from werkzeug.security import check_password_hash
from api.utils.confrimation import check_user, NotValidConfrimationException
from flask import redirect
from api.utils.response import (
    get_response,
    EMAIL_NOT_CONFIRMED,
    ACCOUNT_INFORMATION_NOT_MATCH,
    WELCOME_NEWBIE,
    EMAIL_DUPLICATED,
    REFRESH_TOKEN_ERROR,
)

register_schema = UserRegisterSchema()


class UserLogin(MethodView):
    """
    로그인을 처리합니다.
    로그인 시, 무조건 새로운 refresh token 을 발급하고,
    그것을 데이터베이스에 저장합니다.
    """

    @classmethod
    def post(cls):
        data = request.get_json()
        user = UserModel.find_by_email(data["email"])
        if user and check_password_hash(user.password, data["password"]):
            if user.is_active:
                access_token = create_access_token(
                    identity=user.username, fresh=True
                )
                refresh_token = create_refresh_token(identity=user.username)
                if user.token:
                    token = user.token[0]
                    token.refresh_token_value = refresh_token
                    token.save_to_db()
                else:
                    new_token = RefreshTokenModel(
                        user_id=user.id, refresh_token_value=refresh_token
                    )
                    new_token.save_to_db()
                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                }, 200
            return get_response(False, EMAIL_NOT_CONFIRMED, 400)
        return get_response(False, ACCOUNT_INFORMATION_NOT_MATCH, 401)


class RefreshToken(MethodView):
    """
    리프레시 토큰으로 새로운 액세스 토큰을 발급합니다.
    """

    @classmethod
    @jwt_required(refresh=True)
    def post(cls):
        identity = get_jwt_identity()
        token = dict(request.headers)["Authorization"][7:]
        user = RefreshTokenModel.get_user_by_token(token)
        if not user:
            return get_response(False, REFRESH_TOKEN_ERROR, 401)
        # access token, refresh token 발급
        access_token = create_access_token(fresh=True, identity=identity)
        refresh_token = create_refresh_token(identity=user.username)
        if user:
            token = user.token[0]
            token.refresh_token_value = refresh_token
            token.save_to_db()
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
            }, 200


class UserRegister(Resource):
    """
    회원가입을 처리합니다.
    """

    @classmethod
    def post(cls):
        data = request.get_json()
        validate_result = register_schema.validate(data)
        if validate_result:
            return validate_result, 400
        else:
            if UserModel.find_by_email(data["email"]):
                return get_response(False, EMAIL_DUPLICATED, 400)
            else:
                password = generate_password_hash(data["password"])
                user = register_schema.load(
                    {
                        "username": data["username"],
                        "email": data["email"],
                        "password": password,
                    }
                )
            user.save_to_db()
            user.send_email()
            return get_response(
                True, WELCOME_NEWBIE.format(user.username), 201
            )


class UserConfirm(Resource):
    """
    이메일 인증을 처리합니다.
    """

    @classmethod
    def get(cls, user_id, hashed_email):
        user = UserModel.find_by_id(user_id)
        if not user:
            return redirect("https://money-for-rabbit.netlify.app/signup/fail")
        if user.is_active:
            return redirect("https://money-for-rabbit.netlify.app/")
        try:
            check_user(user.email, hashed_email)
        except NotValidConfrimationException as e:
            return redirect("https://money-for-rabbit.netlify.app/signup/fail")
        user.is_active = True
        user.save_to_db()
        return redirect("https://money-for-rabbit.netlify.app/signup/done")
