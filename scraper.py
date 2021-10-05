from selenium import webdriver
import yaml

options = webdriver.ChromeOptions()
#options.add_argument("headless")
driver = webdriver.Chrome(options=options,executable_path='C:\\Users\Jake\Desktop\CS CLASSES\Social Network Anaylsis\chromedriver.exe')


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


def main():
    conf = openYaml('login.yaml')
    myStEmail = conf['strava_user']['email']
    myStPassword = conf['strava_user']['password']
    login("https://www.strava.com/login", "email", myStEmail, "password", myStPassword, "login-button")
    driver.get("https://www.strava.com/segments/9846518")
    table=driver.find_element_by_id("results").get_attribute('innerHTML')
    print(table)

if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
