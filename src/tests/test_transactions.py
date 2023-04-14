from copy import copy

from tests.conftest import get_results
from tests.util import mask_values


class TestTransactions:
    masks = [
        ('id', '<<id>>'),
        ('fileId', '<<fileId>>'),
        ('transactionId', '<<transactionId>>'),
        ('userId', '<<userId>>'),
        ('createdAt', '<<createdAt>>'),
        ('approverId', '<<approverId>>'),
        ('approvedAt', '<<approvedAt>>'),
    ]
    change_masks = [('id', '<<changeId>>')]

    @classmethod
    def _add_transaction(cls, client, file_id):
        transaction_data = {
            'fileId': file_id,
            'changes': [
                {
                    'changeType': 'create',
                    'rowNumber': '6',
                    'after': {
                        'Age': '40',
                        'Average': None,
                        'Date Entered': '14/04/2023',
                        'First Name': 'Steve',
                        'Intelligence': '85',
                        'Last Name': 'Rogers',
                        'Speed': '75',
                        'Strength': '90'
                    },
                    'before': None
                }
            ]
        }
        response = client.post("/transactions", json=transaction_data)
        assert response.status_code == 200
        return response.json

    def test_get_transactions(self, client, test_file):
        response = client.get("/transactions", query_string={'fileId': test_file['id']})
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 0

        file_id = test_file['id']
        transaction = self._add_transaction(client, file_id)
        transaction_id = transaction['id']

        response = client.get("/transactions", query_string={'fileId': file_id})
        assert response.status_code == 200

        masked_response = [mask_values(item, self.masks) for item in response.json]
        for mr in masked_response:
            mr['changes'] = [mask_values(c, self.change_masks) for c in mr['changes']]

        assert masked_response == [
            get_results('transaction.json')
        ]

        response = client.get("/transactions", query_string={'fileId': file_id, 'id': transaction_id})
        assert response.status_code == 200
        assert isinstance(response.json, dict)
        masked_response = mask_values(response.json, self.masks)
        masked_response['changes'] = [mask_values(c, self.change_masks) for c in masked_response['changes']]
        assert masked_response == get_results('transaction.json')

        response = client.get("/lookups", query_string={'id': transaction_id})
        assert response.status_code == 400
        assert response.json == {
            'message': 'file id not found in request'
        }

    def test_add_transaction(self, client, test_file, mock_open_close_excel):
        transaction_data = {
            'fileId': test_file['id'],
            'changes': [
                {
                    'changeType': 'create',
                    'rowNumber': '6',
                    'after': {
                        'Age': '40',
                        'Average': None,
                        'Date Entered': '14/04/2023',
                        'First Name': 'Steve',
                        'Intelligence': '85',
                        'Last Name': 'Rogers',
                        'Speed': '75',
                        'Strength': '90'
                    },
                    'before': None
                }
            ]
        }
        response = client.post("/transactions", json=transaction_data)
        assert response.status_code == 200
        masked_response = mask_values(response.json, self.masks)
        masked_response['changes'] = [mask_values(c, self.change_masks) for c in masked_response['changes']]
        assert masked_response == get_results('transaction.json')

        # when transaction is approved, 'file_data.apply_changes' is called which in turn calls 'open_close_excel'
        mock_open_close_excel.assert_called_once()

        invalid_data = copy(transaction_data)
        invalid_data.pop('fileId')
        response = client.post("/transactions", json=invalid_data)
        assert response.status_code == 400
        assert response.json == {'message': 'file id not found in request'}

        invalid_data = copy(transaction_data)
        invalid_data.pop('changes')
        response = client.post("/transactions", json=invalid_data)
        assert response.status_code == 400
        assert response.json == {'message': 'changes not found in request'}

    def test_update_transactions(self, client, test_file, mock_open_close_excel):
        transaction = self._add_transaction(client, test_file['id'])
        transaction_id = transaction['id']

        update_data = {
            'fileId': test_file['id'],
            'status': 'APPROVED',
            'notes': 'Test',
        }

        response = client.put("/transactions", query_string={'id': transaction_id}, json=update_data)
        assert response.status_code == 200
        masked_response = mask_values(response.json, self.masks)
        masked_response['changes'] = [mask_values(c, self.change_masks) for c in masked_response['changes']]
        expected_results = get_results('transaction.json')
        expected_results['notes'] = 'Test'
        expected_results['status'] = 'APPROVED'
        assert masked_response == expected_results

        # when transaction is approved, 'file_data.apply_changes' is called which in turn calls 'open_close_excel'
        mock_open_close_excel.assert_called()

        response = client.put("/transactions", json=update_data)
        assert response.status_code == 400
        assert response.json == {'message': 'id not found in request'}

        invalid_data = copy(update_data)
        invalid_data.pop('fileId')
        response = client.put("/transactions", query_string={'id': transaction_id}, json=invalid_data)
        assert response.status_code == 400
        assert response.json == {'message': 'file id not found in request'}

        invalid_data = copy(update_data)
        invalid_data.pop('status')
        response = client.put("/transactions", query_string={'id': transaction_id}, json=invalid_data)
        assert response.status_code == 400
        assert response.json == {'message': 'status not found in request'}

    def test_delete_transactions(self, client, test_file):
        transaction = self._add_transaction(client, test_file['id'])
        transaction_id = transaction['id']

        response = client.delete("/transactions", query_string={'id': transaction_id})
        assert response.status_code == 200
        assert response.json == {'success': True}
