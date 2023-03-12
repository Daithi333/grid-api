from services.users import UserService


def test_is_valid_password():
    assert UserService.valid_password_format('MyPassword1!') is True
    assert UserService.valid_password_format('password123') is False
    assert UserService.valid_password_format('PASSWORD123!') is False
    assert UserService.valid_password_format('password!') is False
