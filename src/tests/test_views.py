from copy import copy

from tests.util import mask_values


class TestViews:

    @classmethod
    def _add_view(cls, client, file_id):
        view_data = {
            'fileId': file_id,
            'name': 'test view',
            'fields': ['First Name', 'Last Name'],
            'filters': []
        }
        response = client.post("/views", json=view_data)
        assert response.status_code == 200
        return response.json

    def test_get_views(self, client, test_file, mock_jwt_required):
        response = client.get("/views", query_string={'fileId': test_file['id']})
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 0

        file_id = test_file['id']
        view = self._add_view(client, file_id)
        view_id = view['id']

        response = client.get("/views", query_string={'fileId': file_id})
        assert response.status_code == 200
        masks = [('id', '<<id>>'), ('fileId', '<<fileId>>')]
        masked_response = [mask_values(item, masks) for item in response.json]
        assert masked_response == [
            {
                'id': '<<id>>',
                'name': 'test view',
                'fields': ['First Name', 'Last Name'],
                'fileId': '<<fileId>>',
                'filters': []
            }
        ]

        response = client.get("/views", query_string={'fileId': file_id, 'id': view_id})
        assert response.status_code == 200
        assert isinstance(response.json, dict)
        masked_response = mask_values(response.json, masks)
        assert masked_response == {
            'id': '<<id>>',
            'name': 'test view',
            'fields': ['First Name', 'Last Name'],
            'fileId': '<<fileId>>',
            'filters': []
        }

        response = client.get("/views", query_string={'id': view_id})
        assert response.status_code == 400
        assert response.json == {
            'message': 'file id not found in request'
        }

    def test_add_view(self, client, test_file, mock_jwt_required):
        view_data = {
            'fileId': test_file['id'],
            'name': 'test view',
            'fields': ['First Name', 'Last Name'],
            'filters': []
        }
        response = client.post("/views", json=view_data)
        assert response.status_code == 200
        masks = [('id', '<<id>>'), ('fileId', '<<fileId>>')]
        masked_response = mask_values(response.json, masks)
        assert masked_response == {
            'id': '<<id>>',
            'name': 'test view',
            'fields': ['First Name', 'Last Name'],
            'fileId': '<<fileId>>',
            'filters': []
        }

        invalid_data = copy(view_data)
        invalid_data.pop('name')
        response = client.post("/views", json=invalid_data)
        assert response.status_code == 400
        assert response.json == {'message': "name and file id required"}

        invalid_data = copy(view_data)
        invalid_data.pop('filters')
        invalid_data.pop('fields')
        response = client.post("/views", json=invalid_data)
        assert response.status_code == 400
        assert response.json == {'message': "view expected to have fields and filter data"}

    def test_delete_view(self, client, test_file, mock_jwt_required):
        view = self._add_view(client, test_file['id'])
        view_id = view['id']

        response = client.delete("/views", query_string={'id': view_id})
        assert response.status_code == 200
        assert response.json == {'success': True}
