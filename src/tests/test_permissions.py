from copy import copy

from tests.util import mask_values


class TestPermissions:
    masks = [('id', '<<id>>')]
    user_masks = [('id', '<<userId>>')]

    @classmethod
    def _add_user(cls, client):
        signup_data = {
            'email': 'testuser2@mail.com',
            'password': 'Abc123!!',
            'firstname': 'test',
            'lastname': 'user2',
        }
        response = client.post("/users/signup", data=signup_data)
        assert response.status_code == 200
        return response.json

    @classmethod
    def _add_permission(cls, client, file_id):
        permission_data = {
            'fileId': file_id,
            'email': 'testuser2@mail.com',
            'role': 'CONTRIBUTOR'
        }
        response = client.post("/permissions", json=permission_data)
        assert response.status_code == 200
        return response.json

    def test_get_current_user_permissions(self, client, test_file):
        response = client.get("/permissions/user")
        assert response.status_code == 200
        masked_response = [mask_values(item, self.masks) for item in response.json]
        for mr in masked_response:
            mr['user'] = mask_values(mr['user'], self.user_masks)

        assert masked_response == [
            {
                "fileId": test_file['id'],
                "id": "<<id>>",
                "role": "OWNER",
                "user": {
                    "email": "testuser@mail.com",
                    "firstname": "test",
                    "id": "<<userId>>",
                    "lastname": "user"
                }
            }
        ]

        response = client.get("/permissions/user", query_string={'fileId': test_file['id']})
        assert response.status_code == 200
        masked_response = mask_values(response.json, self.masks)
        masked_response['user'] = mask_values(masked_response['user'], self.user_masks)
        assert masked_response == {
            "fileId": test_file['id'],
            "id": "<<id>>",
            "role": "OWNER",
            "user": {
                "email": "testuser@mail.com",
                "firstname": "test",
                "id": "<<userId>>",
                "lastname": "user"
            }
        }

    def test_get_permissions(self, client, test_file):
        response = client.get("/permissions", query_string={'fileId': test_file['id']})
        assert response.status_code == 200
        masked_response = [mask_values(item, self.masks) for item in response.json]
        for mr in masked_response:
            mr['user'] = mask_values(mr['user'], self.user_masks)

        assert masked_response == [
            {
                "fileId": test_file['id'],
                "id": "<<id>>",
                "role": "OWNER",
                "user": {
                    "email": "testuser@mail.com",
                    "firstname": "test",
                    "id": "<<userId>>",
                    "lastname": "user"
                }
            }
        ]

        response = client.get("/permissions")
        assert response.status_code == 400
        assert response.json == {
            'message': 'user id or file id found in request'
        }

    def test_add_permissions(self, client, test_file):
        self._add_user(client)

        permission_data = {
            'fileId': test_file['id'],
            'email': 'testuser2@mail.com',
            'role': 'CONTRIBUTOR'
        }

        response = client.post("/permissions", json=permission_data)
        assert response.status_code == 200
        masked_response = mask_values(response.json, self.masks)
        masked_response['user'] = mask_values(masked_response['user'], self.user_masks)
        assert masked_response == {
            'fileId': test_file['id'],
            'id': '<<id>>',
            'role': 'CONTRIBUTOR',
            'user': {
                'email': 'testuser2@mail.com',
                'firstname': 'test',
                'id': '<<userId>>',
                'lastname': 'user2'
            }
        }

        invalid_permission_data = copy(permission_data)
        invalid_permission_data['email'] = 'testuser3@mail.com'

        response = client.post("/permissions", json=invalid_permission_data)
        assert response.status_code == 404
        assert response.json == {'message': 'User is not recognised'}

        invalid_permission_data = copy(permission_data)
        invalid_permission_data.pop('fileId')

        response = client.post("/permissions", json=invalid_permission_data)
        assert response.status_code == 400
        assert response.json == {
            'message': 'file id, email and role expected to add permission'
        }

        invalid_permission_data = copy(permission_data)
        invalid_permission_data.pop('email')

        response = client.post("/permissions", json=invalid_permission_data)
        assert response.status_code == 400
        assert response.json == {
            'message': 'file id, email and role expected to add permission'
        }

        invalid_permission_data = copy(permission_data)
        invalid_permission_data.pop('role')

        response = client.post("/permissions", json=invalid_permission_data)
        assert response.status_code == 400
        assert response.json == {
            'message': 'file id, email and role expected to add permission'
        }

        invalid_permission_data = copy(permission_data)
        invalid_permission_data['role'] = 'INVALID'
        response = client.post("/permissions", json=invalid_permission_data)
        assert response.status_code == 400
        assert response.json == {
            'message': f"Invalid role provided: 'INVALID'"
        }

    def test_update_permissions(self, client, test_file):
        self._add_user(client)
        permission = self._add_permission(client, test_file['id'])
        permission_id = permission['id']
        permission_data = {
            'id': permission_id,
            'role': 'OWNER'
        }

        response = client.put("/permissions", json=permission_data)
        assert response.status_code == 200
        masked_response = mask_values(response.json, self.masks)
        masked_response['user'] = mask_values(masked_response['user'], self.user_masks)
        assert masked_response == {
            'fileId': test_file['id'],
            'id': '<<id>>',
            'role': 'OWNER',
            'user': {
                'email': 'testuser2@mail.com',
                'firstname': 'test',
                'id': '<<userId>>',
                'lastname': 'user2'
            }
        }

        invalid_permission_data = copy(permission_data)
        invalid_permission_data.pop('id')
        response = client.put("/permissions", json=invalid_permission_data)
        assert response.status_code == 400
        assert response.json == {
            'message': 'id not found in request'
        }

        invalid_permission_data = copy(permission_data)
        invalid_permission_data['role'] = 'INVALID'
        response = client.put("/permissions", json=invalid_permission_data)
        assert response.status_code == 400
        assert response.json == {
            'message': f"Invalid role provided: 'INVALID'"
        }

    def test_delete_permissions(self, client, test_file):
        self._add_user(client)
        permission = self._add_permission(client, test_file['id'])
        permission_id = permission['id']

        response = client.delete("/permissions", query_string={'id': permission_id})

        assert response.status_code == 200
        assert response.json == {'success': True}
