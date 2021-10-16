#!/usr/bin/python3

import random, string

# Used for locating the details in the article description fields
import re

# Used for verifying that the feed properly sorts by date
from datetime import datetime, timezone

import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

urls = input("Enter comma-seperated list of ip/domain names: ").split(",")

username = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
password = "Testpassword"

limitNumber = 20
profiles = ["bleepingcomputer", "zdnet", "threatpost"]

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

    # Need to be here to allow the page to load properly
    time.sleep(1)

    print(len(driver.find_elements_by_class_name("col-sm-12")))
    print("Limiting the number of articles work") if len(driver.find_elements_by_class_name("col-sm-12")) == limitNumber else exit()

    DetailPatterns = {
            "publisher":    re.compile(r'(?<=Publisher: )\w*'),
            "publishDate":  re.compile(r'(?<=Published: ).*')
            }


    print(f"Verifying {limitNumber} elements")
    lastTime = datetime.now(timezone.utc).astimezone()
    for i in range(len(driver.find_elements_by_class_name("col-sm-12"))):
        print(i, end=" ")

        currentElementDesc = driver.find_elements_by_class_name("source")[i].text
        currentPublisher = DetailPatterns['publisher'].search(currentElementDesc).group(0)
        currentTime = datetime.strptime(DetailPatterns['publishDate'].search(currentElementDesc).group(0), '%Y-%m-%d %H:%M:%S%z')

        if currentPublisher not in profiles: print("\nPublisher-check failed"); exit()
        if currentTime > lastTime: print("\nDate-check failed"); exit()
        lastTime = currentTime

    print("\nLimiting sources work")
    print("Sorts properly by date")

    print(f"Verifying reading-mode of {limitNumber} elements")
    for i,element in enumerate(driver.find_elements_by_class_name("col-sm-12")):
        print(i, end=" ")

        linkLocation = element.find_element_by_xpath("./child::a").get_attribute("href")

        driver.get(linkLocation)
        if len(driver.find_elements_by_css_selector("li")) < 4: print(f"Reading mode doesn't seem to render properly for {linkLocation}"); exit()
        driver.back()

    print("Reading mode works")

    driver.get(f"{url}/logout")

    print("Logged out successfuly") if driver.find_elements_by_class_name("listview-item-checkbutton") == [] else exit()
