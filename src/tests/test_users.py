import base64
from copy import copy

from services.users import UserService
from tests.conftest import TEST_USER_EMAIL, TEST_USER_PASSWORD
from tests.util import mask_values


class TestUsers:

    def test_signup(self, client):
        signup_data = {
            'email': 'testuser2@mail.com',
            'password': 'Abc123!!',
            'firstname': 'test',
            'lastname': 'user2',
        }

        response = client.post("/users/signup", data=signup_data)

        assert response.status_code == 200
        masks = [('id', '<<id>>')]
        masked_response = mask_values(response.json, masks)
        assert masked_response == {
            'email': 'testuser2@mail.com',
            'firstname': 'test',
            'id': '<<id>>',
            'lastname': 'user2'
        }

        invalid_data = copy(signup_data)
        invalid_data.pop('email')
        response = client.post("/users/signup", data=invalid_data)
        assert response.status_code == 400
        assert response.json == {'message': 'missing fields for signup'}

        invalid_data = copy(signup_data)
        invalid_data.pop('password')
        response = client.post("/users/signup", data=invalid_data)
        assert response.status_code == 400
        assert response.json == {'message': 'missing fields for signup'}

        invalid_data = copy(signup_data)
        invalid_data.pop('firstname')
        response = client.post("/users/signup", data=invalid_data)
        assert response.status_code == 400
        assert response.json == {'message': 'missing fields for signup'}

        invalid_data = copy(signup_data)
        invalid_data.pop('lastname')
        response = client.post("/users/signup", data=invalid_data)
        assert response.status_code == 400
        assert response.json == {'message': 'missing fields for signup'}

        invalid_data = copy(signup_data)
        invalid_data['email'] = 'invalid-email.com'
        response = client.post("/users/signup", data=invalid_data)
        assert response.status_code == 400
        assert response.json == {'message': 'Invalid email format'}

        response = client.post("/users/signup", data=signup_data)
        assert response.status_code == 400
        assert response.json == {'message': 'Email address is already registered'}

        invalid_data = copy(signup_data)
        invalid_data['email'] = 'test-user3@mail.com'
        invalid_data['password'] = 'password1'
        response = client.post("/users/signup", data=invalid_data)
        assert response.status_code == 400
        assert response.json == {
            'message': 'Insufficient password complexity. Must be at least 8 characters long, '
            'with 1 uppercase letter, 1 lowercase letter, 1 special character and 1 number'
        }

    def test_login(self, client):
        headers = self._create_basic_auth_header(TEST_USER_EMAIL, TEST_USER_PASSWORD)
        response = client.post("/users/login", headers=headers)
        assert response.status_code == 200
        masks = [
            ('id', '<<id>>'),
            ('access_token', '<<access_token>>'),
            ('refresh_token', '<<refresh_token>>'),
            ('expires_at', '<<expires_at>>'),
        ]
        user_masks = [('id', '<<userId>>')]
        masked_response = mask_values(response.json, masks)
        masked_response['user'] = mask_values(masked_response['user'], user_masks)
        assert masked_response == {
            'id': '<<id>>',
            'access_token': '<<access_token>>',
            'expires_at': '<<expires_at>>',
            'refresh_token': '<<refresh_token>>',
            'user': {
                'email': TEST_USER_EMAIL,
                'id': '<<userId>>',
                'firstname': 'test',
                'lastname': 'user'
            },
        }

        headers = self._create_basic_auth_header('testuser2@mail.com', TEST_USER_PASSWORD)
        response = client.post("/users/login", headers=headers)
        assert response.status_code == 401
        assert response.json == {'message': 'Incorrect email or password'}

        headers = self._create_basic_auth_header(TEST_USER_EMAIL, 'Invalid1!')
        response = client.post("/users/login", headers=headers)
        assert response.status_code == 401
        assert response.json == {'message': 'Incorrect email or password'}

        response = client.post("/users/login", headers={})
        assert response.status_code == 401
        assert response.json == {'message': 'Authorization header missing'}

    @classmethod
    def _create_basic_auth_header(cls, username, password):
        auth_string = f"{username}:{password}"
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")
        return {"Authorization": f"Basic {auth_base64}"}

    def test_is_valid_password(self):
        assert UserService.valid_password_format('MyPassword1!') is True
        assert UserService.valid_password_format('password123') is False
        assert UserService.valid_password_format('PASSWORD123!') is False
        assert UserService.valid_password_format('password!') is False
        assert UserService.valid_password_format('MyPwd1!') is False
