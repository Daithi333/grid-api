import traceback
from typing import List

from database import db_session
from database.models import Transaction, Change
from enums import ChangeType, ApprovalStatus
from error import NotFoundError, BadRequestError
from services import FileDataService


class TransactionService:
    @classmethod
    def get(cls, id_: str, internal: bool = False) -> Transaction or dict:
        session = db_session.get()
        transaction = session.query(Transaction).filter_by(id=id_).one_or_none()
        if not transaction:
            raise NotFoundError(message=f'File {id_} not found')

        return transaction if internal else cls._transaction_to_dict(transaction)

    @classmethod
    def list(cls, file_id: str) -> List[dict]:
        session = db_session.get()
        transactions = session.query(Transaction).filter_by(file_id=file_id).all()
        return [cls._transaction_to_dict(t) for t in transactions]

    @classmethod
    def create(cls, file_id: str, user_id: str, changes_data: dict) -> dict:
        session = db_session.get()
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

        session.add(transaction)
        session.commit()
        session.refresh(transaction)
        return cls._transaction_to_dict(transaction)

    @classmethod
    def update(cls, id_: str, status: str, notes: str = None):
        session = db_session.get()
        transaction = cls.get(id_=id_, internal=True)

        transaction.status = ApprovalStatus[status]
        if transaction.status == ApprovalStatus.APPROVED:
            try:
                FileDataService.apply_changes(transaction.file, transaction.changes)
            except Exception as e:
                traceback.print_exc()
                raise BadRequestError(f'unable to apply changes in transaction {id_}: {e}')

            transaction.approver_id = '2'

        if notes:
            transaction.notes = notes

        session.commit()
        return cls._transaction_to_dict(transaction)

    @classmethod
    def delete(cls, id_: str) -> bool:
        session = db_session.get()
        transaction = cls.get(id_=id_, internal=True)
        session.delete(transaction)
        session.commit()
        return True

    @classmethod
    def _transaction_to_dict(cls, transaction: Transaction) -> dict:
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
