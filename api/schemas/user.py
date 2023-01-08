from marshmallow import fields
from api.ma import ma
from api.models.user import UserModel

fields.Field.default_error_messages["required"] = "해당 필드를 입력해 주세요."
fields.Field.default_error_messages["validator_failed"] = "해당 필드에 대한 검증이 실패했습니다."
fields.Field.default_error_messages["null"] = "해당 필드는 null 이 될 수 없습니다."


class UserInformationSchema(ma.SQLAlchemyAutoSchema):
    total_amount = fields.Method("get_total_amount")

    class Meta:
        load_instance = True
        model = UserModel
        exclude = [
            "id",
            "email",
            "password",
            "is_active",
            "date_joined",
        ]

    def get_total_amount(self, obj):
        return obj.total_amount


class UserRegisterSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        load_instance = True
        model = UserModel
        load_only = [
            "username",
            "email",
            "password",
        ]
        dump_only = ["activated"]


class UserWithdrawSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        load_instance = True
        model = UserModel
        load_only = ["username"]
        exclude = [
            "id",
            "email",
            "password",
            "is_active",
            "date_joined",
        ]


class UserLoginSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        load_instance = True
        model = UserModel
        load_only = ["email", "password"]
        exclude = [
            "id",
            "username",
            "is_active",
            "date_joined",
        ]
