from marshmallow import fields

from api.ma import ma
from api.models.message import MessageModel

fields.Field.default_error_messages["required"] = "해당 필드를 입력해 주세요."
fields.Field.default_error_messages[
    "validator_failed"
] = "해당 필드에 대한 검증이 실패했습니다."
fields.Field.default_error_messages["null"] = "해당 필드는 null 이 될 수 없습니다."


class MessageSchema(ma.SQLAlchemyAutoSchema):
    image_name = fields.Method("get_money_image_name")
    author_name = fields.Method("get_message_author_name")

    class Meta:
        load_instance = True
        model = MessageModel
        # 쓰기 전용
        load_only = ["password", "author_id"]

    def get_message_author_name(self, obj):
        return obj.author.username

    def get_money_image_name(self, obj):
        return obj.money_image_name
