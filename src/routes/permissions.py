from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from context import current_user_id
from decorators import jwt_user_required
from error import BadRequestError, NotFoundError
from services import PermissionService, UserService

permissions = Blueprint('permissions', __name__, url_prefix='/permissions')


@permissions.get("/user")
@jwt_user_required()
def get_current_user_permissions():
    """Get the current (requesting) user permissions or one or all files"""
    user_id = current_user_id.get()
    file_id = request.args.get('fileId')
    if file_id:
        return PermissionService.get(file_id=file_id, user_id=user_id)
    else:
        return PermissionService.list(user_id=user_id)


@permissions.get("")
@jwt_required()
def get_permissions():
    """Get all permissions for a particular file or user other than the requesting user"""
    file_id = request.args.get('fileId')
    user_id = request.args.get('userId')
    if not file_id and not user_id:
        raise BadRequestError(message='user id or file id found in request')

    permissions_ = PermissionService.list(file_id, user_id)
    return jsonify(permissions_)


@permissions.post("")
@jwt_required()
def add_permission():
    file_id = request.json.get('fileId')
    email = request.json.get('email')
    role = request.json.get('role')
    if any(param is None for param in [file_id, email, role]):
        raise BadRequestError('file id, email and role expected to add permission')
    user = UserService.get(email=email)
    if not user:
        raise NotFoundError('User is not recognised')

    return PermissionService.create(file_id=file_id, user_id=user.id, role=role)


@permissions.put("")
@jwt_required()
def update_permission():
    permission_id = request.json.get('id')
    if not permission_id:
        raise BadRequestError(message='id not found in request')

    role = request.json.get('role')
    return PermissionService.update(permission_id, role)


@permissions.delete("")
@jwt_required()
def delete_permission():
    permission_id = request.args.get('id')
    if not permission_id:
        raise BadRequestError(message='id not found in request')

    success = PermissionService.delete(id_=permission_id)
    return {'success': success}
