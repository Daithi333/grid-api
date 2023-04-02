import logging
from contextvars import ContextVar

from sqlalchemy.orm import Session

from database import db

logger = logging.getLogger(__name__)

db_session: ContextVar[Session] = ContextVar("db_session")
current_user_id: ContextVar[str] = ContextVar("current_user_id")


def init_db_session():
    session = db.get_session()
    db_session.set(session)
    logger.debug('Initialised Database Session')


def teardown_db_session():
    session = db_session.get()
    session.close()
    logger.debug('Closed Database Session')


def init_user_id(user_id: str):
    current_user_id.set(user_id)
    logger.debug('Set Current User Id')
