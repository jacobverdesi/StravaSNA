from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import yaml

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
def parseTable(soup):
    rows=soup.find_all("tr")
    for i in rows:
        print(i)
def parseRow(row):
    return row
def main():
    conf = openYaml('login.yaml')
    myStEmail = conf['strava_user']['email']
    myStPassword = conf['strava_user']['password']
    login("https://www.strava.com/login", "email", myStEmail, "password", myStPassword, "login-button")
    driver.get("https://www.strava.com/segments/17747336")
    results=driver.find_element_by_id("results").get_attribute('innerHTML')
    table = BeautifulSoup(results, "html.parser").find('table')

    pd.set_option('display.max_columns', 100)
    pd.set_option('display.width', 1000)
    df = pd.read_html(str(table))[0]
    print(df)
    #parseTable(df)
    driver.close()
if __name__ == '__main__':
    main()

