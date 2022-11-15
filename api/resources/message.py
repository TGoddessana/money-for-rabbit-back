from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.schemas.message import MessageSchema
from api.models.message import MessageModel
from api.models.user import UserModel


message_detail_schema = MessageSchema()
message_list_schema = MessageSchema(many=True)


class MessageDetail(Resource):
    """
    쪽지 상세 조회
    """


class MessageList(Resource):
    """
    쪽지 목록 조회

    새로운 쪽지 추가하기 위해서는 로그인 처리 필요
    """

    @classmethod
    def get(cls, user_id):
        """
        #TODO : 6개 페이지네이션, 최신순 정렬
        유저를 특정한 다음, 해당 유저가 가지고 있는 모든 쪽지들의 목록을 나타냅니다.
        """
        # 먼저 유저를 특정
        user = UserModel.find_by_id(user_id)

        # 해당 유저가 가지고 있는 쪽지들
        messages = UserModel.message_set

        page = request.args.get("page", type=int, default=1)
        orderd_messages = MessageModel.query.order_by(MessageModel.id.desc())
        pagination = orderd_messages.paginate(
            page, per_page=10, error_out=False
        )
        result = message_list_schema.dump(pagination.items)
        return result

    @classmethod
    @jwt_required()
    def post(cls, user_id):
        """
        특정 유저에게 새로운 쪽지를 생성
        """
        user = UserModel.find_by_id(user_id)
