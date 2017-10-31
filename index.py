from selenium import webdriver
import time
from bottle import route, run, request, response, get
import json

# add this line
def login(webdriver, username, password):
    driver = webdriver
    driver.get("https://www.yushuttles.com/")
    time.sleep(1)
    element = driver.find_element_by_id("user_login")
    element.send_keys(username)
    element = driver.find_element_by_id("user_pass")
    element.send_keys(password)
    driver.find_element_by_id("wp-submit").click()
    if driver.current_url == "https://www.yushuttles.com/wp-login.php?action=logout":
        driver.get("https://www.yushuttles.com/wp-login.php?action=logout&_wpnonce=9ab014e949")
        login(driver, username, password)
    return True


def gettimes(username, password, direction):
    driver = webdriver.Chrome("/Users/Aaron/work/YUSHUTTLESSUX/chromedriver/chromedriver")
    time.sleep(.5)
    login(driver, username, password)
    if(direction == "wilf"):
        pass
    if(direction == "beren"):
        pass
    x = driver.find_elements_by_xpath("//*[@class='app_timetable_cell free']")
    time_dict = {}
    for span in x:
        time_dict[span.get_attribute("title")] = span.text[8:].replace("/n", "")
    driver.quit()
    return time_dict

def bookrides(username, password, times):
    driver = webdriver.Chrome("/Users/Aaron/work/YUSHUTTLESSUX/chromedriver/chromedriver")
    time.sleep(.5)
    login(driver, username, password)
    time_element = driver.find_element_by_xpath("//*[@title='{0}']".replace("{0}", times))
    print(time_element.text)
    time_element.click()

@get("/gettimes/<username>/<password>/<direction>")
def get_times(username, password, direction):
    time_dict = gettimes(username, password, direction)
    time_obj = {"times" : time_dict}
    returner = json.dumps(time_obj)
    response.content_type = 'application/json'
    return returner


@get("/bookride/<username>/<password>/<time>")
def bookride(username, password, time):
    bookrides(username, password, time)


run()