# Edgar Scraping (Direct) Sample Code  

Scripts:
* download_daily_json.py - Downloads companyfacts.zip from [here](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) and extracts the JSON contents  
* create_quarterly_eps.py - Processes the JSON files from above by finding company identifiers and diluted EPS data  
* runner.py - Runs all scripts in order  


Running Scripts:
1. Create a conda environment using edgar_scraping.yml  
2. In a terminal run `conda activate edgar_scraping`  
3. In the same terminal run `python runner.py`
