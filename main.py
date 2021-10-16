#!/usr/bin/python3

import random, string

# Used for locating the details in the article description fields
import re

# Used for verifying that the feed properly sorts by date
from datetime import datetime, timezone

# For sleeping to allow page to load
import time

# Used for downloading the geckodriver
import os
import requests
import json
import tarfile


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

# Mozilla will have an api endpoint giving a lot of information about the latest releases for the geckodriver, from which the url for the linux 64 bit has to be extracted
def extractDriverURL():
    driverDetails = json.loads(requests.get("https://api.github.com/repos/mozilla/geckodriver/releases/latest").text)

    for platformRelease in driverDetails['assets']:
        if platformRelease['name'].endswith("linux64.tar.gz"):
            return platformRelease['browser_download_url']

# Downloading and extracting the .tar.gz file the geckodriver is stored in into the tools directory
def downloadDriver(driverURL):
    driverContents = requests.get(driverURL, stream=True)
    with tarfile.open(fileobj=driverContents.raw, mode='r|gz') as driverFile:
        driverFile.extractall()

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
