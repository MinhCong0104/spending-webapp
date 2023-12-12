# import requests
# from bs4 import BeautifulSoup
# from langchain.agents import tool
# from selenium import webdriver
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
#
#
# def auto_check_in(user, pw, url):
#     """
#     Get DXY from investing.com
#     :return:
#     """
#     # setup page
#     options = Options()
#     # options.add_argument('--headless')
#     # options.add_argument('--no-sandbox')
#     # options.add_argument('--single-process')
#     # options.add_argument('--disable-dev-shm-usage')
#     # options.add_argument('--enable-javascript')
#     driver = webdriver.Chrome(options=options)
#     wait = WebDriverWait(driver, 50)
#
#     # get login page
#     driver.get(f"https://{url}.bachasoftware.com/web/login#cids=1&action=663&menu_id=482")
#     # find username/email field and send the username itself to the input field
#     # driver.find_element(By.ID, "login").send_keys(user)
#     # find password input field and insert password as well
#     # driver.find_element(By.ID, "password").send_keys(pw)
#     # click login button
#     # driver.find_element(By.CLASS_NAME, "btn-primary").click()
#
#
#     print()
#     # check-in
#     css = "body > div.o_action_manager > div > div > div > div.o_hr_attendance_kiosk_mode.flex-grow-1.flex-md-grow-0.card.pb-3.px-0.px-lg-5.\{\{kioskModeClasses.\?.kioskModeClasses.\:.\'\'.\}\} > div.row > div:nth-child(1) > a"
#     wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, css)))
#     driver.find_element(By.CSS_SELECTOR, css).click()
#
#     # driver.close()
#
# url = "demo-odoo16"
# # url = "int"
# login = "congtm.bhsoft@gmail.com"
# password = "Mc010401"
# auto_check_in(login, password, url)

import time
import random
from datetime import datetime
import webbrowser
import pyautogui

now = datetime.now()
ss = random.randint(5, 20)
action_time = datetime.strptime(f"18:00:{ss}", "%H:%M:%S").replace(day=now.day, month=now.month, year=now.year)
time.sleep((action_time - now).total_seconds())
webbrowser.open('https://int.bachasoftware.com/web#cids=1&menu_id=482&action=663')
time.sleep(3)
pyautogui.click(x=2800, y=410, clicks=1)
pyautogui.click(x=2800, y=800, clicks=1)
