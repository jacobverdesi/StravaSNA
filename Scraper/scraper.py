from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import yaml
import json

options = webdriver.ChromeOptions()
options.add_argument("headless")
driver = webdriver.Chrome(options=options)


def login(url, usernameId, username, passwordId, password, submit_buttonId):
    driver.get(url)
    driver.find_element_by_id(usernameId).send_keys(username)
    driver.find_element_by_id(passwordId).send_keys(password)
    driver.find_element_by_id(submit_buttonId).click()


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


def main():
    pd.set_option('display.max_columns', 100)
    pd.set_option('display.width', 1000)
    conf = openYaml('login.yaml')
    myStEmail = conf['strava_user']['email']
    myStPassword = conf['strava_user']['password']
    login("https://www.strava.com/login", "email", myStEmail, "password", myStPassword, "login-button")
    driver.get("https://www.strava.com/segments/17747336")

    table = driver.find_element_by_id("results").get_attribute('innerHTML')
    df = parseTable(table)

    print(df)
    driver.close()


if __name__ == '__main__':
    main()
