# 🛠️ Installation & Setup Guide: FleetLogix Enterprise

Follow these steps to deploy the FleetLogix Data Warehouse ecosystem.

---

## 1. Environment Preparation

Ensure you have the following installed:

| Requirement | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Programming language |
| PostgreSQL | 15+ | Transactional database |
| Docker | Latest | Containerization (optional) |
| Git | 2.30+ | Version control |

### Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv_fleet

# Activate (Linux/Mac)
source venv_fleet/bin/activate

# Activate (Windows)
venv_fleet\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## 2. Database Setup

### 2.1 PostgreSQL (Local Installation)

1. Download and install PostgreSQL from https://www.postgresql.org/download/
2. Start the PostgreSQL service
3. Create the database:

```bash
# Connect to PostgreSQL
psql -U postgres -h localhost

# Create database
CREATE DATABASE fleetlogix_db;

# Verify
\l
```

### 2.2 Using Docker (Alternative)

```bash
# Start PostgreSQL container
docker run -d \
  --name fleetlogix_postgres \
  -e POSTGRES_DB=fleetlogix_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=your_password \
  -p 5432:5432 \
  postgres:15-alpine
```

### 2.3 Snowflake (Cloud Data Warehouse)

1. Create a free trial account at https://signup.snowflake.com/
2. Log into Snowflake console
3. Open a new SQL Worksheet
4. Execute the contents of `sql/snowflake_schema.sql`

This will create:
- Database: `FLEETLOGIX_DW`
- Schema: `ANALYTICS`
- Tables: 6 dimension tables + 1 fact table

---

## 3. Environment Configuration

Create a `.env` file in the root directory:

```properties
# ==============================================================================
# FleetLogix Environment Configuration
# ==============================================================================

# PostgreSQL Configuration (Source Database)
DB_NAME=fleetlogix_db
DB_USER=postgres
DB_PASSWORD=Dody2003
DB_HOST=localhost
DB_PORT=5432

# Snowflake Configuration (Data Warehouse)
SNOWFLAKE_USER=YOUR_SF_USER
SNOWFLAKE_PASSWORD=YOUR_SF_PASSWORD
SNOWFLAKE_ACCOUNT=YOUR_ACCOUNT_ID
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=FLEETLOGIX_DW
SNOWFLAKE_SCHEMA=ANALYTICS

# AWS Configuration (Optional - for Avance 4)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=YOUR_KEY
AWS_SECRET_ACCESS_KEY=YOUR_SECRET

# Application Settings
LOG_LEVEL=INFO
EXECUTION_ENV=PROD
```

---

## 4. Database Initialization

### 4.1 Apply Schema to PostgreSQL

```bash
# Initialize database with schema
python scripts/init_db.py
```

This script will:
- Create all 6 tables (vehicles, drivers, routes, trips, deliveries, maintenance)
- Create basic indexes
- Apply table comments

### 4.2 Generate Synthetic Data

```bash
# Generate 500k+ records
python scripts/01_data_generation.py
```

Expected output:
```
FleetLogix - Data Generation Pipeline
=====================================
Generating master data...
  vehicles: 200
  drivers: 400
  routes: 50
Generating trip data...
  trips: 100000
Generating delivery data...
  deliveries: 400000
Generating maintenance data...
  maintenance: 5000
```

---

## 5. Running the Pipeline

### 5.1 Data Generation (Avance 1)

```bash
python scripts/01_data_generation.py
```

### 5.2 Query Execution (Avance 2)

Run the 12 analytical queries:

```bash
# Execute queries in PostgreSQL
psql -U postgres -d fleetlogix_db -f sql/queries.sql
```

### 5.3 Index Optimization (Avance 2 - Part 2)

```bash
# Apply optimization indexes
psql -U postgres -d fleetlogix_db -f sql/03_optimization_indexes.sql
```

### 5.4 ETL Pipeline (Avance 3)

```bash
# Run ETL from PostgreSQL to Snowflake
python scripts/05_etl_pipeline.py
```

### 5.5 AWS Lambda Deployment (Avance 4)

```bash
# Deploy Lambda functions
python scripts/aws_deploy.py
```

---

## 6. Verification Steps

### 6.1 Verify PostgreSQL Data

```sql
-- Check record counts
SELECT 'vehicles' as table_name, COUNT(*) as records FROM vehicles
UNION ALL
SELECT 'drivers', COUNT(*) FROM drivers
UNION ALL
SELECT 'routes', COUNT(*) FROM routes
UNION ALL
SELECT 'trips', COUNT(*) FROM trips
UNION ALL
SELECT 'deliveries', COUNT(*) FROM deliveries
UNION ALL
SELECT 'maintenance', COUNT(*) FROM maintenance;
```

### 6.2 Verify Snowflake Data

```sql
USE DATABASE FLEETLOGIX_DW;
USE SCHEMA ANALYTICS;

-- Check dimension tables
SELECT COUNT(*) FROM dim_vehicle;
SELECT COUNT(*) FROM dim_driver;
SELECT COUNT(*) FROM dim_route;

-- Check fact table
SELECT COUNT(*) FROM fact_deliveries;
```

### 6.3 Test PostgREST API

```bash
# Start containers
docker-compose up -d

# Test API
curl http://localhost:3000/vehicles?limit=5
```

---

## 7. Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Connection refused to PostgreSQL | Check PostgreSQL service is running |
| Authentication failed | Verify credentials in .env file |
| Snowflake account not found | Use format ORG-ACCOUNT (e.g., xy12345.us-east-1) |
| Memory error during data generation | Reduce chunk_size in scripts |
| Index creation fails | Check database permissions |

### Enable Debug Logging

```properties
LOG_LEVEL=DEBUG
```

---

## 8. Project Structure

```
Proyecto2Dody/
├── app/
│   ├── core/           # Core business logic
│   │   ├── etl_engine.py
│   │   ├── integrator.py
│   │   └── interfaces.py
│   ├── db/             # Database managers
│   │   ├── postgres_manager.py
│   │   └── snowflake_manager.py
│   └── generators/     # Data generators
│       ├── vehicle_generator.py
│       ├── driver_generator.py
│       ├── route_generator.py
│       ├── trip_generator.py
│       ├── delivery_generator.py
│       └── maintenance_generator.py
├── docs/               # Documentation
├── scripts/            # Execution scripts
├── sql/                # SQL scripts
│   ├── schema.sql
│   ├── queries.sql
│   ├── snowflake_schema.sql
│   └── 03_optimization_indexes.sql
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## 9. Quick Start Command

Run everything in one command:

```bash
# Full pipeline execution
python -c "
from scripts.init_db import init_database
from scripts.data_generation import run_pipeline

print('Initializing database...')
init_database()
print('Generating data...')
run_pipeline(scale_factor=1)
print('Done!')
"
```

---

**Author:** Dody Dueñas  
**Project:** Henry M2 - FleetLogix Enterprise  
**Date:** April 2026
