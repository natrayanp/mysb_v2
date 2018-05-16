from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options

from dateutil import tz
from datetime import datetime
from datetime import date

options = Options()
#options.add_argument("--headless")
#chrome_options.add_argument("--window-size=1920x1080")


driver = webdriver.Firefox(firefox_options=options)
#driver = webdriver.Chrome(chrome_options=options)

'''
driver.get("https://camskra.com/")


#driver.get("file:///C:/Users/natrayanpalani.REG1/Desktop/new23.html")
#element = driver.find_element_by_xpath("//span[@class='ytp-menu-label-secondary']")

try:

    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "tbPanSrch"))
    )

finally:
    pass

print("after element")
elem = driver.find_element_by_name("ctl00$tbPanSrch")
elem.clear()
elem.send_keys('BNZPM2501F')
elem.send_keys(Keys.RETURN)

sst=True

se=True
while se:
    tx = driver.find_element_by_xpath('//*[@id="lblPanNo"]')
    txv = tx.get_attribute('textContent')
    print(txv)
    if (len(txv) > 7):
        se = False
print("waiting")
print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
driver.implicitly_wait(100) # seconds
print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print("waiting end")


name_str = driver.find_element_by_xpath('//*[@id="lblName"]').get_attribute('textContent')
status_str = driver.find_element_by_xpath('//*[@id="lblStatus"]').get_attribute('textContent')

print(name_str)
print(status_str)
 
#status_str values
# 1) KYC Not Registered (testing - AWXPR5832J)
# 2) KYC Registered-New KYC (testing - BNZPM2501F)
 
driver.close()
'''










# instantiate a chrome options object so you can set the size and headless preference
options = Options()
#options.add_argument("--headless")
#chrome_options.add_argument("--window-size=1920x1080")


#driver = webdriver.Firefox(firefox_options=options)
driver = webdriver.Chrome(chrome_options=options)
driver.get("https://bsestarmfdemo.bseindia.com")
assert "Mutual Fund System - Bombay Stock Exchange Limited" in driver.title
name = driver.find_element_by_name("txtUserId")
name.clear()
name.send_keys("1712301")

member = driver.find_element_by_name("txtMemberId")
member.clear()
member.send_keys("17123")

elem = driver.find_element_by_name("txtPassword")
elem.clear()
elem.send_keys('@654321')

myvalue = True
while myvalue:
    #present = wait.until(EC.text_to_be_present_in_element((By.NAME, "txtCaptcha"), "valueyouwanttomatch"))
    elem = driver.find_element_by_name("txtCaptcha").get_attribute('value')
    print (elem)
    if (len(elem) == 5):
        myvalue = False
print("outside while")

member = driver.find_element_by_name("btnLogin").click()


assert "WELCOME : NATRAYAN" not in driver.page_source


member = driver.find_element_by_xpath('//*[@id="ddtopmenubar"]/ul/li[6]/a')
member.click()

print("completed")
driver.close()


'''
#ddtopmenubar > ul > li:nth-child(6) > a
export PATH=$PATH:/home/natrayan/project/AwsProject/puppeteer/geko
'''