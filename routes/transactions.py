from flask import Blueprint, request, jsonify

from database import db
from database.models import Transaction, Change
from enums import ChangeType, ApprovalStatus

transactions = Blueprint('transactions', __name__, url_prefix='/transactions')


@transactions.post("")
def add_transaction():
    file_id = request.json.get('fileId')
    changes_data = request.json.get('changes', [])
    user_id = 1

    if not file_id:
        return {'message': 'file id not found in request'}, 400

    if not changes_data:
        return {'message': 'changes not found in request'}, 400

    changes = [
        Change(
            change_type=ChangeType(c['changeType']),
            row_number=c['rowNumber'],
            before=c.get('before'),
            after=c.get('after')
        )
        for c in changes_data
    ]
    transaction = Transaction(file_id=file_id, user_id=user_id, status=ApprovalStatus.PENDING, changes=changes)

    session = next(db.get_session())
    session.add(transaction)
    session.commit()
    session.refresh(transaction)

    return {"id": transaction.id}


@transactions.get("")
def get_transactions():
    session = next(db.get_session())
    file_id = request.args.get('fileId')
    if not file_id:
        return {'message': 'file id not found in request'}, 404

    transaction_id = request.args.get('id')

    if transaction_id:
        transaction = session.query(Transaction).filter_by(id=transaction_id).one_or_none()
        if not transaction:
            return {'message': f'transaction {transaction_id} not found'}, 404

        return _transaction_to_dict(transaction)

    else:
        transactions_ = session.query(Transaction).filter_by(file_id=file_id).all()
        return jsonify([_transaction_to_dict(t) for t in transactions_])


def _transaction_to_dict(transaction: Transaction) -> dict:
    return {
        'id': transaction.id,
        'fileId': transaction.file_id,
        'createdAt': transaction.created_at,
        'userId': transaction.user_id,
        'status': transaction.status.name,
        'notes': transaction.notes,
        'approvedAt': transaction.approved_at,
        'approverId': transaction.approver_id,
        'changes': [
            {
                'id': c.id,
                'changeType': c.change_type.value,
                'rowNumber': c.row_number,
                'before': c.before,
                'after': c.after
            }
            for c in transaction.changes
        ]
    }


@transactions.put("")
def update_transaction():
    pass


@transactions.delete("")
def delete_transaction():
    transaction_id = request.args.get('id')
    if not transaction_id:
        return {'message': 'id not found in request'}, 400

    session = next(db.get_session())
    transaction = session.query(Transaction).filter_by(id=transaction_id).one_or_none()
    if not transaction:
        return {'message': f'Transaction {transaction_id!r} not found'}, 404

    session.delete(transaction)
    session.commit()
    return {'success': True}
