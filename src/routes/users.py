import base64
from datetime import timedelta

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, decode_token

from config import Config
from error import BadRequestError, UnauthorizedError
from services import UserService

users = Blueprint('users', __name__, url_prefix='/users')


@users.route("/signup", methods=["POST"])
def signup():
    email = request.form.get('email')
    password = request.form.get('password')
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')

    if any(param is None for param in [email, password, firstname, lastname]):
        raise BadRequestError('missing fields for signup')

    return UserService.signup(email, password, firstname, lastname)


@users.route("/login", methods=["POST"])
def login():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        raise UnauthorizedError('Authorization header missing')

    auth_token = auth_header.split(' ')[1]
    auth_bytes = base64.b64decode(auth_token.encode('utf-8'))
    auth_str = auth_bytes.decode('utf-8')
    email, password = auth_str.split(':')
    user = UserService.login(email, password)

    expires_delta = timedelta(hours=Config.JWT_ACCESS_TOKEN_EXPIRES)
    access_token = create_access_token(identity=user, expires_delta=expires_delta)
    refresh_token = create_refresh_token(identity=user)

    decoded_token = decode_token(access_token)
    expiration_time = decoded_token["exp"] * 1000

    return jsonify(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expiration_time,
        user=user
    )


@users.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    expires_delta = timedelta(hours=Config.JWT_ACCESS_TOKEN_EXPIRES)
    access_token = create_access_token(identity=identity, expires_delta=expires_delta)

    decoded_token = decode_token(access_token)
    expiration_time = decoded_token["exp"] * 1000

    return jsonify(access_token=access_token, expires_at=expiration_time)
