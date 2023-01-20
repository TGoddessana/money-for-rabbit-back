from flask import redirect
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource, request

from api.models.user import RefreshTokenModel, UserModel
from api.services.user import UserService
from api.utils.confrimation import NotValidConfrimationException, check_user
from api.utils.response import (FORBIDDEN, NOT_FOUND, REFRESH_TOKEN_ERROR,
                                get_response)


class UserInformation(Resource):
    @classmethod
    def get(cls, user_id):
        """마이페이지 정보조회를 수행합니다."""
        user = UserModel.find_by_id(user_id)
        if not user:
            return get_response(False, NOT_FOUND.format("사용자"), 404)
        return UserService(user).get_info()

    @classmethod
    @jwt_required()
    def put(cls, user_id):
        """닉네임 변경을 수행합니다."""
        if get_jwt_identity() != user_id:
            return get_response(False, FORBIDDEN, 403)
        data = request.get_json()
        user = UserModel.find_by_id(user_id)
        return UserService(user).update_info(data)


class UserLogin(MethodView):
    """
    Access Token, Refresh Token 을 발급하고,
    Refresh Token Rotation 을 수행합니다.
    """

    @classmethod
    def post(cls):
        data = request.get_json()
        user = UserModel.find_by_email(data["email"])
        if not user:
            return get_response(False, NOT_FOUND.format("사용자"), 404)
        return UserService(user).login(data)


class RefreshToken(MethodView):
    """
    리프레시 토큰으로 새로운 액세스 토큰을 발급합니다.
    """

    @classmethod
    @jwt_required(refresh=True)
    def post(cls):
        user = RefreshTokenModel.get_user_by_token(
            dict(request.headers)["Authorization"][7:]
        )
        if not user:
            return get_response(False, REFRESH_TOKEN_ERROR, 401)
        return UserService(user).refresh_login()


class UserRegister(Resource):
    """회원가입을 처리합니다."""

    @classmethod
    def post(cls):
        data = request.get_json()
        return UserService().register(data)


class UserWithdraw(Resource):
    """
    회원탈퇴를 처리합니다.
    본인만 회원탈퇴를 진행할 수 있습니다.
    """

    @classmethod
    @jwt_required()
    def delete(cls):
        """
        클라이언트 -> email, password (로그인과 동일)
        """
        data = request.get_json()
        user = UserModel.find_by_id(get_jwt_identity())
        if not user:
            return get_response(False, NOT_FOUND.format("사용자"), 404)
        return UserService(user).withdraw(data)


class UserConfirm(Resource):
    """
    이메일 인증을 처리합니다.
    """

    @classmethod
    def get(cls, user_id, hashed_email):
        user = UserModel.find_by_id(user_id)
        if not user:
            return redirect("https://money-for-rabbit.netlify.app/signup/fail")
        if user.email_confirmed:
            return redirect("https://money-for-rabbit.netlify.app/")
        try:
            check_user(user.email, hashed_email)
        except NotValidConfrimationException as e:
            return redirect("https://money-for-rabbit.netlify.app/signup/fail")
        user.email_confirmed = True
        user.save_to_db()
        return redirect("https://money-for-rabbit.netlify.app/signup/done")
