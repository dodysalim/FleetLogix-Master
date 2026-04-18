"""
FleetLogix - ETL Pipeline Module
================================
Professional ETL pipeline for data migration from PostgreSQL to Snowflake.

Features:
- Extract: Chunked reading from PostgreSQL
- Transform: Pandas-based transformations
- Load: Bulk loading to Snowflake via COPY command
- Scheduling: Automated daily execution

SOLID Principles Applied:
- Single Responsibility: Each class handles one phase of ETL
- Open/Closed: Easy to add new transformations
- Liskov Substitution: Pluggable data sources/destinations
- Interface Segregation: Clean interfaces for each component
- Dependency Inversion: Uses abstract interfaces

Author: Dody Dueñas
Project: Henry M2 - FleetLogix Enterprise
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Iterator
from abc import ABC, abstractmethod
from dataclasses import dataclass

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import snowflake.connector
import schedule
import time


@dataclass
class ETLConfig:
    """Configuration for ETL pipeline"""

    postgres_dsn: str
    snowflake_config: Dict[str, str]
    chunk_size: int = 100000
    batch_size: int = 10000
    enable_logging: bool = True


@dataclass
class ETLMetrics:
    """Metrics for ETL execution"""

    records_extracted: int = 0
    records_transformed: int = 0
    records_loaded: int = 0
    errors: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @property
    def duration_seconds(self) -> float:
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0


class IDataExtractor(ABC):
    """Abstract interface for data extraction"""

    @abstractmethod
    def extract(self, table: str, chunksize: int) -> Iterator[pd.DataFrame]:
        """Extract data in chunks"""
        pass


class IDataTransformer(ABC):
    """Abstract interface for data transformation"""

    @abstractmethod
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform a DataFrame"""
        pass


class IDataLoader(ABC):
    """Abstract interface for data loading"""

    @abstractmethod
    def load(self, df: pd.DataFrame, target_table: str) -> int:
        """Load DataFrame to target table"""
        pass


class PostgreSExtractor(IDataExtractor):
    """PostgreSQL data extractor with chunked reading"""

    def __init__(self, dsn: str, logger: logging.Logger):
        self.dsn = dsn
        self.logger = logger
        self.engine = create_engine(dsn)

    def extract(self, table: str, chunksize: int = 100000) -> Iterator[pd.DataFrame]:
        """Extract data in chunks"""
        self.logger.info(f"Extracting {table} in chunks of {chunksize}")
        query = f"SELECT * FROM {table}"
        for chunk in pd.read_sql(query, self.engine, chunksize=chunksize):
            yield chunk

    def extract_full(self, table: str) -> pd.DataFrame:
        """Extract entire table"""
        return pd.read_sql(f"SELECT * FROM {table}", self.engine)

    def close(self):
        self.engine.dispose()


class DataTransformer(IDataTransformer):
    """Data transformer with business logic"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        self.logger.info(f"Transforming {len(df)} records")
        df = df.replace({np.nan: None})
        datetime_cols = df.select_dtypes(include=["datetime64"]).columns
        for col in datetime_cols:
            df[col] = pd.to_datetime(df[col], utc=True, errors="coerce")
        return df

    def transform_deliveries(self, df: pd.DataFrame) -> pd.DataFrame:
        df["delivery_time_minutes"] = (
            (
                pd.to_datetime(df["delivered_datetime"])
                - pd.to_datetime(df["scheduled_datetime"])
            ).dt.total_seconds()
            / 60
        ).round(2)
        df["delay_minutes"] = df["delivery_time_minutes"].apply(
            lambda x: max(0, x) if pd.notna(x) else 0
        )
        df["is_on_time"] = df["delay_minutes"] <= 30
        return self.transform(df)


class SnowflakeLoader(IDataLoader):
    """Snowflake data loader using COPY command"""

    def __init__(self, config: Dict[str, str], logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.conn = None

    def connect(self):
        self.conn = snowflake.connector.connect(**self.config)
        self.logger.info("Connected to Snowflake")

    def load(self, df: pd.DataFrame, target_table: str) -> int:
        if df.empty:
            return 0

        from snowflake.connector.pandas_tools import write_pandas
        
        try:
            # write_pandas handles staging and copy into automatically
            success, nchunks, nrows, _ = write_pandas(
                conn=self.conn,
                df=df,
                table_name=target_table,
                auto_create_table=True  # Ensure tables are created if missing
            )
            
            if success:
                self.logger.info(f"Loaded {nrows} records to {target_table} in {nchunks} chunks")
                return nrows
            return 0
        except Exception as e:
            self.logger.error(f"Loading error into {target_table}: {e}")
            raise

    def close(self):
        if self.conn:
            self.conn.close()


class FleetLogixETL:
    """
    ETL Pipeline Orchestrator

    Coordinates: Extract -> Transform -> Load
    """

    TABLE_MAPPING = {
        "vehicles": "STG_VEHICLES",
        "drivers": "STG_DRIVERS",
        "routes": "STG_ROUTES",
        "trips": "STG_TRIPS",
        "deliveries": "STG_DELIVERIES",
        "maintenance": "STG_MAINTENANCE",
    }

    def __init__(self, config: ETLConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.metrics = ETLMetrics()
        self.extractor = None
        self.transformer = None
        self.loader = None

    def initialize(self):
        self.logger.info("Initializing ETL components")
        self.extractor = PostgreSExtractor(self.config.postgres_dsn, self.logger)
        self.transformer = DataTransformer(self.logger)
        self.loader = SnowflakeLoader(self.config.snowflake_config, self.logger)
        self.loader.connect()

    def run_full_etl(self) -> ETLMetrics:
        self.metrics.start_time = datetime.now()
        self.logger.info(f"Starting ETL at {self.metrics.start_time}")

        try:
            self.initialize()
            for source_table, target_table in self.TABLE_MAPPING.items():
                self._process_table(source_table, target_table)
        except Exception as e:
            self.logger.error(f"ETL failed: {e}")
            self.metrics.errors += 1
        finally:
            self.metrics.end_time = datetime.now()
            self._cleanup()

        self._log_metrics()
        return self.metrics

    def _process_table(self, source: str, target: str):
        self.logger.info(f"Processing {source} -> {target}")
        for chunk in self.extractor.extract(source, self.config.chunk_size):
            self.metrics.records_extracted += len(chunk)
            transformed = self.transformer.transform(chunk)
            self.metrics.records_transformed += len(transformed)
            loaded = self.loader.load(transformed, target)
            self.metrics.records_loaded += loaded

    def _cleanup(self):
        if self.extractor:
            self.extractor.close()
        if self.loader:
            self.loader.close()

    def _log_metrics(self):
        self.logger.info("=" * 50)
        self.logger.info("ETL Execution Metrics:")
        self.logger.info(f"  Records Extracted: {self.metrics.records_extracted:,}")
        self.logger.info(f"  Records Transformed: {self.metrics.records_transformed:,}")
        self.logger.info(f"  Records Loaded: {self.metrics.records_loaded:,}")
        self.logger.info(f"  Errors: {self.metrics.errors}")
        self.logger.info(f"  Duration: {self.metrics.duration_seconds:.2f} seconds")


def run_etl_job():
    """Job function for scheduled execution"""
    from dotenv import load_dotenv

    load_dotenv()

    # Build DSN from individual components
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME")
    
    postgres_dsn = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

    config = ETLConfig(
        postgres_dsn=postgres_dsn,
        snowflake_config={
            "user": os.getenv("SNOWFLAKE_USER"),
            "password": os.getenv("SNOWFLAKE_PASSWORD"),
            "account": os.getenv("SNOWFLAKE_ACCOUNT"),
            "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
            "database": os.getenv("SNOWFLAKE_DATABASE", "FLEETLOGIX_DW"),
            "schema": os.getenv("SNOWFLAKE_SCHEMA", "ANALYTICS"),
        },
    )

    etl = FleetLogixETL(config)
    return etl.run_full_etl()


def main():
    """Main entry point"""
    from dotenv import load_dotenv

    load_dotenv()

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    print("=" * 60)
    print("FleetLogix - ETL Pipeline")
    print("Author: Dody Dueñas")
    print("Project: Henry M2 - FleetLogix Enterprise")
    print("=" * 60)

    result = run_etl_job()

    print("\nETL Execution Summary:")
    print(f"  Status: {'Success' if result.errors == 0 else 'Failed'}")
    print(f"  Records Processed: {result.records_transformed:,}")
    print(f"  Duration: {result.duration_seconds:.2f} seconds")

    print("\nScheduling ETL for daily execution...")
    schedule.every().day.at("02:00").do(run_etl_job)
    print("ETL scheduled for 2:00 AM daily")

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()
