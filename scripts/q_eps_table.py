import psycopg2
from dotenv import load_dotenv
import os 
from pathlib import Path
import pandas as pd
import shutil

load_dotenv()
user = os.getenv("db_user")
password = os.getenv("db_password")
database = os.getenv("database")
db_host = os.getenv("db_host")
port = os.getenv("db_port")

def create_quarterly_eps_table(cursor, table_name, fp):
        with open(fp) as f:
            sql = f"COPY {table_name} FROM STDIN WITH CSV HEADER"
            cursor.copy_expert(sql, f)

def combine_csvs(eps_paths):
    save_fp = "combine_eps/"
    if os.path.exists(save_fp):
        shutil.rmtree(save_fp)

    download_dir = os.path.join(os.getcwd(), "combine_eps")
    os.makedirs(download_dir, exist_ok=True)

    curr_dfs = list()

    for i, path in enumerate(eps_paths):
        curr_dfs.append(pd.read_csv(path))
        if (i - 1) % 1000 == 0:
            combined = pd.concat(curr_dfs)
            curr_dfs = list()

            combined.to_csv(save_fp + f"combined_{i // 1000}.csv", index=False)
        
    if curr_dfs:
        combined = pd.concat(curr_dfs)
        combined.to_csv(save_fp + f"combined_{i // 1000}.csv", index=False)

conn = psycopg2.connect(
    dbname=database,
    user=user,
    password=password,
    host=db_host,
    port=port
)

if conn:
    print("Connected to database")

    table_name = "quarterly_eps"
    print(f"Starting {table_name} table recreation...")
    
    schema = f"""
    CREATE TABLE IF NOT EXISTS "{table_name}" (
    "cik" INT,
    "start" DATE,
    "end" DATE,
    "diluted_eps" FLOAT,
    "fiscal_year" FLOAT,
    "manually_calculated" FLOAT,
    "quarter" FLOAT
    );
    """

    # TODO
    # not enforced, but need to perform better preprocessing before insertion for: 
    # - PRIMARY KEY(cik, fiscal_year, quarter)  
    # - fiscal_year INT
    # - manually_calculated BOOLEAN
    # - quarter INT CHECK(quarter BETWEEN 1 AND 4)

    dir = Path("quarterly_eps_data/")
    eps_paths = list()
    for fp in dir.iterdir():
        if fp.is_file():
            eps_paths.append(fp)

    combine_csvs(eps_paths)
    dir = Path("combine_eps")
    combined_paths = list()
    for fp in dir.iterdir():
        if fp.is_file():
            combined_paths.append(fp)

    cursor = conn.cursor()
    cursor.execute(f"""
    DROP TABLE IF EXISTS "{table_name}";
    """)
    cursor.execute(schema)

    for i, fp in enumerate(combined_paths):
        create_quarterly_eps_table(cursor, table_name, fp)
        conn.commit()
        # print(f"{i} combined records inserted")
    
    conn.close()
    print(f"Finished {table_name} table recreation")