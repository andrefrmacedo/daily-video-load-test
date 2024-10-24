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
    driver.find_element(By.XPATH, "/html/body/div/div[2]/div/form/div/div/button").click()

def create_virtual_large_event(driver):
    create_emp_event_url = BASE_URL + "/emp/events/new"
    current_datetime = datetime.now()
    event_title = "Test event " + str(current_datetime)
    date_format = "%Y-%m-%d %I:%M %p"
    start_date = current_datetime
    end_date = start_date + timedelta(hours=3)

    driver.get(create_emp_event_url)
    driver.find_element(By.ID, "name").send_keys(event_title)
    driver.find_element(By.XPATH, "/html/body/div[4]/div[4]/div/div/div/div[1]/div/form/div/div/div[4]/fieldset[1]/div/div/div[1]/label/input").click()
    driver.find_element(By.ID, "startDate").send_keys(start_date.strftime(date_format).lower())
    driver.find_element(By.ID, "endDate").send_keys(end_date.strftime(date_format).lower())
    Select(driver.find_element(By.ID, "timeZone")).select_by_visible_text("Berlin")
    driver.find_element(By.ID, "eventFormat-virtualEmployerHosted").click()
    driver.find_element(By.ID, "virtualEventType-handshakeVirtualEventLarge").click()
    driver.find_element(By.ID, "dailyVideoSession.recordingEnabled-No").click()
    
    mandatory_checkin = driver.find_element(By.ID, "employerKioskActive")
    if mandatory_checkin.is_selected():
        mandatory_checkin.click()

    driver.find_element(By.XPATH, "/html/body/div[4]/div[4]/div/div/div/div[1]/div/form/div/div/div[4]/div[14]/div/div[2]/div[2]/div").send_keys("test description")
    sleep(2)
    driver.find_element(By.XPATH, "/html/body/div[4]/div[4]/div/div/div/div[1]/div/form/div/div/div[9]/div/div/div/button").click()
    WebDriverWait(driver, 10).until(EC.title_contains(event_title))

    parsed_url = urlparse(driver.current_url)
    return parsed_url.path.split('/')[-1]

def stu_join_video(driver: webdriver):
    try:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "event-button"))).click() # Register for event
        sleep(5)
    except:
        print("Already registered for event")
    finally:
        WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "/html/body/main/div[2]/div/div/div[2]/header/aside/div[2]/p[2]/button"))).click() # Join event

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    # when a lot of browser windows are open, it takes quite a long time for daily elements to become visible
    WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div/div[1]/div/div/div[2]/div[1]/div/button"))).click() # Click Join
    WebDriverWait(driver, 30).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, "/html/body/div[2]/div/div[1]/div/div/div[2]/div/iframe")))
    WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, "broadcast-joining"))).click() # Click "Get started"

def send_chat_message(driver: webdriver, message_text):
    WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, "chat-controls")))
    driver.find_element(By.ID, "chat-controls").click()

    chat_element = WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div/div[1]/div[2]/div[3]/div/div/div[2]/div[2]/div/form/div/div[1]/div/div/div/textarea")))
    chat_element.send_keys(message_text)
    chat_element.submit()

    chat_message = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, "isLocal"))).text
    assert message_text in chat_message

def event_setup(employer_user: User):
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    
    login_user(driver, employer_user)
    event_id = create_virtual_large_event(driver)
    driver.quit()

    return event_id


    chrome_options = Options()
    chrome_options.add_argument("use-fake-ui-for-media-stream")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    driver.command_executor.set_timeout(10)

    login_user(driver, employer_user)
    emp_join_video(driver, event_id)
    assert_result = send_chat_message(driver, "Hello World!")

    sleep(90)
    driver.quit()

    return assert_result


    sleep(randint(1,10))
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    driver.command_executor.set_timeout(10)

    login_user(driver, student_user)
    stu_join_video(driver, event_id)
    assert_result = send_chat_message(driver, "Hello from " + student_user.email)

    sleep(60)
    driver.quit()

    return assert_result

student_email = os.getenv("STUDENT_EMAIL")
event_id = os.getenv("EVENT_ID")

chrome_options = Options()
chrome_options.binary_location= '/usr/bin/chromium'
chrome_options.add_argument("--headless")
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service('/usr/bin/chromedriver'), options=chrome_options)
user = User(student_email)

sleep(randint(0,120))
login_user(driver, user, event_id)
stu_join_video(driver)
send_chat_message(driver, "Hello from " + user.email)
sleep(3600)
