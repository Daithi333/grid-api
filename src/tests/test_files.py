from io import BytesIO

from tests.conftest import get_results, get_file_bytes, TEST_EXCEL, TEST_TXT
from tests.util import mask_values


class TestFiles:

    def test_get_files(self, client, test_file, mock_jwt_functions):
        response = client.get("/files")
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 1
        masks = [('id', '<<id>>')]
        masked_response = [mask_values(item, masks) for item in response.json]
        assert masked_response == [
            {
                'id': '<<id>>',
                'name': 'test.xlsx',
                'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'size_bytes ': 9429
            }
        ]

        response = client.get("/files", query_string={'id': test_file['id']})
        assert response.status_code == 200
        assert isinstance(response.json, dict)
        masked_response = mask_values(response.json, masks)
        assert masked_response == {
            'id': '<<id>>',
            'name': 'test.xlsx',
            'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'size_bytes ': 9429
        }

        response = client.get("/files", query_string={'id': 'invalid'})
        # enforce permission decorator intercepts this. Perhaps should check existence first..
        assert response.status_code == 401
        assert response.json == {
            'message': "User not permitted to perform action"
        }

    def test_add_file(self, client, mock_jwt_functions):
        text_excel_bytes = get_file_bytes(TEST_EXCEL)
        virtual_file = BytesIO(text_excel_bytes)
        response = client.post("/files", data={
            'file': (virtual_file, 'test.xlsx')
        })
        assert response.status_code == 200
        masks = [('id', '<<id>>')]
        masked_response = mask_values(response.json, masks)
        assert masked_response == {
            'id': '<<id>>',
            'name': 'test.xlsx',
            'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'size_bytes ': 9429
        }

        response = client.post("/files")
        assert response.status_code == 400
        assert response.json == {
            'message': 'file not found in request'
        }

        virtual_file = BytesIO(text_excel_bytes)
        response = client.post("/files", data={
            'file': (virtual_file, 'test.xlsx')
        })
        assert response.status_code == 400
        assert response.json == {
            'message': "Filename 'test.xlsx' already in use"
        }

        text_txt_bytes = get_file_bytes(TEST_TXT)
        virtual_file = BytesIO(text_txt_bytes)
        response = client.post("/files", data={
            'file': (virtual_file, 'test.txt')
        })
        assert response.status_code == 400
        assert response.json == {
            'message': "unsupported file type 'text/plain'"
        }

    def test_update_file(self, client, test_file, mock_jwt_functions):
        text_excel_bytes = get_file_bytes(TEST_EXCEL)
        virtual_file = BytesIO(text_excel_bytes)
        response = client.put("/files", query_string={'id': test_file['id']}, data={
            'file': (virtual_file, 'test.xlsx')
        })

        assert response.status_code == 200
        masks = [('id', '<<id>>')]
        masked_response = mask_values(response.json, masks)
        assert masked_response == {
            'id': '<<id>>',
            'name': 'test.xlsx',
            'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'size_bytes ': 9429
        }

        virtual_file = BytesIO(text_excel_bytes)
        response = client.put(f"/files", data={
            'file': (virtual_file, 'test.xlsx')
        })
        assert response.status_code == 400
        assert response.json == {
            'message': "id not found in request"
        }

        response = client.put("/files", query_string={'id': test_file['id']}, data={
            'file': None
        })
        assert response.status_code == 400
        assert response.json == {
            'message': "file not found in request"
        }

        virtual_file = BytesIO(text_excel_bytes)
        response = client.put("/files", query_string={'id': test_file['id']}, data={
            'file': (virtual_file, 'different.xlsx')
        })
        assert response.status_code == 400
        assert response.json == {
            'message': "Replacement does not match existing file"
        }

    def test_download(self, client, test_file, mock_jwt_functions):
        response = client.get("/files/download", query_string={'id': test_file['id']})
        assert response.status_code == 200
        assert response.headers['Content-Type'] == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        assert response.headers['Content-Disposition'] == 'attachment; filename=test.xlsx'
        assert int(response.headers['Content-Length']) == 9429
        assert isinstance(response.data, bytes)

        response = client.get("/files/download")
        assert response.status_code == 400
        assert response.json == {
            'message': "id not found in request"
        }

    def test_delete(self, client, test_file, mock_jwt_functions):
        response = client.delete("/files", query_string={'id': test_file['id']})
        assert response.status_code == 200
        assert response.json == {'success': True}

        response = client.delete("/files")
        assert response.status_code == 400
        assert response.json == {
            'message': "id not found in request"
        }

    def test_get_file_data(self, client, test_file, mock_jwt_functions):
        response = client.get("/files/data", query_string={'id': test_file['id']})
        assert response.status_code == 200
        assert response.json == get_results('file_data.json')

        response = client.get("/files/data")
        assert response.status_code == 400
        assert response.json == {
            'message': "id not found in request"
        }
