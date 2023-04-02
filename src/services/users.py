import re

import bcrypt

from constants import EMAIL_REGEX, PASSWORD_REGEX
from context import db_session
from database.models import User
from error import BadRequestError, UnauthorizedError


class UserService:

    @classmethod
    def get(cls, id_: str = None, email: str = None) -> User or None:
        filters = {}
        if id_:
            filters['id'] = id_
        if email:
            filters['email'] = email

        session = db_session.get()
        return session.query(User).filter_by(**filters).one_or_none()

    @classmethod
    def signup(cls, email: str, password: str, firstname: str, lastname: str):
        session = db_session.get()

        if not cls.valid_email_format(email):
            raise BadRequestError('Invalid email format')

        if cls.get(email=email) is not None:
            raise BadRequestError('Email address is already registered')

        if not cls.valid_password_format(password):
            raise BadRequestError(
                'Insufficient password complexity. Must be at least 8 characters long, '
                'with 1 uppercase letter, 1 lowercase letter, 1 special character and 1 number'
            )

        user = User(
            firstname=firstname,
            lastname=lastname,
            email=email,
            password_hash=cls.get_password_hash(password)
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return cls._user_to_dict(user)

    @classmethod
    def login(cls, email: str, password: str) -> dict:
        session = db_session.get()
        user = session.query(User).filter_by(email=email).one_or_none()
        if not user:
            raise UnauthorizedError('User does not exist')

        if not cls.valid_password(password, user.password_hash):
            raise UnauthorizedError('Incorrect email or password')

        return cls._user_to_dict(user)

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
        return password_hash.decode('utf-8')

    @classmethod
    def valid_password(cls, password: str, password_hash: str) -> bool:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        return hashed_password == password_hash.encode('utf-8')

    @classmethod
    def valid_email_format(cls, email):
        return re.match(EMAIL_REGEX, email) is not None

    @classmethod
    def valid_password_format(cls, password):
        return re.match(PASSWORD_REGEX, password) is not None

    @classmethod
    def _user_to_dict(cls, user: User) -> dict:
        return {
            'id': user.id,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'email': user.email
        }
