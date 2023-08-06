"""Extensions to improve the experience of handling the database."""

from contextlib import contextmanager
from typing import Generator

from sqlalchemy.engine import Engine
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import Session


@contextmanager
def session_scope(bind: Engine, *args, **kwargs) -> Generator[Session, Engine, None]:
    """Provide a transactional scope around a series of database operations.

    src: https://docs.sqlalchemy.org/en/13/orm/session_basics.html
    """
    session = Session(bind=bind, expire_on_commit=False, *args, **kwargs)
    try:
        yield session
        session.commit()
    except InvalidRequestError as e:
        session.rollback()
        raise e
    finally:
        session.close()
