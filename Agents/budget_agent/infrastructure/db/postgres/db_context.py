"""
Module to connect to database for interactign with it
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from sqlalchemy.pool import QueuePool

from core.logger import LOGGER
from core.settings import SETTINGS

class SQLAlchemyConnection:
    """
    SQLAlchemy connection object to be used as context manager
    for interacting with database
    """

    session: Session

    def __init__(self):
        """Initialize the session as None."""
        self.connection = None
        self.session = None

    def __enter__(self):
        """Initialize the session when called using with statement."""
        if self.session is None:
            try:
                session_maker = sessionmaker()
                engine = self.fetch_tenant_engine()
                self.connection = engine.connect()
                self.session = session_maker(bind=self.connection)
            except Exception as why:
                LOGGER.error(
                    "Error while establishing a connection with database: %s", why
                )

        return self

    def __exit__(self, *args):
        """Close the session on exit."""
        if self.connection is not None:
            self.session.close()
            self.connection.close()

    def fetch_tenant_engine(self):
        """create the engine connection"""
        engine = None
        try:
            engine = create_engine(
                SETTINGS.postgres_connection_string,
                poolclass=QueuePool,
                pool_size=SETTINGS.new_db_pool,
            )
        except AssertionError as e:
            print(e)

        return engine
