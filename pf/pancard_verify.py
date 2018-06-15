from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.select import Select


# for datetime processing
from pytz import timezone
from datetime import datetime, timedelta, date
from time import strptime, sleep
from dateutil.relativedelta import relativedelta
from dateutil import tz


def pancard_verify(pan):
#verify pan status
    
    options = Options()
    #options.add_argument("--headless")
    #chrome_options.add_argument("--window-size=1920x1080")

    #driver = webdriver.Firefox(firefox_options=options)
    driver = webdriver.Chrome(chrome_options=options)


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
    #elem.send_keys('BODPM4264E')
    elem.send_keys(pan)
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
    
    pan_status = { 'pan_name' : name_str,
                   'kyc_status' : status_str,
                   'kyc_status_dt' : ''
                    }

    driver.close()
    return pan_status

    
    


    '''
    #ddtopmenubar > ul > li:nth-child(6) > a
    export PATH=$PATH:/home/natrayan/project/AwsProject/puppeteer/geko
    '''