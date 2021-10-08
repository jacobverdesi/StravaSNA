import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import yaml
import json

options = webdriver.ChromeOptions()
# options.add_argument("--enable-automation")
options.add_argument("--disable-web-security")
options.add_argument("--allow-running-insecure-content")
# options.add_argument("--user-data-dir=C:\\Users\\Jake\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 2")


options.add_argument("headless")
driver = webdriver.Chrome(options=options)

BASE_URL = "https://www.strava.com"

URL_LOGIN = "%s/login" % BASE_URL
URL_SEGMENT = "%s/segments/" % BASE_URL
URL_DASHBOARD = "%s/dashboard" % BASE_URL


def login(url, usernameId, username, passwordId, password, submit_buttonId):
    driver.get(url)
    driver.find_element_by_id(usernameId).send_keys(username)
    driver.find_element_by_id(passwordId).send_keys(password)
    driver.find_element_by_id(submit_buttonId).click()
    print(f"Logged in as: {username}")


def openYaml(filePath):
    with open(filePath, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)


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
    left = width * percent // 100
    right = width - left
    print('\r[', '#' * left, ' ' * right, ']', f' {percent:.0f}%', sep='', end='', flush=True)


def getSegment(id):
    driver.get(URL_SEGMENT + str(id))
    errored = False
    df = pd.DataFrame()
    active_page = 1
    max = 0
    while not (errored):
        WebDriverWait(driver, 3).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, '//li[@class="active"]/span'),
                str(active_page)))

        if (active_page == 1):
            max = int(driver.find_element(By.XPATH, '//ul[@class="pagination"]/li[8]/a').get_attribute('innerHTML'))
        progress(percent=int((active_page / max) * 100))

        active_page = int(driver.find_element(By.XPATH, '//li[@class="active"]/span').get_attribute('innerHTML')) + 1
        table = driver.find_element_by_id("results").get_attribute('innerHTML')
        try:

            driver.find_element(By.XPATH, '//li[@class="next_page"]/a[@rel="next"]').click()

        except:
            errored = True
            pass
        df = df.append(parseTable(table), ignore_index=True)
    print()
    driver.get(URL_DASHBOARD)
    df.to_csv(f'Data/Master/Segments/{str(id)}.txt', index=False)
    print(df)


def main():
    pd.set_option('display.max_columns', 100)
    pd.set_option('display.width', 1000)
    conf = openYaml('login.yaml')
    myStEmail = conf['strava_user']['email']
    myStPassword = conf['strava_user']['password']

    # login(URL_LOGIN, "email", myStEmail, "password", myStPassword, "login-button")
    # getSegment(17747336)

    if 'headless' in options.arguments:
        driver.close()


if __name__ == '__main__':
    main()
