from . import CommonTestCaseSetting
from api.models.user import UserModel
from api.utils.auth import create_username_access_token
import json
from flask_jwt_extended import create_access_token, decode_token


class MyPageTest(CommonTestCaseSetting):
    """사용자 정보조회 및 수정을 테스트합니다."""

    def setUp(self):
        super().setUp()
        with self.client.application.app_context():
            UserModel(
                username="미미",
                password="1234",
                email="meme@naver.com",
                is_active=True,
            ).save_to_db()
            # 테스트를 위한 사용자 "미미" 생성, id = 1
            UserModel(
                username="민수", password="1234", email="minsu@naver.com", is_active=True
            ).save_to_db()
            # 테스트를 위한 사용자 "민수" 생성, id = 2

    def test_get_not_exist_user_information_should_404(self):
        """
        존재하지 않는 사용자의 정보를 조회하려고 한다면,
            - 서버는 상태 코드 404로 응답해야 합니다.
            - 적절한 에러 메시지를 반환해야 합니다.
        """
        response = self.client.get(self.url + "/api/user/3")
        self.assertEqual(404, response.status_code)
        self.assertEqual(response.get_json(), {"error": "사용자를 찾을 수 없습니다."})

    def test_get_exist_user_information_should_200(self):
        """
        존재하는 사용자의 정보를 조회하려고 한다면, 맞는 정보와 상태 코드 200을 응답해야 합니다.
        """
        response = self.client.get(self.url + "/api/user/1")  # 미미
        self.assertEqual(200, response.status_code)
        self.assertEqual(
            response.get_json(), {"user_info": {"total_amount": 0, "username": "미미"}}
        )

    def test_put_user_information_should_403(self):
        """
        본인이 아니라 다른 사람의 정보를 수정하려고 한다면, 적절한 에러 메시지와 403 상태 코드를 응답해야 합니다.
        """
        with self.client.application.app_context():
            user_미미 = UserModel.find_by_id(1)
            user_민수 = UserModel.find_by_id(2)
            # 민수의 액세스 토큰 발급
            access_token = create_access_token(
                identity=user_민수.id,
                fresh=True,
            )
        # 민수의 토큰으로 미미의 정보 수정 요청
        response = self.client.put(
            self.url + "/api/user/1",
            content_type="application/json",
            data=json.dumps({"username": "미미미"}),
            headers={"Authorization": "Bearer " + access_token},
        )
        self.assertEqual(403, response.status_code)
        self.assertEqual(response.get_json(), {"error": "권한이 없습니다."})

    def test_put_user_information_should_200(self):
        """
        본인이 본인의 사용자 정보를 수정하려고 한다면, 수정이 잘 되어야 합니다.
        """
        with self.client.application.app_context():
            user_민수 = UserModel.find_by_id(2)
            # 민수의 액세스 토큰 발급
            access_token = create_access_token(
                identity=user_민수.id,
                fresh=True,
            )
            # 민수가 본인의 정보 수정 요청
            response = self.client.put(
                self.url + "/api/user/2",
                content_type="application/json",
                data=json.dumps({"username": "민수민수"}),
                headers={"Authorization": "Bearer " + access_token},
            )
            self.assertEqual(200, response.status_code)
            self.assertEqual(response.get_json(), {"success": "닉네임이 민수민수 으로 변경되었습니다."})
            self.assertEqual(UserModel.find_by_id(2).username, "민수민수")


