"""
테스트 목록

- 쪽지 목록 조회
- 쪽지 상세 조회
- 쪽지 생성
"""
from api import MessageModel, UserModel
from api.tests import CommonTestCaseSetting


class MessageTest(CommonTestCaseSetting):
    def setUp(self):
        super().setUp()
        with self.client.application.app_context():
            UserModel(
                username="미미",
                password="1234",
                email="meme@naver.com",
                email_confrimed=True,
            ).create_user()
            # 테스트를 위한 사용자 "미미" 생성, id = 1
            UserModel(
                username="민수",
                password="1234",
                email="minsu@naver.com",
                email_confirmed=True,
            ).create_user()
            # 테스트를 위한 사용자 "민수" 생성, id = 2
            MessageModel(
                user_id=1,
                author_id=2,
                message="새해 복 많이 받아.",
                amount=1000,
                is_moneybag=True,
            )
