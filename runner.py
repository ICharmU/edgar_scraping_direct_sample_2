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
    


# expects edgar_scraping environment to be active
if __name__ == "__main__":
    download_daily_data()
    create_quarterly_eps()