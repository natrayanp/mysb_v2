''' 
Author: Natrayan
Description: crawl BSEStar web portal (bsestrmf.in) to update transaction status
    because API endpoints are not provided for this. These crawling functions are resilient to handle
    common crawling exceptions because crawling often encounters errors in html rendering or data loading
'''

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1366x768")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--test-type")
chrome_options.add_argument("--ignore-certificate-errors")



# https://sites.google.com/a/chromium.org/chromedriver/downloads
chrome_driver = '/usr/bin/chromedriver'

driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver)

driver.get("http://bsestarmfdemo.bseindia.com/Index.aspx")

userid=WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "txtUserId")))
memberid=WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "txtMemberId")))
password=WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "txtPassword")))
userid.send_keys('1712301')
memberid.send_keys('17123')
password.send_keys('@654321')
submit = driver.find_element_by_id("btnLogin")
submit.click()
print("Logged in")

'''
try:
    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "aspNetHidden")))
finally:
    pass
#english_link = driver.find_element_by_id("txtUserId")
#element.clear()
#element.send_keys("Olabode")
#element.send_keys(Keys.RETURN)
'''
driver.get_screenshot_as_file("basefile.png")