class WithdrawTest(CommonTestCaseSetting):
    def setUp(self):
        super().setUp()
        with self.client.application.app_context():
            UserModel(
                username="미미",
                password="1234",
                email="meme@naver.com",
                is_active=True,
            ).save_to_db()
            # 테스트를 위한 사용자 "미미" 생성, id = 1
            UserModel(
                username="민수", password="1234", email="minsu@naver.com", is_active=True
            ).save_to_db()
            # 테스트를 위한 사용자 "민수" 생성, id = 2

    def test_withdraw_request_with_invalid_data_should_400(self):
        """적절하지 않은 데이터와 함께 회원탈퇴 요청을 보내면, 실패해야 합니다."""
        with self.client.application.app_context():
            response = self.client.delete(
                self.url + "/api/user/withdraw",
                content_type="application/json",
                data=json.dumps({"username": "마마"}),
                headers={
                    "Authorization": "Bearer "
                    + create_username_access_token(UserModel.find_by_id(1))
                },
            )
        self.assertEqual(400, response.status_code)

    def test_minsu_requests_withdraw_meme_should_400(self):
        """민수가 미미 사용자에 대한 회원탈퇴 요청을 보내면, 실패해야 합니다."""
        with self.client.application.app_context():
            response = self.client.delete(
                self.url + "/api/user/withdraw",
                content_type="application/json",
                data=json.dumps({"username": "미미"}),
                headers={
                    "Authorization": "Bearer "
                    + create_username_access_token(UserModel.find_by_id(2))
                },
            )
        self.assertEqual(400, response.status_code)

    def test_meme_requests_withdraw_meme_should_204(self):
        """
        미미가 미미 사용자에 대한 회원탈퇴 요청을 보내면, 성공해야 합니다.
        데이터베이스에 2명의 사용자가 있었으므로,
        회원탈퇴 진행 후에는 1명의 사용자만 남아있어야 합니다.
        """
        with self.client.application.app_context():
            response = self.client.delete(
                self.url + "/api/user/withdraw",
                content_type="application/json",
                data=json.dumps({"username": "미미"}),
                headers={
                    "Authorization": "Bearer "
                    + create_username_access_token(UserModel.find_by_id(1))
                },
            )
            self.assertEqual(204, response.status_code)
            self.assertEqual(len(UserModel.query.all()), 1)


