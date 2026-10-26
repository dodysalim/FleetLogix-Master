import os
import logging
import psycopg2.extras
from typing import List, Optional
from app.core.interfaces import IDatabaseManager
from dotenv import load_dotenv

load_dotenv()

class PostgresManager(IDatabaseManager):
    """
    Concrete implementation of PostgreSQL manager.
    Follows Dependency Inversion Principle.
    """
    def __init__(self):
        self._conn = None
        self._cursor = None
        self._logger = logging.getLogger(__name__)

    def connect(self):
        try:
            self._conn = psycopg2.connect(
                dbname=os.getenv('DB_NAME', 'fleetlogix_db'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'postgres'),
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432')
            )
            self._cursor = self._conn.cursor()
            self._logger.info("Successfully connected to PostgreSQL database.")
        except Exception as e:
            self._logger.error(f"Failed to connect to database: {e}")
            raise

    def close(self):
        if self._cursor:
            self._cursor.close()
        if self._conn:
            self._conn.close()
            self._logger.info("Database connection closed.")

    def execute_query(self, query: str, params: tuple = None):
        try:
            self._cursor.execute(query, params)
            return self._cursor.fetchall() if self._cursor.description else None
        except Exception as e:
            self._logger.error(f"Error executing query: {e}")
            self._conn.rollback()
            raise

    def execute_many(self, query: str, data: List[tuple]):
        try:
            # We use execute_values because it's significantly faster than executemany
            psycopg2.extras.execute_values(self._cursor, query, data)
            self._logger.info(f"Bulk insertion completed.")
        except Exception as e:
            self._logger.error(f"Error during bulk execution: {e}")
            self._conn.rollback()
            raise

    def commit(self):
        if self._conn:
            self._conn.commit()

    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor
