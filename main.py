#!/usr/bin/python3

import random, string

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

#urls = input("Enter comma-seperated list of ip/domain names: ").split(",")
urls = ["localhost:5000"]

username = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
password = "Testpassword"
limitNumber = 5
profiles = ["bleepingcomputer", "zdnet"]

# Setting the options for running the browser driver headlessly so it doesn't pop up when running the script
#driverOptions = Options()
#driverOptions.headless = headless

# Setup the webdriver with options
profile = webdriver.FirefoxProfile()
profile.set_preference("permissions.default.image", 2)
driver = webdriver.Firefox(executable_path="./geckodriver", firefox_profile=profile)


for url in urls:
    print(f"\n\n---\n\nTesting {url}\n\n--\n\n")
    driver.get(url)

    print("Page loads") if driver.find_element_by_id("links").is_enabled() else exit()

    driver.get(f"{url}/signup")
    driver.find_element_by_id("username").send_keys(username);
    driver.find_element_by_id("password").send_keys(password);
    driver.find_element_by_id("confirmPassword").send_keys(password);
    submitButton = driver.find_element_by_id("submit")
    submitButton.click()

    print("User created successfully") if driver.find_elements_by_class_name("error-message")[0].text == "Created user, log in here." else exit()

    driver.get(f"{url}/signup")
    driver.find_element_by_id("username").send_keys(username);
    driver.find_element_by_id("password").send_keys(password + "g");
    driver.find_element_by_id("confirmPassword").send_keys(password + "g");
    submitButton = driver.find_element_by_id("submit")
    submitButton.click()

    print("Confirmed that the same user can't be created twice") if driver.find_elements_by_class_name("error-message")[0].text == "User already exists, log in here." else exit()

    driver.find_element_by_id("username").send_keys(username);
    driver.find_element_by_id("password").send_keys(password);
    submitButton = driver.find_element_by_id("submit")
    submitButton.click()

    print("User logged in successfully") if len(driver.find_elements_by_class_name("listview-item-checkbutton")) > 5 else exit()

    driver.get(f"{url}/config")

    for profile in profiles:
        driver.find_element_by_css_selector(f"label[for='{profile}-checkbox']").click()

    driver.find_element_by_class_name("form-control").send_keys(Keys.CONTROL, "a")
    driver.find_element_by_class_name("form-control").send_keys(Keys.BACKSPACE)
    driver.find_element_by_class_name("form-control").send_keys(str(limitNumber))
    driver.find_element_by_css_selector("label[for='readingmode-checkbox']").click()
    driver.find_element_by_css_selector("form[action='/']").submit()

    for element in driver.find_elements_by_class("col-sm-12"):

