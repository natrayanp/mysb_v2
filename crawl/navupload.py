#!/usr/bin/env python

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, ErrorInResponseException, ElementNotVisibleException, UnexpectedAlertPresentException, NoAlertPresentException
from http.client import BadStatusLine

# for datetime processing
from pytz import timezone
from datetime import datetime, timedelta, date
from time import strptime, sleep
from dateutil.relativedelta import relativedelta
from dateutil import tz
import requests, zipfile, os, shutil 
from pathlib import Path
import psycopg2
 

#@app.route('/navdownload',methods=['GET','POST','OPTIONS'])
#example for model code http://www.postgresqltutorial.com/postgresql-python/transaction/
#should be called from mforderapi.
def navdownload():
    driver = init_driver("chrome",False)
    #driver = init_driver("firefox",False)
    
    #boddate = datetime.now().strftime('%d-%b-%Y')
    boddate = (datetime.now() + timedelta(days=-1)).strftime('%d-%b-%Y')
    boddates = (datetime.now() + timedelta(days=-1)).strftime('%d%m%Y')
    pathstr = "/home/natrayan/project/AwsProject/BSEStarMF/NAV/"
    ffilename = "NAVDWLD_" + boddates + ".txt"
    pfilename = "NAVDWLD_" + boddates + ".part"
    prt_file = Path(pathstr + pfilename)
    full_file = Path(pathstr + ffilename)

    try:
        #driver = login(driver)
        #print("login done")
        order_status_recs, driver = get_nav_file(driver,boddate,prt_file,full_file)
        print("get tran done")
        stat = import_to_db(pathstr + ffilename)
    finally:
        quit_driver(driver)
        print("finally done")
        #return order_status_recs

    #return order_status_recs


def import_to_db(filepa):  

    conn = psycopg2.connect("host=localhost dbname=amcdb user=postgres password=password123")
    cur = conn.cursor()
    
    #with open('/home/natrayan/project/AwsProject/BSEStarMF/NAV/NAVDWLD_18062018.txt', 'r') as f:
    with open(filepa, 'r') as f:    
        # Notice that we don't need the `csv` module.
        next(f)  # Skip the header row.
        cur.copy_from(f, 'webapp.navcurload', sep='|')
        
    conn.commit()

    return "ok"

def get_nav_file(driver, dt,prt_file,full_file):
    '''
    get NAV download from bsestarmf.in
    '''
    print("line 52: download NAV file")
    try:
        order_status_recs, driver = download_nav(driver, dt, prt_file, full_file)
        #order_status_recs, driver = find_order_status(driv = driver)
        # update status of all orders incl sip instalment orders
        #update_order_status(driver)
        return order_status_recs, driver

    except (TimeoutException, StaleElementReferenceException, ErrorInResponseException, ElementNotVisibleException):
        print("Retrying")
        return download_nav(driver, dt, prt_file, full_file)

    except (BadStatusLine):
        print("Retrying for BadStatusLine in login")
        driver = init_driver()     
        return download_nav(driver, dt, prt_file, full_file)




def download_nav(driv, dt, prt_file, full_file):
#P - PURHCASE, R - REDEMPTION
    driver = driv
    print("get find_order_status sttus")
    if dt:
        dt = dt
    else:
        dt = datetime.now().strftime('%d-%b-%Y')


    url = "https://bsestarmf.in/RptNavMaster.aspx"
    driver.get(url)
    print("Navigated to home page")

    date = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'txtToDate')))
    date.clear()
    date.send_keys(dt)
    sleep(1)
    viewbtn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="btnSubmit"]')))
    viewbtn.click()
    
    viewbtn = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'btnText')))
    sleep(1)
    viewbtn.click()

    #prt_file = Path("/home/natrayan/project/AwsProject/BSEStarMF/NAV/*.part")
    #full_file = Path("/home/natrayan/project/AwsProject/BSEStarMF/NAV/NAVDWLD_18062018.txt")

    while True:
        if prt_file.is_file():
            print("has part file")
            sleep(10)
        elif full_file.is_file():
            print("has full file")
            break
        else:
            print("has nside else")
            sleep(10)
    r = "0k"
    '''
    date.send_keys(dt)
    #date.send_keys(date_dict['date'].strftime("%d-%b-%Y"))
    sleep(2)    # needed as page refreshes after setting date
    # make_ready(driver)

    if frmclntcd == None or frmclntcd == '' or toclntcd == None or toclntcd == '':
        pass
    else:
        frmcltcd = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'txtFromCltCode')))
        frmcltcd.clear()
        frmcltcd.send_keys(frmclntcd)

        tocltcd = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'txtToCltCode')))
        tocltcd.clear()
        tocltcd.send_keys(toclntcd)

    element = driver.find_element_by_xpath('//*[@id="ddlBuySell"]')
    all_options = element.find_elements_by_tag_name("option")
    for option in all_options:
        print("Value is: %s" % option.get_attribute("value"))
        if option.get_attribute("value") == tran_type:
            #selected option purcharse or redemption as per tran_type
            option.click()

    element = driver.find_element_by_xpath('//*[@id="ddlOStatus"]')
    all_options = element.find_elements_by_tag_name("option")
    for option in all_options:
        print("Value is: %s" % option.get_attribute("value"))
        if option.get_attribute("value") == 'V':
            option.click()

    submit = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "btnSubmit")))
    submit.click()
    sleep(2)
    
    ## parse the table- find orders for this date
    table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//table[@class='glbTableD']/tbody")))
    print ('html loading done')
    rows = table.find_elements(By.XPATH, "tr[@class='tblERow'] | tr[@class='tblORow']")
    '''

    return r,driver



