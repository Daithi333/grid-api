from tests.conftest import get_results


class TestFileData:

    def test_get_file_data(self, client, test_file):
        response = client.get("/files/data", query_string={'id': test_file['id']})
        assert response.status_code == 200
        assert response.json == get_results('file_data.json')

        response = client.get("/files/data")
        assert response.status_code == 400
        assert response.json == {
            'message': "id not found in request"
        }

    def test_file_data_changes(self, client, test_file):
        create_row_transaction = {
            'fileId': test_file['id'],
            'changes': [
                {
                    'changeType': 'create',
                    'rowNumber': '5',
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
        response = client.post("/transactions", json=create_row_transaction)
        assert response.status_code == 200

        response = client.get("/files/data", query_string={'id': test_file['id']})
        assert response.status_code == 200
        assert response.json == get_results('file_data_new_row.json')

        update_row_transaction = {
            'fileId': test_file['id'],
            'changes': [
                {
                    'changeType': 'update',
                    'rowNumber': '5',
                    'after': {
                        'Age': '43',
                        'Average': None,
                        'Date Entered': '15/04/2023',
                        'First Name': 'Steve',
                        'Intelligence': '80',
                        'Last Name': 'Rogers',
                        'Speed': '70',
                        'Strength': '85'
                    },
                    'before': {
                        'Age': '40',
                        'Average': None,
                        'Date Entered': '14/04/2023',
                        'First Name': 'Steve',
                        'Intelligence': '85',
                        'Last Name': 'Rogers',
                        'Speed': '75',
                        'Strength': '90'
                    }
                }
            ]
        }
        response = client.post("/transactions", json=update_row_transaction)
        assert response.status_code == 200

        response = client.get("/files/data", query_string={'id': test_file['id']})
        assert response.status_code == 200
        assert response.json == get_results('file_data_update_row.json')

        delete_row_transaction = {
            'fileId': test_file['id'],
            'changes': [
                {
                    'changeType': 'delete',
                    'rowNumber': '5',
                    'after': None,
                    'before': {
                        'Age': '43',
                        'Average': None,
                        'Date Entered': '15/04/2023',
                        'First Name': 'Steve',
                        'Intelligence': '80',
                        'Last Name': 'Rogers',
                        'Speed': '70',
                        'Strength': '85'
                    }
                }
            ]
        }
        response = client.post("/transactions", json=delete_row_transaction)
        assert response.status_code == 200

        response = client.get("/files/data", query_string={'id': test_file['id']})
        assert response.status_code == 200
        assert response.json == get_results('file_data_delete_row.json')

        multi_row_transaction = {
            'fileId': test_file['id'],
            'changes': [
                {
                    'changeType': 'create',
                    'rowNumber': '5',
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
                },
                {
                    'changeType': 'update',
                    'rowNumber': '1',
                    'after': {
                        'Age': '47',
                        'Average': None,
                        'Date Entered': '14/04/2023',
                        'First Name': 'Bruce',
                        'Intelligence': '85',
                        'Last Name': 'Banner',
                        'Speed': '55',
                        'Strength': '95'
                    },
                    'before': {
                        'Age': '45',
                        'Average': None,
                        'Date Entered': '14/01/2023',
                        'First Name': 'Bruce',
                        'Intelligence': '80',
                        'Last Name': 'Banner',
                        'Speed': '50',
                        'Strength': '99'
                    }
                },
                {
                    'changeType': 'delete',
                    'rowNumber': '2',
                    'after': None,
                    'before': {
                        'Age': '28',
                        'Average': None,
                        'Date Entered': '14/01/2023',
                        'First Name': 'Peter',
                        'Intelligence': '70',
                        'Last Name': 'Parker',
                        'Speed': '75',
                        'Strength': '70'
                    }
                }
            ]
        }
        response = client.post("/transactions", json=multi_row_transaction)
        assert response.status_code == 200

        response = client.get("/files/data", query_string={'id': test_file['id']})
        assert response.status_code == 200
        assert response.json == get_results('file_data_multi_row.json')
