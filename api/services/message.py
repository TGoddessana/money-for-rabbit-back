from flask import request
from flask_jwt_extended import get_jwt_identity

from api import UserModel, MessageModel
from api.utils.korean_datetime import get_korean_datetime, MESSAGE_OPEN_DATETIME
from api.utils.response import get_response, NOT_FOUND, INTERNAL_SERVER_ERROR

from api.schemas.message import MessageSchema


class MessageService:
    """
    쪽지
        - 작성
        - 상세 조회
        - 목록 조회
    """

    def detail_view(self, user_id, message_id):
        if get_korean_datetime() > MESSAGE_OPEN_DATETIME:
            user = UserModel.find_by_id(user_id)
            message = MessageModel.find_by_id(message_id)
            if not user:
                return get_response(False, NOT_FOUND.format("사용자"), 404)
            if message:
                return MessageSchema().dump(message), 200
            return get_response(False, NOT_FOUND.format("쪽지"), 404)
        return get_response(False, "쪽지는 22일 이후에만 조회할 수 있습니다.", 400)

    def list_view(self, user_id):
        if get_korean_datetime() > MESSAGE_OPEN_DATETIME:
            user = UserModel.find_by_id(user_id)
            if not user:
                return get_response(False, NOT_FOUND.format("사용자"), 400)
            if not user.id == get_jwt_identity():
                return get_response(False, "쪽지는 본인만 조회할 수 있습니다", 403)
            paginated_posts = user.message_set.order_by(
                MessageModel.id.desc()
            ).paginate(
                page=request.args.get("page", type=int, default=1),
                per_page=6,
                error_out=False,
            )
            next_page = (
                f"{request.base_url}?page={paginated_posts.next_num}"
                if paginated_posts.next_num
                else None
            )
            prev_page = (
                f"{request.base_url}?page={paginated_posts.prev_num}"
                if paginated_posts.prev_num
                else None
            )
            return {
                "user_info": {
                    "username": user.username,
                    "email": user.email,
                    "total_amount": user.total_amount,
                },
                "message_set_count": user.message_set_count,
                "next": next_page,
                "prev": prev_page,
                "messages": MessageSchema(many=True).dump(paginated_posts.items),
            }
        return get_response(False, "쪽지는 22일 이후에만 조회할 수 있습니다.", 400)

    def write(self, user_id):
        message_json = request.get_json()
        author = UserModel.find_by_id(get_jwt_identity())
        reader = UserModel.find_by_id(user_id)
        if not reader:
            return get_response(False, NOT_FOUND.format("사용자"), 400)
        validate_result = MessageSchema().validate(message_json)
        if validate_result:
            return get_response(False, validate_result, 400)
        new_message = MessageSchema().load(message_json)
        new_message.user_id = user_id
        new_message.author_id = author.id
        new_message.save_to_db()
        return MessageSchema().dump(new_message), 201
