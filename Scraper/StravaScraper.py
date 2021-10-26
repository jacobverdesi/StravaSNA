import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from bs4 import BeautifulSoup
from datetime import timedelta
import pandas as pd
import yaml
import json
import ast
from pathlib import Path

BASE_URL = "https://www.strava.com"

URL_LOGIN = "%s/login" % BASE_URL
URL_SEGMENT = "%s/segments/" % BASE_URL
URL_DASHBOARD = "%s/dashboard" % BASE_URL

SEGMENT_SLEEP = 5


def login(driver, url, usernameId, username, passwordId, password, submit_buttonId):
    """
    driver function to login to a login page
    directs to url finds username and password fields and enters data
    then finds submit id and clicks
    """
    driver.get(url)
    driver.find_element(By.XPATH, f'//input[@id=\"{usernameId}\"]').send_keys(username)
    driver.find_element(By.XPATH, f'//input[@id=\"{passwordId}\"]').send_keys(password)
    driver.find_element(By.XPATH, f'//button[@id=\"{submit_buttonId}\"]').click()
    driver.implicitly_wait(5)
    strUrl = driver.current_url
    if strUrl != "https://www.strava.com/login":
        print(f"Logged in as: {username}")
        return True
    print(f"Failed to Log in as: {username}")
    return False


def openYaml(filePath):
    """
    open yaml file and return datastream
    :param filePath:
    :return:
    """
    with open(filePath, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


def dumpYaml(filePath, data):
    """
    dump yaml file and return datastream
    :param filePath:
    :return:
    """
    with open(filePath, "w") as stream:
        return yaml.dump(data, stream)


def parseTable(table):
    """
    After selenium finds results div, parse the table contained in the html string
    Use bs4 to parse html and find the contained table
    Get table from html as pandas table

    Find each athlete by td and get data tracking properties and convert to json object
    Read list of json data into second dataframe

    combine dataframes
    :param table: string of HTML div containing a table object
    :return: combined pandas dataframe containing athletes data
    """
    soup = BeautifulSoup(table, "html.parser").find('table')  # reduce html string using bs4 parser
    athleteData = pd.read_html(str(soup))[0].drop("Rank", axis=1)  # get the table data and remove rank column

    dataTrackingProperties = soup.find_all("td", class_="athlete track-click")  # find each athlete

    for i in range(len(dataTrackingProperties)):
        # for each athlete read data-traking properties attribute and load back as json
        dataTrackingProperties[i] = json.loads(dataTrackingProperties[i].attrs.get("data-tracking-properties"))

    dtpDF = pd.DataFrame.from_records(dataTrackingProperties)  # read list of athlete data properties as dataframe
    combined = pd.concat([dtpDF, athleteData], axis=1, join="inner")  # merge the two dataframes
    return combined


def progress(percent=0, width=30):
    """
    simple progress meter display
    :param percent:
    :param width:
    :return:
    """
    left = width * percent // 100
    right = width - left
    print('\r[', '#' * left, ' ' * right, ']', f' {percent:.0f}%', sep='', end='', flush=True)


def getSegment(driver, id):
    driver.get(URL_SEGMENT + id)
    ended = False
    df = pd.DataFrame()
    active_page = 1
    max = 0
    print(f"Getting segment: {id}")
    while not ended:

        try:

            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, '//div[@id="results"]')))  # Wait for table to load
            table = driver.find_element(By.XPATH, '//div[@id="results"]').get_attribute('innerHTML')  # Get the table
            df = df.append(parseTable(table), ignore_index=True)  # Add to dataframe


        except TimeoutException:
            try:
                driver.find_element(By.XPATH, '//div[@class="alert alert-warning mt-md"]')
                print("Hazardous segment skipping")
                break
            except NoSuchElementException:

                print(f"Error trying to get table of segment: {id} on page {active_page}")
                return False, active_page

        if (active_page == 1):
            # Get total number of pages break if only one page
            try:
                max = int(driver.find_element(By.XPATH, '//ul[@class="pagination"]/li[last()-1]/a').get_attribute(
                    'innerHTML'))
            except:
                break

        progress(percent=int((active_page / max) * 100))
        active_page += 1

        try:
            if (driver.find_element(By.XPATH, '//ul[@class="pagination"]/li[last()]').get_attribute(
                    "class") == "next_page disabled"):
                break
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.XPATH, '//li[@class="next_page"]/a[@rel="next"]')))
            driver.find_element(By.XPATH, '//li[@class="next_page"]/a[@rel="next"]').click()
            WebDriverWait(driver, 3).until(
                EC.text_to_be_present_in_element(
                    (By.XPATH, '//li[@class="active"]/span'),
                    str(active_page)))

        except:
            if (driver.find_element(By.XPATH, '//div[@class="loading-panel"]')):
                print()
                print("Max requests today")
                return False, active_page
    print()
    if (len(df.index) > 0):
        df.to_csv(f"./Data/Master/Segments/{str(id)}.csv", index=False)
        print(df)
    return True, active_page


def getAllSegmentsFromDict(driver):
    base_path = Path(__file__).parent
    file_path = (base_path / "../Data/Master/segmentList.txt").resolve()
    totalPages = 0
    totalErrors = 0
    with open(file_path, 'r') as f:
        my_set = dict(ast.literal_eval(f.read()))
    try:
        for i in my_set:
            if not my_set[i]:
                # print(f"{i} {my_set[i]}")
                succeeded, pages = getSegment(driver, i)
                my_set[i] = succeeded
                totalErrors += int(not succeeded)
                totalPages += pages
                print(f"Made {pages} requests for total of {totalPages}")
                if totalErrors > 2:
                    raise Exception
                print("Sleeping")
                for i in range(SEGMENT_SLEEP):
                    progress(int(i / SEGMENT_SLEEP * 100))
                    time.sleep(1)
                print()
    except Exception as e:
        print(e)
        with open(file_path, 'w') as f:
            f.write(str(my_set))
            print("\nUpdated segmentList.txt")
    return totalErrors > 2


def main():
    pd.set_option('display.max_columns', 100)
    pd.set_option('display.width', 1000)
    conf = openYaml('Scraper/login.yaml')
    options = webdriver.ChromeOptions()
    # options.add_argument("--enable-automation")
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    # options.add_argument("--user-data-dir=C:\\Users\\Jake\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 2")

    options.add_argument("headless")

    for user in conf:
        myStEmail = conf[user]['email']
        myStPassword = conf[user]['password']

        if (time.time() - conf[user]['lastmaxed'] > 86400):
            driver = webdriver.Chrome(options=options)
            succeeded = login(driver, URL_LOGIN, "email", myStEmail, "password", myStPassword, "login-button")
            if succeeded:
                succeeded = getAllSegmentsFromDict(driver)
            if succeeded:
                conf[user]['lastmaxed'] = time.time()
                dumpYaml('Scraper/login.yaml', conf)

            driver.close()
        else:
            print(
                f"{myStEmail} is probably timedout {str(timedelta(seconds=86400 - (time.time() - conf[user]['lastmaxed'])))} remaining ")


if __name__ == '__main__':
    main()
