import pandas as pd
from sqlalchemy import create_engine, text
import urllib.parse

db_user = 'postgres'
db_password = urllib.parse.quote_plus('PASSWORD') 
db_host = 'localhost'
db_port = '5432'
db_name = 'postgres' 

engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

schema_sql = """
CREATE SCHEMA IF NOT EXISTS client_ops;

DROP TABLE IF EXISTS client_ops.stg_hospital_records CASCADE;

CREATE TABLE client_ops.stg_hospital_records (
    record_id INT PRIMARY KEY,
    date TIMESTAMP,
    facility VARCHAR(100),
    department VARCHAR(100),
    er_wait_time_mins NUMERIC(10, 2),
    bed_turnover_hrs NUMERIC(10, 2),
    procurement_cost_usd NUMERIC(10, 2)
);

CREATE OR REPLACE VIEW client_ops.vw_diagnostic_anomalies AS
SELECT 
    record_id,
    date,
    facility,
    department,
    er_wait_time_mins,
    bed_turnover_hrs,
    procurement_cost_usd,
    
    CASE WHEN er_wait_time_mins > 45 THEN (er_wait_time_mins - 45) * (60.0 / 60.0) ELSE 0 END AS er_leakage_usd,
    CASE WHEN bed_turnover_hrs > 2.0 THEN (bed_turnover_hrs - 2.0) * 150.0 ELSE 0 END AS bed_leakage_usd,
    CASE WHEN procurement_cost_usd > 400 THEN (procurement_cost_usd - 400.0) ELSE 0 END AS proc_leakage_usd,

    (
        CASE WHEN er_wait_time_mins > 45 THEN (er_wait_time_mins - 45) * 1.0 ELSE 0 END +
        CASE WHEN bed_turnover_hrs > 2.0 THEN (bed_turnover_hrs - 2.0) * 150.0 ELSE 0 END +
        CASE WHEN procurement_cost_usd > 400 THEN (procurement_cost_usd - 400.0) ELSE 0 END
    ) AS total_variance_usd
FROM client_ops.stg_hospital_records;
"""

print("Building database schema...")
with engine.begin() as conn:
    conn.execute(text(schema_sql))

print("Loading 50K+ records into PostgreSQL...")
df = pd.read_csv('hospital_operations_data.csv')

df.to_sql('stg_hospital_records', 
          engine, 
          schema='client_ops', 
          if_exists='append', 
          index=False)

print("Data successfully loaded! The diagnostic view is ready.")
