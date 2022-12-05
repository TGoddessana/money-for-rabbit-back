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

register_schema = UserRegisterSchema()


class UserLogin(MethodView):
    """
    로그인을 처리합니다.
    로그인 시, 무조건 새로운 refresh token 을 발급하고,
    그것을 데이터베이스에 저장합니다.
    """

    def post(self):
        data = request.get_json()
        user = UserModel.find_by_email(data["email"])

        if user and check_password_hash(user.password, data["password"]):
            if user.is_active:
                access_token = create_access_token(
                    identity=user.username, fresh=True
                )
                refresh_token = create_refresh_token(identity=user.username)
                # username 에 맞는 refresh token 이 테이블에 존재하면 업데이트, 존재하지 않으면 저장
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
            return {"message": "이메일 인증이 되지 않은 계정입니다."}, 400

        return {"unauthorized": "이메일과 비밀번호를 확인하세요."}, 401


class RefreshToken(MethodView):
    """
    Refresh Token 을 받아 검증하고,
    새로운 Refresh Token, Access token 을 발급합니다.
    Refresh Token 은 일회용이므로, 새로운 Refresh Token 이 발급되면
    데이터베이스에 그 값을 저장합니다.
    """

    @jwt_required(refresh=True)
    def post(self):
        """
        -> refresh token 은 이미 검증된 상태라고 가정 (틀린 토큰, 만료된 토큰 X)
        -> 해당 유저가 데이터베이스에서 가지고 있는 refresh token 과 요청으로 들어온 refresh token이 다르다면,
        -> access token 발급은 실패해야 함
        """
        identity = get_jwt_identity()
        token = dict(request.headers)["Authorization"][7:]
        user = RefreshTokenModel.get_user_by_token(token)
        if not user:
            return {"unauthorized": "Refresh Token은 2회 이상 사용될 수 없습니다."}, 401
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
    def post(self):
        data = request.get_json()
        validate_result = register_schema.validate(data)
        if validate_result:
            return validate_result, 400
        else:
            if UserModel.find_by_email(data["email"]):
                return {"Bad Request": "중복된 이메일입니다."}, 400
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
            return {"Success": f"{user.username} 님, 가입을 환영합니다!"}, 201


class UserConfirm(Resource):
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
            return redirect("lms.induk.ac.kr")
        user.is_active = True
        user.save_to_db()
        return redirect("https://money-for-rabbit.netlify.app/signup/done")
