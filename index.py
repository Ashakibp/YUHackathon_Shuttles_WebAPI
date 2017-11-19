from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time as t
from bottle import route, run, request, response, get, post
import json

class shuttleAPI():
    def __init__(self):
        #self.display = Display(visible=0, size=(800, 600))
        #self.display.start()
        self.driver = None
        self.aborting = False
        self.page_delay = 1


    def set_selenium_local_session(self):
        """Starts local session for a selenium server. Default case scenario."""
        if self.aborting:
            return self

        else:
            chromedriver_location = './chromedriver/chromedriver'
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')

            # managed_default_content_settings.images = 2: Disable images load, this setting can improve pageload & save bandwidth
            # default_content_setting_values.notifications = 2: Disable notifications
            # credentials_enable_service & password_manager_enabled = false: Ignore save password prompt from chrome
            # 'profile.managed_default_content_settings.images': 2,
            # 'profile.default_content_setting_values.notifications' : 2,
            # 'credentials_enable_service': False,
            # 'profile': {
            #   'password_manager_enabled': False
            # }

            chrome_prefs = {
                'intl.accept_languages': 'en-US'
            }
            chrome_options.add_experimental_option('prefs', chrome_prefs)
            self.driver = webdriver.Chrome(chromedriver_location, chrome_options=chrome_options)
        self.driver.implicitly_wait(self.page_delay)

        return self


    def logins(self, username, password):
        self.driver.get("https://www.yushuttles.com/")
        t.sleep(2)
        element = self.driver.find_element_by_id("user_login")
        element.send_keys(username)
        element = self.driver.find_element_by_id("user_pass")
        element.send_keys(password)
        t.sleep(2)
        self.driver.find_element_by_id("wp-submit").click()
        try:
            self.driver.find_element_by_id("login_error")
            return False
        except(Exception):
            pass
        if self.driver.current_url == "https://www.yushuttles.com/wp-login.php?action=logout":
            self.driver.get("https://www.yushuttles.com/wp-login.php?action=logout&_wpnonce=9ab014e949")
            self.logins(username, password)
        return True


    def gettimes(self, username, password, direction):
        self.logins(username, password)
        t.sleep(1)
        if(direction == "wilf"):
            self.driver.find_element_by_xpath(
                "//select[@name='app_select_services']/option[text()='Beren to Wilf Campus Shuttle']").click()
        if(direction == "beren"):
            self.driver.find_element_by_xpath(
                "//select[@name='app_select_services']/option[text()='Wilf to Beren Campus shuttle ']").click()
        self.driver.find_element_by_xpath("//*[@class='app_services_button']").click()
        t.sleep(.5)
        x = self.driver.find_elements_by_xpath("//*[@class='app_timetable_cell free']")
        time_ar = []
        for span in x:
            time_ar.append(span.get_attribute("title") + " " + span.text[8:].replace("\n", ""))
        return time_ar

    def bookrides(self, username, password, direction, times):
        try:
            t.sleep(.5)
            self.logins(username, password)
            t.sleep(1)
            if (direction == "wilf"):
                self.driver.find_element_by_xpath(
                    "//select[@name='app_select_services']/option[text()='Beren to Wilf Campus Shuttle']").click()
            if (direction == "beren"):
                self.driver.find_element_by_xpath(
                    "//select[@name='app_select_services']/option[text()='Wilf to Beren Campus shuttle ']").click()
            self.driver.find_element_by_xpath("//*[@class='app_services_button']").click()
            t.sleep(.5)
            time_element = self.driver.find_element_by_xpath("//*[@title='{0}']".replace("{0}", times))
            time_element.click()
            t.sleep(2)
            phone_field = self.driver.find_element_by_id("appointments-field-customer_phone")
            phone_field.send_keys(0000000000)
            self.driver.find_element_by_xpath("//*[@class='appointments-confirmation-button']").click()
            t.sleep(.5)
            return True
        except(Exception):
            return False
    def getrides(self, username, password):
        self.logins(username, password)
        self.driver.get("https://www.yushuttles.com/cancel-your-reservation/")


    def close_driver(self):
        self.driver.quit()
        #self.display.stop()

@get("/login/<username>/<password>")
def login(username, password):
    api = shuttleAPI()
    api.set_selenium_local_session()
    isTrue = api.logins(username, password)
    response.content_type = 'application/json'
    response_obj = {}
    response_obj["login"] = isTrue
    api.close_driver()
    returner = json.dumps(response_obj)
    return returner

@get("/gettimes/<username>/<password>/<direction>")
def get_times(username, password, direction):
    api = shuttleAPI()
    api.set_selenium_local_session()
    time_dict = api.gettimes(username, password, direction)
    time_obj = {"times" : time_dict}
    returner = json.dumps(time_obj)
    api.close_driver()
    response.content_type = 'application/json'
    return returner


@get("/bookride/<username>/<password>/<direction>/<time>")
def bookride(username, password,direction, time):
    api = shuttleAPI()
    api.set_selenium_local_session()
    returner = api.bookrides(username, password, direction, time)
    return_dict = {
        "worked": returner
    }
    response.content_type = 'application/json'
    return return_dict

@get("/getRides/<username>/<password>")
def getRides(username, password):
    api = shuttleAPI()
    api.set_selenium_local_session()
    time_dict = api.getrides(username, password)
    time_obj = {"times": time_dict}
    returner = json.dumps(time_obj)
    api.close_driver()
    response.content_type = 'application/json'
    return returner











@post("/login")
def login():
    response_json = json.load(request.body)
    username = response_json["username"]
    password = response_json["password"]
    api = shuttleAPI()
    api.set_selenium_local_session()
    isTrue = api.logins(username, password)
    response.content_type = 'application/json'
    response_obj = {}
    response_obj["login"] = isTrue
    api.close_driver()
    returner = json.dumps(response_obj)
    return returner

@post("/gettimes")
def get_times():
    response_json = json.load(request.body)
    username = response_json["username"]
    password = response_json["password"]
    direction = response_json["direction"]
    api = shuttleAPI()
    api.set_selenium_local_session()
    time_dict = api.gettimes(username, password, direction)
    time_obj = {"times" : time_dict}
    returner = json.dumps(time_obj)
    api.close_driver()
    response.content_type = 'application/json'
    return returner


@post("/bookride")
def bookride():
    response_json = json.load(request.body)
    username = response_json["username"]
    password = response_json["password"]
    direction = response_json["direction"]
    time = response_json["time"]
    api = shuttleAPI()
    api.set_selenium_local_session()
    returner = api.bookrides(username, password, direction, time)
    return_dict = {
        "worked": returner
    }
    response.content_type = 'application/json'
    return return_dict

@post("/getRides")
def getRides():
    responeJson = json.load(response.json())
    username = responeJson["username"]
    password = responeJson["password"]
    api = shuttleAPI()
    api.set_selenium_local_session()
    time_dict = api.getrides(username, password)
    time_obj = {"times": time_dict}
    returner = json.dumps(time_obj)
    api.close_driver()
    response.content_type = 'application/json'
    return returner

run()