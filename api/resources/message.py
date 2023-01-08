from flask import request, url_for
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from marshmallow import ValidationError

from api.models.message import MessageModel
from api.models.user import UserModel
from api.schemas.message import MessageSchema
from api.utils.response import INTERNAL_SERVER_ERROR, NOT_FOUND, get_response

message_detail_schema = MessageSchema()
message_list_schema = MessageSchema(many=True)


class MessageDetail(Resource):
    @classmethod
    def get(cls, user_id, message_id):
        """
        쪽지를 특정한 다음, 해당 쪽지의 상세내용을 조회
        """
        user = UserModel.find_by_id(user_id)
        if not user:
            return get_response(False, NOT_FOUND.format("사용자"), 404)
        message = MessageModel.find_by_id(message_id)
        if message:
            return message_detail_schema.dump(message), 200
        else:
            return get_response(False, NOT_FOUND.format("쪽지"), 404)


class MessageList(Resource):
    @classmethod
    @jwt_required()
    def get(cls, user_id):
        """
        유저를 특정한 다음, 해당 유저가 가지고 있는 모든 쪽지들의 목록을 조회
        쪽지는 요청 보낸 본인만 확인할 수 있음
        """
        user = UserModel.find_by_id(user_id)
        if user:
            if not user.id == get_jwt_identity():
                return get_response(False, "쪽지는 본인만 조회할 수 있습니다", 403)
            user.total_amount
            messages = user.message_set
            page = request.args.get("page", type=int, default=1)
            orderd_messages = messages.order_by(MessageModel.id.desc())
            pagination = orderd_messages.paginate(page, per_page=6, error_out=False)

            next = (
                f"{request.base_url}?page={pagination.next_num}"
                if pagination.next_num
                else None
            )
            prev = (
                f"{request.base_url}?page={pagination.prev_num}"
                if pagination.prev_num
                else None
            )

            return {
                "user_info": {
                    "username": user.username,
                    "email": user.email,
                    "total_amount": user.total_amount,
                },
                "next": next,
                "prev": prev,
                "messages": message_list_schema.dump(pagination.items),
            }

        else:
            return get_response(False, NOT_FOUND.format("사용자"), 400)

    @classmethod
    @jwt_required()
    def post(cls, user_id):
        """
        특정 유저에게 새로운 쪽지를 생성
        """
        message_json = request.get_json()
        user = UserModel.find_by_id(get_jwt_identity())
        if UserModel.find_by_id(user_id):
            try:
                new_message = message_detail_schema.load(message_json)
                new_message.user_id = user_id
                new_message.author_id = user.id
            except ValidationError as err:
                return err.messages, 400
            except ValueError as err:
                return get_response(False, str(err), 400)
            try:
                new_message.save_to_db()
            except:
                return get_response(False, INTERNAL_SERVER_ERROR, 500)
            return message_detail_schema.dump(new_message), 201
        else:
            return get_response(False, NOT_FOUND.format("사용자"), 400)
