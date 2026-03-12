import psycopg2
from dotenv import load_dotenv
import os 
from pathlib import Path
import pandas as pd
import shutil

def create_mapping_table(cursor, table_name, fp):
        with open(fp) as f:
            sql = f"COPY {table_name} FROM STDIN WITH CSV HEADER"
            cursor.copy_expert(sql, f)

load_dotenv()
user = os.getenv("db_user")
password = os.getenv("db_password")
database = os.getenv("database")
db_host = os.getenv("db_host")
port = os.getenv("db_port")

conn = psycopg2.connect(
    dbname=database,
    user=user,
    password=password,
    host=db_host,
    port=port
)

if conn:
    print("Connected to database")
    
    table_name = "tickers"
    print(f"Starting {table_name} table recreation...")

    schema = f"""
    CREATE TABLE IF NOT EXISTS "{table_name}" (
    "ticker" VARCHAR(20),
    "cik" INT
    );
    """

    cursor = conn.cursor()
    cursor.execute(f"""
    DROP TABLE IF EXISTS "{table_name}";
    """)
    cursor.execute(schema)

    mapping_fp = Path("ticker_cik_mapping") / "mappings.csv"
    create_mapping_table(cursor, table_name, mapping_fp)
    conn.commit()

    conn.close()
    print(f"Finished {table_name} table recreation")
    
