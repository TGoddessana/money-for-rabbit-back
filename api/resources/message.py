from flask_jwt_extended import jwt_required
from flask_restful import Resource

from api.services.message import MessageService


class MessageDetail(Resource):
    @classmethod
    def get(cls, user_id, message_id):
        """
        쪽지를 특정한 다음, 해당 쪽지의 상세내용을 조회
        """
        return MessageService().detail_view(user_id=user_id, message_id=message_id)


class MessageList(Resource):
    @classmethod
    @jwt_required()
    def get(cls, user_id):
        """
        유저를 특정한 다음, 해당 유저가 가지고 있는 모든 쪽지들의 목록을 조회
        """
        return MessageService().list_view(user_id=user_id)

    @classmethod
    @jwt_required()
    def post(cls, user_id):
        """
        특정 유저에게 새로운 쪽지를 생성
        """
        return MessageService().write(user_id=user_id)
