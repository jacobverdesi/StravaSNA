import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import yaml
import json
import ast
from pathlib import Path


options = webdriver.ChromeOptions()
# options.add_argument("--enable-automation")
options.add_argument("--disable-web-security")
options.add_argument("--allow-running-insecure-content")
# options.add_argument("--user-data-dir=C:\\Users\\Jake\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 2")


driver = webdriver.Chrome(options=options)

BASE_URL = "https://www.doogal.co.uk/strava.php"
import sys, signal
def signal_handler(signal, frame):
    print("\nprogram exiting gracefully")
    sys.exit(0)

def main():
    base_path = Path(__file__).parent
    file_path = (base_path / "../Data/Master/segmentList.txt").resolve()
    with open(file_path, 'r') as f:
        my_set = set(ast.literal_eval(f.read()))
    driver.get(BASE_URL)
    time.sleep(2)
    driver.find_element(By.XPATH, '//button[@aria-label="AGREE"]').click()
    time.sleep(2)
    driver.find_element(By.XPATH, '//input[@id="nearestRadio"]').click()
    print(my_set)
    prevLen=len(my_set)
    try:
        while(True):
            time.sleep(2)

            table = driver.find_element_by_id("segments-table").get_attribute('innerHTML')
            soup = BeautifulSoup(table, "html.parser").find('table')
            for tr in soup.select('tr[data-id]'):
                my_set.update([str(tr['data-id'])])
            newLen=len(my_set)
            print(f"Added {newLen-prevLen} new segments for total of {newLen}")
            prevLen=newLen
    except KeyboardInterrupt:
        with open(file_path, 'w') as f:
            f.write(str(my_set))
            print(f"Saved {len(my_set)} segments to the file")
if __name__ == '__main__':
    main()
