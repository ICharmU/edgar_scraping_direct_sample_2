from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

ticker_url = r"https://sec.gov/include/ticker.txt"

driver = webdriver.Chrome() # options.add_argument('--headless=new') gets blocked. using headed browser
driver.get(ticker_url)
time.sleep(5)
html = driver.page_source
driver.quit()

if "Request Rate Threshold Exceeded" in html:
    raise Exception("Rate limit exceeded or invalid access method used. If using the '--headless=new' argument consider using a headed browser.")

text = BeautifulSoup(html, features="lxml")
canvas = text.find("pre").text.split()

print(len(canvas))
if len(canvas) % 2 == 1:
    raise ValueError("canvas has an odd number of entries. Cannot generate consistent dataframe.")

import pandas as pd

tickers = [ticker for i, ticker in enumerate(canvas) if i % 2 == 0]
ciks = [cik for i, cik in enumerate(canvas) if i % 2 == 1]

df = pd.DataFrame({"ticker": tickers, "cik": ciks})
df = df.astype({"ticker": str, "cik": int})

import os, shutil
from pathlib import Path

save_dir = "ticker_cik_mapping/"
if os.path.exists(save_dir):
    shutil.rmtree(save_dir)

download_dir = os.path.join(os.getcwd(), "ticker_cik_mapping")
os.makedirs(download_dir, exist_ok=True)

df.to_csv(Path(save_dir) / "mappings.csv", index=False)