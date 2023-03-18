from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from error import BadRequestError
from services import TransactionService

transactions = Blueprint('transactions', __name__, url_prefix='/transactions')


@transactions.post("")
@jwt_required()
def add_transaction():
    file_id = request.json.get('fileId')
    changes_data = request.json.get('changes', [])
    identity = get_jwt_identity()
    user_id = str(identity.get('id'))

    if not file_id:
        raise BadRequestError(message='file id not found in request')

    if not changes_data:
        raise BadRequestError(message='changes not found in request')

    return TransactionService.create(file_id, user_id, changes_data)


@transactions.get("")
@jwt_required()
def get_transactions():
    file_id = request.args.get('fileId')
    if not file_id:
        raise BadRequestError(message='file id not found in request')

    transaction_id = request.args.get('id')
    if transaction_id:
        return TransactionService.get(id_=transaction_id)
    else:
        transactions_ = TransactionService.list(file_id=file_id)
        return jsonify(transactions_)


@transactions.put("")
@jwt_required()
def update_transaction():
    transaction_id = request.args.get('id')
    if not transaction_id:
        raise BadRequestError(message='id not found in request')

    status = request.json.get('status')
    notes = request.json.get('notes')
    identity = get_jwt_identity()
    user_id = str(identity.get('id'))

    if not status:
        raise BadRequestError(message='status not found in request')

    return TransactionService.update(transaction_id, user_id, status, notes)


@transactions.delete("")
@jwt_required()
def delete_transaction():
    transaction_id = request.args.get('id')
    if not transaction_id:
        raise BadRequestError(message='id not found in request')

    success = TransactionService.delete(id_=transaction_id)
    return {'success': success}
