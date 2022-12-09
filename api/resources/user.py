from flask import redirect
from flask.views import MethodView
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from flask_restful import Resource, request
from werkzeug.security import check_password_hash, generate_password_hash

from api.models.user import RefreshTokenModel, UserModel
from api.schemas.user import UserRegisterSchema
from api.utils.confrimation import NotValidConfrimationException, check_user
from api.utils.response import (
    ACCOUNT_INFORMATION_NOT_MATCH,
    NOT_FOUND,
    EMAIL_DUPLICATED,
    EMAIL_NOT_CONFIRMED,
    REFRESH_TOKEN_ERROR,
    WELCOME_NEWBIE,
    get_response,
)

register_schema = UserRegisterSchema()


class UserInformation(Resource):
    @classmethod
    @jwt_required()
    def put(cls, user_id):
        data = request.get_json()
        if not data.get("username"):
            return get_response(False, "적절한 데이터를 입력하세요.", 400)
        if not user_id == get_jwt_identity():
            return get_response(False, "본인만 정보수정이 가능합니다.", 403)
        user = UserModel.find_by_id(user_id)
        if not user:
            return get_response(False, NOT_FOUND.format("사용자"), 404)
        user.username = data["username"]
        user.save_to_db()
        return get_response(True, f"닉네임이 {user.username} 으로 변경되었습니다.", 200)


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
                # TOKEN 발급
                additional_claims = {"nickname": user.username}
                access_token = create_access_token(
                    identity=user.id,
                    fresh=True,
                    additional_claims=additional_claims,
                )
                refresh_token = create_refresh_token(
                    identity=user.id,
                    additional_claims=additional_claims,
                )
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
        additional_claims = {"nickname": user.username}
        access_token = create_access_token(
            identity=user.id,
            fresh=True,
            additional_claims=additional_claims,
        )
        refresh_token = create_refresh_token(
            identity=user.id,
            additional_claims=additional_claims,
        )
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


class UserWithdraw(Resource):
    """
    회원탈퇴를 처리합니다.
    본인만 회원탈퇴를 진행할 수 있습니다.
    """

    @classmethod
    @jwt_required()
    def delete(cls):
        user = UserModel.find_by_id(get_jwt_identity())
        if user:
            user.delete_from_db()
            return "", 204
        else:
            return get_response(False, NOT_FOUND.format("사용자"), 404)


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
