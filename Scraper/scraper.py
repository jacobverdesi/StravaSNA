from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import yaml

options = webdriver.ChromeOptions()
#options.add_argument("headless")
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
    soup = BeautifulSoup(table, "html.parser").find('table')

    pd.set_option('display.max_columns', 100)
    pd.set_option('display.width', 1000)
    dtp = soup.find_all("td", class_="athlete track-click")
    for i in dtp:
        print(i.attrs.get("data-tracking-properties"))
        print("==============================")
    df = pd.read_html(str(soup))[0]
    print(df)
def parseRow(row):
    return row
def main():
    conf = openYaml('login.yaml')
    myStEmail = conf['strava_user']['email']
    myStPassword = conf['strava_user']['password']
    login("https://www.strava.com/login", "email", myStEmail, "password", myStPassword, "login-button")
    driver.get("https://www.strava.com/segments/17747336")

    table=driver.find_element_by_id("results").get_attribute('innerHTML')
    parseTable(table)

   # driver.close()
if __name__ == '__main__':
    main()

