# Edgar Scraping (Direct) Sample Code  

Scripts:
* download_daily_json.py - Downloads companyfacts.zip from [here](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) and extracts the JSON contents  
* create_quarterly_eps.py - Processes the JSON files from above by finding company identifiers and diluted EPS data
* cik_ticker_map.py - Goes [here](https://sec.gov/include/ticker.txt) to download current tickers associated with CIK
* ticker_mappings.py - Create ticker mapping table in postgres
* q_eps_table.py - Create quarterly eps table in postgres
* runner.py - Runner file for extracting/processing/loading data in appropriate order


Running Scripts:
1. Create a conda environment using edgar_scraping.yml  
2. In a terminal run `conda activate edgar_scraping`  
3. In the same terminal run `python runner.py`
