from pf import app
from flask import redirect, request,make_response
from datetime import datetime
from flask import jsonify
from pf import dbfunc as db
from pf import mforderapi_crawl as crawl

import jwt
import requests
import json
      
#This job to trigger at 4 PM IST
def mforderstatusschejb():

    payload = {"from_client_code":'', "to_client_code":'',"dt":'',"tran_type":'', "member_code": ''}
    orderstatusres = crawl.mforstaint(payload)
    
    '''
    recs = {
    'order_id' : fields[3].text,
    'status' : fields[18].text,
    'client_code' : fields[5].text,
    'scheme_code' : fields[7].text,
    'buy_sell' : fields[10].text
    }
    '''
    status = orderstatusres.get('status')
    orderstatus = 'PPP'
    order_id = orderstatusres.get('order_id')
    segment = 'BSEMF'
    savetimestamp = datetime.now()
    pfsavetimestamp=savetimestamp.strftime('%Y-%m-%d %H:%M:%S')
    client_code = orderstatusres.get('client_code')
    member_code = '17123'
    entity_id = 'IN'

    #mforderstatusschejb (Purchase & Redemption) - Runs every day at 3,4,5,6,7,8,9,10 PM IST
    if status == "ALLOTMENT DONE":
        orderstatus = 'ALT'
    elif status == "SENT TO RTA FOR VALIDATION":
        orderstatus = 'RTA'
    elif status == "ORDER CANCELLED BY USER":
        orderstatus = 'CAN'
    elif status == "PAYMENT NOT RECEIVED TILL DATE":
        orderstatus = 'PAW'

    con,cur=db.mydbopncon()

    command = cur.mogrify(
    """
    UPDATE webapp.mforderdetails SET mfor_orderstatus = %s, mfor_orderlmtime = %s WHERE 
    --mfor_orderstatus in ('PPP') AND 
    mfor_orderid = %s AND mfor_producttype = %s 
    AND mfor_entityid = %s AND mfor_clientcode = %s AND mfor_memberid = %s
    """,(orderstatus,pfsavetimestamp,order_id,segment,entity_id,client_code,member_code,))
    print(command)
    cur, dbqerr = db.mydbfunc(con,cur,command)
    if cur.closed == True:
        if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
            dbqerr['statusdetails']="mflist insert Failed"
        resp = make_response(jsonify(dbqerr), 400)
        return(resp)
    
    db.mydbcloseall(con,cur)

    return "ok"


def mforderallotschejb():
    
    payload = {"dt":'', "member_code": ''}    
    allotresp = crawl.mforalltint(payload)

    ''' Response message structure
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
    '''
    


    return "ok"
    #mforderstatusschejb - Runs every day at 5 (after mforderstatuspg_web),10 (after mforderstatuspg_web) PM IST