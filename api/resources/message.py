from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.schemas.message import MessageSchema
from api.models.message import MessageModel
from api.models.user import UserModel
from marshmallow import ValidationError


message_detail_schema = MessageSchema()
message_list_schema = MessageSchema(many=True)


class MessageDetail(Resource):
    """
    쪽지 상세 조회
    """

    @classmethod
    def get(cls, user_id, message_id):
        """
        쪽지를 특정한 다음, 해당 쪽지의 상세내용을 조회
        """
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"Error": "사용자를 찾을 수 없습니다."}
        message = MessageModel.find_by_id(message_id)
        if message:
            return message_detail_schema.dump(message), 200
        else:
            return {"Error": "쪽지를 찾을 수 없습니다."}, 404


class MessageList(Resource):
    @classmethod
    def get(cls, user_id):
        """
        유저를 특정한 다음, 해당 유저가 가지고 있는 모든 쪽지들의 목록을 나타냅니다.
        """
        # 먼저 유저를 특정
        user = UserModel.find_by_id(user_id)

        if user:
            # 해당 유저가 가지고 있는 쪽지들
            messages = user.message_set

            page = request.args.get("page", type=int, default=1)
            orderd_messages = messages.order_by(MessageModel.id.desc())
            pagination = orderd_messages.paginate(
                page, per_page=6, error_out=False
            )
            result = message_list_schema.dump(pagination.items)
            return result
        else:
            return {"Error": "존재하지 않는 사용자입니다."}, 404

    @classmethod
    @jwt_required()
    def post(cls, user_id):
        """
        특정 유저에게 새로운 쪽지를 생성
        """
        message_json = request.get_json()
        user = UserModel.find_by_username(get_jwt_identity())
        if UserModel.find_by_id(user_id):
            try:
                new_message = message_detail_schema.load(message_json)
                new_message.user_id = user_id
                new_message.author_id = user.id
            except ValidationError as err:
                return err.messages, 400
            except ValueError as err:
                return {"Error": str(err)}, 400
            try:
                new_message.save_to_db()
            except:
                return {"Error": "저장에 실패하였습니다."}, 500
            return message_detail_schema.dump(new_message), 201
        else:
            return {"Error": "존재하지 않는 사용자입니다."}, 404


class AdminMessageList(Resource):
    @classmethod
    def get(cls):
        return message_list_schema.dump(MessageModel.find_all())
