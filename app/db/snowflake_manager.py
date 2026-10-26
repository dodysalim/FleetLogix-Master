import os
import logging
import snowflake.connector
from typing import List, Optional
from app.core.interfaces import IDatabaseManager
from dotenv import load_dotenv

load_dotenv()

class SnowflakeManager(IDatabaseManager):
    """
    Concrete implementation of Snowflake manager for Data Warehouse operations.
    """
    def __init__(self):
        self._conn = None
        self._cursor = None
        self._logger = logging.getLogger(__name__)

    def connect(self):
        try:
            self._conn = snowflake.connector.connect(
                user=os.getenv('SNOWFLAKE_USER'),
                password=os.getenv('SNOWFLAKE_PASSWORD'),
                account=os.getenv('SNOWFLAKE_ACCOUNT'),
                warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
                database=os.getenv('SNOWFLAKE_DATABASE'),
                schema=os.getenv('SNOWFLAKE_SCHEMA')
            )
            self._cursor = self._conn.cursor()
            # Explicitly set warehouse session
            warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
            self._cursor.execute(f"USE WAREHOUSE {warehouse}")
            self._logger.info(f"Successfully connected to Snowflake. Using Warehouse: {warehouse}")
        except Exception as e:
            self._logger.error(f"Failed to connect to Snowflake: {e}")
            raise

    def close(self):
        if self._cursor:
            self._cursor.close()
        if self._conn:
            self._conn.close()
            self._logger.info("Snowflake connection closed.")

    def execute_query(self, query: str, params: tuple = None):
        try:
            self._cursor.execute(query, params)
            return self._cursor.fetchall()
        except Exception as e:
            self._logger.error(f"Snowflake query error: {e}")
            raise

    def execute_many(self, query: str, data: List[tuple]):
        """
        Note: For bulk loading in Snowflake, 'COPY INTO' or using the write_pandas 
        method is preferred. This is a generic implementation.
        """
        try:
            self._cursor.executemany(query, data)
        except Exception as e:
            self._logger.error(f"Snowflake execute_many error: {e}")
            raise

    def commit(self):
        # Snowflake usually auto-commits or handled via transactions explicitly
        pass

    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor
