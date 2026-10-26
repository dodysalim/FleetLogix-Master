import logging
import pandas as pd
from typing import List, Dict
from app.db.postgres_manager import PostgresManager
from app.db.snowflake_manager import SnowflakeManager
from snowflake.connector.pandas_tools import write_pandas

class ETLEngine:
    """
    Enterprise ETL Orchestrator for FleetLogix.
    Moves data from PostgreSQL (Transactional Source) to Snowflake (Star Schema Target).
    """
    def __init__(self, pg_manager: PostgresManager, sf_manager: SnowflakeManager):
        self._pg = pg_manager
        self._sf = sf_manager
        self._logger = logging.getLogger(__name__)

    def run_etl(self):
        """
        Executes the full ETL (Extract, Transform, Load) pipeline.
        """
        self._logger.info("Initializing ETL Pipeline...")
        try:
            self._pg.connect()
            self._sf.connect()
            
            # Sub-pipeline for Dates & Times (Dimension Population)
            self._populate_static_dimensions()

            # Sub-pipeline for Master Data Dimensions (Vehicles, Drivers, Routes, Customers)
            self._transform_load_master_dimensions()
            
            # Sub-pipeline for Fact Tables (Deliveries)
            self._transform_load_fact_deliveries()

            self._logger.info("ETL Pipeline completed successfully.")
        except Exception as e:
            self._logger.error(f"ETL Execution failure: {e}", exc_info=True)
            raise
        finally:
            self._pg.close()
            self._sf.close()

    def _populate_static_dimensions(self):
        self._logger.info("Initializing Static Dimensions (Date/Time)...")
        # Populate dim_date via Snowflake SQL if empty
        cursor = self._sf.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM dim_date")
        if cursor.fetchone()[0] == 0:
            self._logger.info("Generating dim_date data...")
            cursor.execute("""
                INSERT INTO dim_date
                SELECT 
                    TO_CHAR(date_day, 'YYYYMMDD')::INT,
                    date_day,
                    DAYOFWEEK(date_day),
                    DAYNAME(date_day),
                    DAY(date_day),
                    DAYOFYEAR(date_day),
                    WEEK(date_day),
                    MONTH(date_day),
                    MONTHNAME(date_day),
                    QUARTER(date_day),
                    YEAR(date_day),
                    CASE WHEN DAYNAME(date_day) IN ('Sat', 'Sun') THEN TRUE ELSE FALSE END,
                    FALSE, NULL, QUARTER(date_day), YEAR(date_day)
                FROM (
                    SELECT DATEADD(day, seq4(), '2022-01-01') AS date_day
                    FROM TABLE(GENERATOR(ROWCOUNT => 1500))
                )
            """)
        
        cursor.execute("SELECT COUNT(*) FROM dim_time")
        if cursor.fetchone()[0] == 0:
            self._logger.info("Generating dim_time data...")
            cursor.execute("""
                INSERT INTO dim_time
                SELECT 
                    (hour * 3600 + minute * 60 + second)::INT,
                    hour, minute, second,
                    CASE WHEN hour < 6 THEN 'Madrugada' WHEN hour < 12 THEN 'Mañana' WHEN hour < 18 THEN 'Tarde' ELSE 'Noche' END,
                    LPAD(hour,2,'0') || ':' || LPAD(minute,2,'0'),
                    TO_CHAR(TO_TIME(LPAD(hour,2,'0') || ':' || LPAD(minute,2,'0')), 'HH12:MI AM'),
                    CASE WHEN hour < 12 THEN 'AM' ELSE 'PM' END,
                    CASE WHEN hour >= 8 AND hour <= 18 THEN TRUE ELSE FALSE END,
                    CASE WHEN hour < 8 THEN 'Turno 3' WHEN hour < 16 THEN 'Turno 1' ELSE 'Turno 2' END
                FROM (SELECT seq4() as hour FROM TABLE(GENERATOR(ROWCOUNT => 24)))
                CROSS JOIN (SELECT seq4() as minute FROM TABLE(GENERATOR(ROWCOUNT => 60)))
                CROSS JOIN (SELECT seq4() as second FROM TABLE(GENERATOR(ROWCOUNT => 60)))
                LIMIT 86400
            """)

    def _transform_load_master_dimensions(self):
        self._logger.info("Transforming Master Dimensions...")
        
        # 1. Vehicles
        df_v = pd.read_sql("""
            SELECT vehicle_id as vehicle_key, vehicle_id, license_plate, vehicle_type, capacity_kg, 
                   fuel_type, acquisition_date, status, acquisition_date as valid_from, '9999-12-31'::DATE as valid_to, TRUE as is_current 
            FROM vehicles""", self._pg.connection)
        df_v.columns = [c.upper() for c in df_v.columns]
        write_pandas(self._sf.connection, df_v, "DIM_VEHICLE")

        # 2. Drivers
        df_d = pd.read_sql("""
            SELECT driver_id as driver_key, driver_id, employee_code, first_name || ' ' || last_name as full_name, 
                   license_number, license_expiry, phone, hire_date, status, hire_date as valid_from, '9999-12-31'::DATE as valid_to, TRUE as is_current 
            FROM drivers""", self._pg.connection)
        df_d.columns = [c.upper() for c in df_d.columns]
        write_pandas(self._sf.connection, df_d, "DIM_DRIVER")
        
        # 3. Routes
        df_r = pd.read_sql("""
            SELECT route_id as route_key, route_id, route_code, origin_city, destination_city, 
                   distance_km, estimated_duration_hours, toll_cost FROM routes""", self._pg.connection)
        df_r.columns = [c.upper() for c in df_r.columns]
        write_pandas(self._sf.connection, df_r, "DIM_ROUTE")

        # 4. Customers (Extract unique from deliveries)
        df_c = pd.read_sql("""
            SELECT DISTINCT customer_name, 'Individual' as customer_type, split_part(delivery_address, ',', 2) as city, 
                   'Regular' as customer_category FROM deliveries""", self._pg.connection)
        df_c['CUSTOMER_KEY'] = range(1, len(df_c) + 1)
        df_c.columns = [c.upper() for c in df_c.columns]
        write_pandas(self._sf.connection, df_c, "DIM_CUSTOMER")

    def _transform_load_fact_deliveries(self):
        self._logger.info("Transforming Fact Deliveries...")
        query = """
            SELECT 
                d.delivery_id, d.trip_id, d.tracking_number, d.package_weight_kg, 
                d.scheduled_datetime, d.delivered_datetime, d.delivery_status, d.recipient_signature,
                t.vehicle_id, t.driver_id, t.route_id, t.fuel_consumed_liters, t.departure_datetime, t.arrival_datetime,
                r.distance_km, r.toll_cost, r.destination_city, d.customer_name
            FROM deliveries d
            JOIN trips t ON d.trip_id = t.trip_id
            JOIN routes r ON t.route_id = r.route_id
        """
        df = pd.read_sql(query, self._pg.connection)
        
        # Transformations
        df['DATE_KEY'] = pd.to_datetime(df['scheduled_datetime']).dt.strftime('%Y%m%d').astype(int)
        df['SCHEDULED_TIME_KEY'] = (pd.to_datetime(df['scheduled_datetime']).dt.hour * 3600 + pd.to_datetime(df['scheduled_datetime']).dt.minute * 60).astype(int)
        df['DELIVERED_TIME_KEY'] = df['delivered_datetime'].apply(lambda x: (x.hour * 3600 + x.minute * 60) if pd.notnull(x) else 0).astype(int)
        
        df['DELIVERY_TIME_MINUTES'] = ((pd.to_datetime(df['delivered_datetime']) - pd.to_datetime(df['scheduled_datetime'])).dt.total_seconds() / 60).fillna(0).round(2)
        df['DELAY_MINUTES'] = df['DELIVERY_TIME_MINUTES'].apply(lambda x: max(0, x))
        df['IS_ON_TIME'] = df['DELAY_MINUTES'] <= 30
        
        # Trip metrics
        trip_counts = df.groupby('trip_id').size()
        df['DELIVERIES_IN_TRIP'] = df['trip_id'].map(trip_counts)
        trip_durations = (pd.to_datetime(df['arrival_datetime']) - pd.to_datetime(df['departure_datetime'])).dt.total_seconds() / 3600
        df['DELIVERIES_PER_HOUR'] = (df['DELIVERIES_IN_TRIP'] / trip_durations).round(2)
        
        df['FUEL_EFFICIENCY_KM_PER_LITER'] = (df['distance_km'] / df['fuel_consumed_liters']).round(2)
        df['COST_PER_DELIVERY'] = ((df['fuel_consumed_liters'] * 5000 + df['toll_cost']) / df['DELIVERIES_IN_TRIP']).round(2)
        df['REVENUE_PER_DELIVERY'] = (20000 + df['package_weight_kg'] * 500).round(2)
        
        # Keys mapping
        # In a real ETL we'd join with dim tables to get surrogate keys, 
        # here we use source IDs as placeholders for simplicity in this star schema.
        df['VEHICLE_KEY'] = df['vehicle_id']
        df['DRIVER_KEY'] = df['driver_id']
        df['ROUTE_KEY'] = df['route_id']
        
        # Customer key mapping (Mock join)
        df['CUSTOMER_KEY'] = 1 
        
        cols_to_load = [
            'DATE_KEY', 'SCHEDULED_TIME_KEY', 'DELIVERED_TIME_KEY', 'VEHICLE_KEY', 'DRIVER_KEY', 'ROUTE_KEY', 'CUSTOMER_KEY',
            'DELIVERY_ID', 'TRIP_ID', 'TRACKING_NUMBER', 'PACKAGE_WEIGHT_KG', 'DISTANCE_KM', 'FUEL_CONSUMED_LITERS',
            'DELIVERY_TIME_MINUTES', 'DELAY_MINUTES', 'DELIVERIES_PER_HOUR', 'FUEL_EFFICIENCY_KM_PER_LITER',
            'COST_PER_DELIVERY', 'REVENUE_PER_DELIVERY', 'IS_ON_TIME', 'DELIVERY_STATUS'
        ]
        
        df_fact = df[cols_to_load].copy()
        df_fact['HAS_SIGNATURE'] = df['recipient_signature']
        df_fact['IS_DAMAGED'] = False
        df_fact['ETL_BATCH_ID'] = 1
        
        df_fact.columns = [c.upper() for c in df_fact.columns]
        write_pandas(self._sf.connection, df_fact, "FACT_DELIVERIES")