class RegisterTest(CommonTestCaseSetting):
    """회원가입을 테스트합니다."""

    def test_invalid_email_data_should_400(self):
        """
        사용자가 이메일을 이상한 형식으로 보내왔을 때, 서버는 400 상태 코드로 응답해야 합니다.
        """
        data_from_client = json.dumps(
            {
                "username": "some_username",
                "email": "some_invalid_email_value",
                "password": "SomeVali@123",
            }
        )
        response = self.client.post(
            self.url + "/api/user/register",
            content_type="application/json",
            data=data_from_client,
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(response.get_json(), {"error": "유효한 이메일 값이 아닙니다."})

    def test_invalid_password_data_should_400(self):
        """
        사용자가 알맞지 않은 비밀번호 값을 보내온다면, 서버는 400 상태 코드로 응답해야 합니다.
        """
        data_from_client = json.dumps(
            {
                "username": "some_username",
                "email": "logical_man@naver.com",
                "password": "some_invalid_password_value",
            }
        )
        response = self.client.post(
            self.url + "/api/user/register",
            content_type="application/json",
            data=data_from_client,
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(response.get_json(), {"error": "유효한 비밀번호 값이 아닙니다."})

    def test_valid_register_should_201(self):

        """
        정상적인 데이터와 함께 회원가입이 진행되었다면,
        서버는 사용자에게 확인 이메일을 보내고
        is_active 필드가 False 인 채로 저장해야 합니다.
        201 상태 코드와 적절한 성공 메시지를 응답해야 합니다.
        """
        with self.client.application.app_context():
            data_from_client = json.dumps(
                {
                    "username": "some_username",
                    "email": "logical_man@naver.com",
                    "password": "SomeVali@123",
                }
            )
            response = self.client.post(
                self.url + "/api/user/register",
                content_type="application/json",
                data=data_from_client,
            )
            self.assertEqual(201, response.status_code)
            self.assertEqual(
                response.get_json(), {"success": "some_username 님, 회원가입을 환영합니다!"}
            )


class LoginTest(CommonTestCaseSetting):
    """access, refresh token 발행 및 refresh token rotation 을 테스트합니다."""

    def setUp(self):
        super().setUp()
        with self.client.application.app_context():
            UserModel(
                username="미미",
                password="1234",
                email="meme@naver.com",
                is_active=True,
            ).create_user()
            # 테스트를 위한 사용자 "미미" 생성, id = 1
            UserModel(
                username="민수", password="1234", email="minsu@naver.com", is_active=True
            ).create_user()
            # 테스트를 위한 사용자 "민수" 생성, id = 2

    def test_not_matching_information_login_should_401(self):
        """알맞지 않은 정보로 로그인을 시도하면, 401 상태 코드를 응답해야 합니다."""
        response = self.client.post(
            self.url + "/api/user/login",
            content_type="application/json",
            data=json.dumps({"email": "meme@naver.com", "password": "틀린 비밀번호"}),
        )
        self.assertEqual(response.get_json(), {"error": "이메일과 비밀번호를 확인하세요."})
        self.assertEqual(401, response.status_code)

    def test_mathing_information_login_should_200(self):
        """
        알맞는 정보로 로그인을 시도하면,
        - 서버는 username이 포함되어 있는 액세스 토큰과 리프레시 토큰을 상태 코드 200과 함께 응답해야 합니다.
        """
        response = self.client.post(
            self.url + "/api/user/login",
            content_type="application/json",
            data=json.dumps({"email": "meme@naver.com", "password": "1234"}),
        )
        self.assertIn("access_token", response.get_json())
        self.assertIn("refresh_token", response.get_json())
        self.assertEqual(200, response.status_code)

    def test_username_exists_access_token(self):
        """액세스 토큰에는 username이 들어가 있어야 합니다."""
        response = self.client.post(
            self.url + "/api/user/login",
            content_type="application/json",
            data=json.dumps({"email": "meme@naver.com", "password": "1234"}),
        )
        with self.client.application.app_context():
            decoded_token = decode_token(response.get_json()["access_token"])
            self.assertIn("username", decoded_token.keys())
            self.assertEqual("미미", decoded_token["username"])

    def test_username_exists_login_refresh_token(self):
        """
        리프레시 토큰으로 받아온 액세스 토큰에서도,
        username 이 들어있어야 합니다.
        """
        refresh_token = (
            self.client.post(
                self.url + "/api/user/login",
                content_type="application/json",
                data=json.dumps({"email": "meme@naver.com", "password": "1234"}),
            )
            .get_json()
            .get("refresh_token")
        )
        response = self.client.post(
            self.url + "/api/user/refresh",
            content_type="application/json",
            headers={"Authorization": "Bearer " + refresh_token},
        )
        with self.client.application.app_context():
            decoded_token = decode_token(response.get_json()["access_token"])
            self.assertIn("username", decoded_token.keys())
            self.assertEqual("미미", decoded_token["username"])

    def test_refresh_token_rotation_should_401(self):
        """
        이미 사용된 리프레시 토큰으로 리프레시 요청을 보내면,
        서버는 상태 코드 401과 함께 적절한 에러 메시지를 응답해야 합니다.
        """
        refresh_token = (
            self.client.post(
                self.url + "/api/user/login",
                content_type="application/json",
                data=json.dumps({"email": "meme@naver.com", "password": "1234"}),
            )
            .get_json()
            .get("refresh_token")
        )
        first_response = self.client.post(
            self.url + "/api/user/refresh",
            content_type="application/json",
            headers={"Authorization": "Bearer " + refresh_token},
        )
        second_response = self.client.post(
            self.url + "/api/user/refresh",
            content_type="application/json",
            headers={"Authorization": "Bearer " + refresh_token},
        )
        self.assertEqual(401, second_response.status_code)
        self.assertEqual(
            second_response.get_json(), {"error": "refresh token 은 2회 이상 사용될 수 없습니다."}
        )
