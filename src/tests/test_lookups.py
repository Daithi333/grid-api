from copy import copy
from io import BytesIO

from enums import LookupOperator
from tests.conftest import get_file_bytes, TEST_LOOKUP_EXCEL
from tests.util import mask_values


class TestLookups:

    @classmethod
    def _add_lookup(cls, client, file_id):
        lookup_file_bytes = get_file_bytes(TEST_LOOKUP_EXCEL)
        virtual_file = BytesIO(lookup_file_bytes)
        response = client.post("/files", data={
            'file': (virtual_file, 'lookup.xlsx')
        })
        assert response.status_code == 200
        lookup_file = response.json
        lookup_file_id = lookup_file['id']
        lookup_data = {
            'fileId': file_id,
            'name': 'test lookup',
            'field': 'Last Name',
            'lookupFileId': lookup_file_id,
            'lookupField': 'Last Name',
            'operator': LookupOperator.EQUALS.value
        }
        response = client.post("/lookups", json=lookup_data)
        assert response.status_code == 200
        return response.json

    def test_get_lookups(self, client, test_file):
        response = client.get("/lookups", query_string={'fileId': test_file['id']})
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 0

        file_id = test_file['id']
        lookup = self._add_lookup(client, file_id)
        lookup_id = lookup['id']

        response = client.get("/lookups", query_string={'fileId': file_id})
        assert response.status_code == 200
        masks = [('id', '<<id>>'), ('fileId', '<<fileId>>'), ('lookupFileId', '<<lookupFileId>>')]
        masked_response = [mask_values(item, masks) for item in response.json]
        assert masked_response == [
            {
                'field': 'Last Name',
                'fileId': '<<fileId>>',
                'id': '<<id>>',
                'lookupField': 'Last Name',
                'lookupFileId': '<<lookupFileId>>',
                'name': 'test lookup',
                'operator': 'equals'
            }
        ]

        response = client.get("/lookups", query_string={'fileId': file_id, 'id': lookup_id})
        assert response.status_code == 200
        assert isinstance(response.json, dict)
        masked_response = mask_values(response.json, masks)
        assert masked_response == {
            'field': 'Last Name',
            'fileId': '<<fileId>>',
            'id': '<<id>>',
            'lookupField': 'Last Name',
            'lookupFileId': '<<lookupFileId>>',
            'name': 'test lookup',
            'operator': 'equals'
        }

        response = client.get("/lookups", query_string={'id': lookup_id})
        assert response.status_code == 400
        assert response.json == {
            'message': 'file id not found in request'
        }

    def test_add_lookup(self, client, test_file):
        lookup_file_bytes = get_file_bytes(TEST_LOOKUP_EXCEL)
        virtual_file = BytesIO(lookup_file_bytes)
        response = client.post("/files", data={
            'file': (virtual_file, 'lookup.xlsx')
        })
        assert response.status_code == 200

        lookup_file = response.json
        lookup_file_id = lookup_file['id']
        lookup_data = {
            'fileId': test_file['id'],
            'name': 'test lookup',
            'field': 'Last Name',
            'lookupFileId': lookup_file_id,
            'lookupField': 'Last Name',
            'operator': LookupOperator.EQUALS.value
        }

        response = client.post("/lookups", json=lookup_data)
        assert response.status_code == 200
        masks = [('id', '<<id>>'), ('fileId', '<<fileId>>'), ('lookupFileId', '<<lookupFileId>>')]
        masked_response = mask_values(response.json, masks)
        assert masked_response == {
            'field': 'Last Name',
            'fileId': '<<fileId>>',
            'id': '<<id>>',
            'lookupField': 'Last Name',
            'lookupFileId': '<<lookupFileId>>',
            'name': 'test lookup',
            'operator': 'equals'
        }

        invalid_data = copy(lookup_data)
        invalid_data.pop('name')
        response = client.post("/lookups", json=invalid_data)
        assert response.status_code == 400
        assert response.json == {'message': "some lookup fields were missing"}

        invalid_data = copy(lookup_data)
        invalid_data.pop('fileId')
        response = client.post("/lookups", json=invalid_data)
        assert response.status_code == 400
        assert response.json == {'message': "some lookup fields were missing"}

        invalid_data = copy(lookup_data)
        invalid_data.pop('field')
        response = client.post("/lookups", json=invalid_data)
        assert response.status_code == 400
        assert response.json == {'message': "some lookup fields were missing"}

        invalid_data = copy(lookup_data)
        invalid_data.pop('lookupField')
        response = client.post("/lookups", json=invalid_data)
        assert response.status_code == 400
        assert response.json == {'message': "some lookup fields were missing"}

        invalid_data = copy(lookup_data)
        invalid_data.pop('lookupField')
        response = client.post("/lookups", json=invalid_data)
        assert response.status_code == 400
        assert response.json == {'message': "some lookup fields were missing"}

        invalid_data = copy(lookup_data)
        invalid_data.pop('operator')
        response = client.post("/lookups", json=invalid_data)
        assert response.status_code == 400
        assert response.json == {'message': "some lookup fields were missing"}

    def test_delete_lookup(self, client, test_file):
        lookup = self._add_lookup(client, test_file['id'])
        lookup_id = lookup['id']

        response = client.delete("/lookups", query_string={'id': lookup_id})
        assert response.status_code == 200
        assert response.json == {'success': True}