def init_driver(browsertyp = "chrome", headles = False):
# instantiate a browser with options object so you can set the size and headless preference
# intialises and returns the driver
    newpath = '/home/natrayan/project/AwsProject/BSEStarMF/NAV'
    if not os.path.exists(newpath):
        os.makedirs(newpath)   

    for the_file in os.listdir(newpath):
        file_path = os.path.join(newpath, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            #elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

    if browsertyp == "chrome":
        options = webdriver.ChromeOptions()
        options.add_experimental_option("prefs", {"download.default_directory": newpath})
        if headles:
            options.add_argument("--headless")
            options.add_argument("--window-size=1920x1080")
        driver = webdriver.Chrome(chrome_options=options)
    elif browsertyp == "firefox":
        options = webdriver.FirefoxProfile()
        options.set_preference("browser.download.dir", newpath)
        if headles:
            options.add_argument("--headless")
            options.add_argument("--window-size=1920x1080")

        driver = webdriver.Firefox(firefox_options=options)

    return driver    




def quit_driver(driver):
#Quit the driver
    driver.quit()


if __name__ == '__main__':
    xx = navdownload()  

#ddtopmenubar > ul > li:nth-child(6) > a
#export PATH=$PATH:/home/natrayan/project/AwsProject/puppeteer/geko







'''

def mforstaint(payload):
#intermediate function whcih can be called directly or api    
    driver = init_driver("chrome",False)
    #driver = init_driver("firefox",False)

    try:
        driver = login(driver)
        print("login done")
        order_status_recs, driver = get_transaction_status(driver,payload)
        print("get tran done")
    finally:
        quit_driver(driver)
        print("quit done")

    return jsonify(order_status_recs)


@app.route('/mforderallotpg_web',methods=['GET','POST','OPTIONS'])
#example for model code http://www.postgresqltutorial.com/postgresql-python/transaction/
#should be called from mforderapi.
def mforderallotpg_web():
    
    if request.method=='OPTIONS':
        print ("inside mforderallotpg_web options")
        return jsonify({'body':'success'})

    elif request.method=='POST':   
        print ("inside mforderallotpg_web post")
        print(request.headers)
        payload= request.get_json()
        #payload = request.stream.read().decode('utf8')    
        
        print("line 83:",payload)
        #check if client code is available in payload
        memcd = payload.get("member_code")
        
        if memcd == None or memcd == '':
            resp = make_response({'natstatus': 'error', 'statusdetails': 'No Member code provided in request'}, 400)
            return resp

        allotment_recs = mforalltint(payload)

        return allotment_recs

def mforalltint(payload):

    driver = init_driver("chrome",False)
    #driver = init_driver("firfox",False)

    try:
        driver = login(driver)
        allotment_recs, driver = get_allotments(driver,payload)
    finally:
        quit_driver(driver)

    return allotment_recs




def get_allotments(driver,payload):

    try:
        allotment_recs, driver = find_allotment(driver, payload.get("dt"), payload.get("member_code"))
        #allotment_recs, driver = find_allotment(driver,'','')
        # update status of all orders incl sip instalment orders
        #update_order_status(driver)
        return allotment_recs, driver

    except (TimeoutException, StaleElementReferenceException, ErrorInResponseException, ElementNotVisibleException):
        print("Retrying")
        return get_allotments(driver,payload)

    except (BadStatusLine):
        print("Retrying for BadStatusLine in login")
        driver = init_driver()     
        driver = login(driver)
        return get_allotments(driver,payload)

    

def find_allotment(driver, dt=None, mecd = None):
#P - PURHCASE, R - REDEMPTION
    if dt:
        dt = dt
    else:
        dt = datetime.now().strftime('%d-%b-%Y')


    url = settings.BSESTAR_ALLOTMENT_PG[settings.LIVE]
    driver.get(url)
    print("Navigated to order status page")

    date = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'txtToDate')))
    date.clear()
    date.send_keys(dt)
    sleep(2)    # needed as page refreshes after setting date


    submit = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "btnSubmit")))
    submit.click()
    sleep(2)

        ## parse the table- find orders for this date
    table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//table[@class='glbTableD']/tbody")))
    print ('html loading done')
    rows = table.find_elements(By.XPATH, "tr[@class='tblERow'] | tr[@class='tblORow']")

    allotment_recs = []
    for row in rows:
        fields = row.find_elements(By.XPATH, "td")
        recs = {
            'order_id' : fields[1].text,
            'order_dt' : fields[4].text,
            'scheme_code' : fields[5].text,
            'member_id' : fields[10].text,
            'folio_num' : fields[12].text,
            'client_code' : fields[15].text,
            'client_name' : fields[16].text,
            'alloted_nav' : fields[18].text,
            'alloted_unt' : fields[19].text,
            'alloted_amt' : fields[20].text,
            'remarks' : fields[22].text,
            'order_type' : fields[25].text,
            'order_subtype' : fields[33].text,
            'sipreg_num' : fields[26].text,
            'sipreg_dt' : fields[27].text,
            'dp_typ' : fields[32].text,
        }
        allotment_recs.append(recs)
    
    print("line 262:", allotment_recs)

    return allotment_recs, driver



def get_transaction_status(driver, payload):

    print("line 272: get transaction sttus")
    try:
        order_status_recs, driver = find_order_status(driver, payload.get("dt"), payload.get("tran_type"), payload.get("from_client_code"), payload.get("to_client_code"))
        #order_status_recs, driver = find_order_status(driv = driver)
        # update status of all orders incl sip instalment orders
        #update_order_status(driver)
        return order_status_recs, driver

    except (TimeoutException, StaleElementReferenceException, ErrorInResponseException, ElementNotVisibleException):
        print("Retrying")
        return get_transaction_status(driver,payload)

    except (BadStatusLine):
        print("Retrying for BadStatusLine in login")
        driver = init_driver()     
        driver = login(driver)
        return get_transaction_status(driver,payload)


def find_order_status(driv, dt=None, tran_type='P',frmclntcd = None,toclntcd = None):
#P - PURHCASE, R - REDEMPTION
    driver = driv
    print("get find_order_status sttus")
    if dt:
        dt = dt
    else:
        dt = datetime.now().strftime('%d-%b-%Y')


    url = settings.BSESTAR_ORDER_STATUS_PG[settings.LIVE]
    driver.get(url)
    print("Navigated to order status page")

    date = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'txtToDate')))
    date.clear()
    date.send_keys(dt)
    #date.send_keys(date_dict['date'].strftime("%d-%b-%Y"))
    sleep(2)    # needed as page refreshes after setting date
    # make_ready(driver)

    if frmclntcd == None or frmclntcd == '' or toclntcd == None or toclntcd == '':
        pass
    else:
        frmcltcd = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'txtFromCltCode')))
        frmcltcd.clear()
        frmcltcd.send_keys(frmclntcd)

        tocltcd = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'txtToCltCode')))
        tocltcd.clear()
        tocltcd.send_keys(toclntcd)

    element = driver.find_element_by_xpath('//*[@id="ddlBuySell"]')
    all_options = element.find_elements_by_tag_name("option")
    for option in all_options:
        print("Value is: %s" % option.get_attribute("value"))
        if option.get_attribute("value") == tran_type:
            #selected option purcharse or redemption as per tran_type
            option.click()

    element = driver.find_element_by_xpath('//*[@id="ddlOStatus"]')
    all_options = element.find_elements_by_tag_name("option")
    for option in all_options:
        print("Value is: %s" % option.get_attribute("value"))
        if option.get_attribute("value") == 'V':
            option.click()

    submit = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "btnSubmit")))
    submit.click()
    sleep(2)
    
    ## parse the table- find orders for this date
    table = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//table[@class='glbTableD']/tbody")))
    print ('html loading done')
    rows = table.find_elements(By.XPATH, "tr[@class='tblERow'] | tr[@class='tblORow']")

    order_status_recs = []
    for row in rows:
        fields = row.find_elements(By.XPATH, "td")
        recs = {
            'order_id' : fields[3].text,
            'status' : fields[18].text,
            'client_code' : fields[5].text,
            'scheme_code' : fields[7].text,
            'buy_sell' : fields[10].text
        }
        order_status_recs.append(recs)
    
    print("line 196:", order_status_recs)

    return order_status_recs, driver



'''


