import sys
import subprocess

def download_daily_data():
    '''
    delete and redownloads the most recent companyfacts.zip file
    Save data in /json_data
    '''
    script_path = "download_daily_json.py"

    print("Starting daily SEC data extraction...")
    try:
        subprocess.run([sys.executable, script_path])
        print("Downloaded and extracted daily SEC data")
    except Exception as e:
        print("Failed to download daily data. Halting program.")
        print(e)
        raise Exception()
    
def create_quarterly_eps():
    '''
    Converts annual diluted eps figures to quarterly figures.
    Saves processed csvs in /quarterly_eps_data
    '''
    script_path = "create_quarterly_eps.py"
    print("Creating quarterly EPS...")
    try:
        subprocess.run([sys.executable, script_path])
        print("Created quarterly EPS figures")
    except Exception as e:
        print("Failed to create quarterly EPS figures. Halting program")
        print(e)
        raise Exception()
    
def create_cik_mapping():
    '''
    Maps CIKs to current tickers.
    Saves processed csv in /ticker_cik_mapping
    '''
    script_path = "cik_ticker_map.py"
    print("Mapping CIKs to tickers...")
    try:
        subprocess.run([sys.executable, script_path])
        print("Mapped CIKs to tickers")
    except Exception as e:
        print("Failed to map CIKs to tickers. Halting program")
        print(e)
        raise Exception()
    
def insert_cik_mapping():
    '''
    Inserts CIK-ticker mappings into Postgres
    '''
    script_path = "ticker_mappings.py"
    print("Inserting CIK-ticker mappings into Postgres...")
    try:
        subprocess.run([sys.executable, script_path])
        print("Inserted CIK-ticker mappings")
    except Exception as e:
        print("Failed to insert CIK-ticker mappings. Halting program")
        print(e)
        raise Exception()
    
def insert_quarterly_eps():
    '''
    Inserts quarterly EPS into Postgres
    '''
    script_path = "q_eps_table.py"
    print("Inserting quarterly EPS into Postgres...")
    try:
        subprocess.run([sys.executable, script_path])
        print("Inserted quarterly EPS mappings")
    except Exception as e:
        print("Failed to insert quarterly EPS. Halting program")
        print(e)
        raise Exception()

# expects edgar_scraping environment to be active
if __name__ == "__main__":
    # data retrieval
    RETRIEVE_DATA = False
    if RETRIEVE_DATA:
        download_daily_data()
        create_quarterly_eps()

    create_cik_mapping()

    # database insertion
    insert_cik_mapping()
    insert_quarterly_eps()