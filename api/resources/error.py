from flask import current_app, jsonify
from flask_jwt_extended import JWTManager
from marshmallow import ValidationError

with current_app.app_context():
    jwt = JWTManager(current_app)

    @current_app.errorhandler(ValidationError)
    def handle_marshmallow_validation(err):
        return jsonify(err.messages), 400

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"error": "토큰이 만료되었습니다."}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({"error": "잘못된 토큰입니다."}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "error": "토큰 정보가 필요합니다.",
                }
            ),
            401,
        )
