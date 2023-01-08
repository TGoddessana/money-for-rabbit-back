from . import CommonTestCaseSetting
from api.models.user import UserModel
import json
from flask_jwt_extended import create_access_token


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
