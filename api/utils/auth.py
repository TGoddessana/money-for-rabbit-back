from flask_jwt_extended import create_access_token, create_refresh_token


def create_username_access_token(user):
    return create_access_token(
        additional_claims={"username": user.username},
        identity=user.id,
        fresh=True,
    )


def create_userid_refresh_token(user):
    return create_refresh_token(
        identity=user.id,
    )
