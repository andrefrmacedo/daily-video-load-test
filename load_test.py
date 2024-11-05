import os
from random import randint
from time import sleep
from datetime import datetime, timedelta
from dataclasses import dataclass
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "https://joinhandshake-staging.com"

@dataclass
class User:
    email: str
    password: str = "fishtank123!"

def login_user(driver: webdriver, user: User, event_id: int):
    # login_url = BASE_URL + "/login"
    stu_event_url = BASE_URL + "/stu/events/" + str(event_id)
    
    driver.get(stu_event_url)
    driver.find_element(By.ID, "email-address-identifier").send_keys(user.email)
    driver.find_element(By.XPATH, "/html/body/div/div[2]/div[2]/div[1]/div[3]/form/div/button").click()
    driver.find_element(By.ID, "password").send_keys(user.password)
    print("Logging in...")
    driver.find_element(By.XPATH, "//button[text()='Sign In']").click()

def stu_join_video(driver: webdriver):
    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "event-button"))).click() # Register for event
        sleep(5)
    except:
        print("Already registered for event")
    finally:
        WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, "/html/body/main/div[2]/div/div/div[2]/header/aside/div[2]/p[2]/button"))).click() # Join event

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    # when a lot of browser windows are open, it takes quite a long time for daily elements to become visible
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div/div[1]/div/div/div[2]/div[1]/div/button"))).click() # Click Join
    WebDriverWait(driver, 30).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "/html/body/div[2]/div/div[1]/div/div/div[2]/div/iframe")))
    WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, "broadcast-joining"))).click() # Click "Get started"

def send_chat_message(driver: webdriver, message_text):
    WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, "chat-controls")))
    driver.find_element(By.ID, "chat-controls").click()

    chat_element = WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div/div[1]/div[2]/div[3]/div/div/div[2]/div[2]/div/form/div/div[1]/div/div/div/textarea")))
    chat_element.send_keys(message_text)
    chat_element.submit()

    chat_message = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, "isLocal"))).text
    assert message_text in chat_message

print("Starting up")
student_email = os.getenv("STUDENT_EMAIL")
print("Running as " + student_email)
event_id = os.getenv("EVENT_ID")
print("Event ID: " + event_id)

chrome_options = Options()
chrome_options.binary_location= '/usr/bin/chromium'
chrome_options.add_argument("--headless")
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")

driver = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=chrome_options)
user = User(student_email)

print("Sleep for random time between 0s and 3m")
sleep(randint(0,180))
print("Starting test...")
login_user(driver, user, event_id)
print("Joining video...")
stu_join_video(driver)
print("Sending chat message...")
send_chat_message(driver, "Hello from " + user.email)
print("Sleeping for 1h...")
sleep(3600)
