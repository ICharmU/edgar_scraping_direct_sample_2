from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import os
import time
import shutil

daily_xbrl_url = r"https://www.sec.gov/Archives/edgar/daily-index/xbrl/companyfacts.zip"

data_fp = "json_data/"
if os.path.exists(data_fp):
    shutil.rmtree(data_fp)

download_dir = os.path.join(os.getcwd(), "json_data")
os.makedirs(download_dir, exist_ok=True)

chrome_options = Options()
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "profile.default_content_settings.popups": 0
}
chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=chrome_options)
driver.get(daily_xbrl_url)

save_path = "json_data/companyfacts.zip"
while not os.path.exists(save_path):
    time.sleep(3)
driver.quit()

from zipfile import ZipFile

with ZipFile(save_path) as zip_object:
    zip_path = "json_data/"
    zip_object.extractall(zip_path)