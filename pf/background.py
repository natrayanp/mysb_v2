from pf import app
from pf import dbfunc as db
from pf import jwtdecodenoverify as jwtnoverify
from pf import background as bgjobs
from pf import mforderapi
from pf import mfsiporder
from pf import webapp_settings


from datetime import datetime, date, timedelta
from multiprocessing import Process
from multiprocessing import Pool
import time
import json

from flask import request, make_response, jsonify, Response, redirect
import requests
import psycopg2
import jwt
from dateutil import tz

#@app.route('/mfordpaystatusbg',methods=['GET','POST','OPTIONS'])
#def mfordpaystatusbg():
def mfordpaystatusbg(submit_recs_json,userid,entityid):
    con,cur=db.mydbopncon()
    order_results = mforderapi.paystatusapi(submit_recs_json)

    for order_res in order_results:    
        command = cur.mogrify("BEGIN;")
        cur, dbqerr = db.mydbfunc(con,cur,command)
        if cur.closed == True:
            if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                dbqerr['statusdetails']="DB query failed, BEGIN failed"
            resp = make_response(jsonify(dbqerr), 400)
            return(resp)

        savetimestamp = datetime.now()
        pfsavetimestamp=savetimestamp.strftime('%Y-%m-%d %H:%M:%S')
        
        orderstatus = 'PPP'
        fndstatus= 'SUBM'
        bse_status_code = order_res.get('bse_status_code')
        bse_status_msg = order_res.get('bse_status_msg')
        segment = order_res.get('segment')
        order_id = order_res.get('order_id')
        print(bse_status_code)
        print(type(bse_status_code))

        if bse_status_code == '101':
            orderstatus = 'PER'
            fndstatus= 'COMPF'

        elif bse_status_code == '100':
            if bse_status_msg == 'PAYMENT NOT INITIATED FOR GIVEN ORDER' in bse_status_msg:
                #Payment not initiated so leave this in PPY status
                orderstatus = 'PPY'
                pass
            elif bse_status_msg == 'REJECTED' in bse_status_msg:
                orderstatus = 'PRJ'
                fndstatus= 'COMPF'

            elif bse_status_msg == 'AWAITING FOR FUNDS CONFIRMATION' in bse_status_msg:
                orderstatus = 'PAW'               

            elif bse_status_msg ==  'APPROVED' in bse_status_msg:
                orderstatus = 'PAP'
                fndstatus= 'COMPS'

            else:
                pass
        else:
            pass


        if orderstatus != 'PPP':
            command = cur.mogrify(
                """
                UPDATE webapp.mforderdetails SET mfor_orderstatus = %s, mfor_orderlmtime = %s WHERE mfor_orderstatus in ('PPP','PAW') AND mfor_orderid = %s AND mfor_producttype = %s AND mfor_pfuserid = %s AND mfor_entityid = %s;
                """,(orderstatus,pfsavetimestamp,order_id,segment,userid,entityid,))
            print(command)
            cur, dbqerr = db.mydbfunc(con,cur,command)
            if cur.closed == True:
                if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                    dbqerr['statusdetails']="mflist insert Failed"
                resp = make_response(jsonify(dbqerr), 400)
                return(resp)
            
            if orderstatus != 'SUBM':
                command = cur.mogrify(
                    """
                    UPDATE webapp.pfmforlist SET ormffndstatus = %s, ormflmtime = %s 
                    WHERE ormffndstatus in ('SUBM') 
                    AND orormfpflistid = (SELECT mfor_orormfpflistid FROM webapp.mforderdetails WHERE mfor_orderid = %s AND mfor_producttype = %s AND mfor_pfuserid = %s AND mfor_entityid = %s)                    
                    AND orormfprodtype = %s AND ororpfuserid = %s AND entityid = %s;
                    """,(fndstatus,pfsavetimestamp,order_id,segment,userid,entityid,segment,userid,entityid,))
                print(command)
                cur, dbqerr = db.mydbfunc(con,cur,command)
                if cur.closed == True:
                    if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                        dbqerr['statusdetails']="mflist insert Failed"
                    resp = make_response(jsonify(dbqerr), 400)
                    return(resp)

            con.commit()

        '''
        Approach 1:
            send CLIENT CODE and MEMEBER ID to registoer for the mforderapijobs.py to pick and check for the order status
        Approach 2:   (preferred)
            Dont get any registration, send all the data for the client code which are due and processed by BSE on this date
        command = cur.mogrify(
        """
        SELECT row_to_json(art) FROM (SELECT mfor_producttype,mfor_orderid,mfor_clientcode FROM webapp.mforderdetails WHERE mfor_orderstatus = 'PAP' AND mfor_pfuserid = %s AND mfor_entityid = %s) art;
        """,(userid,entityid,))
        print(command)
        cur, dbqerr = db.mydbfunc(con,cur,command)

        if cur.closed == True:
            if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                dbqerr['statusdetails']="pf Fetch failed"
            resp = make_response(jsonify(dbqerr), 400)
            return(resp)

        #Model to follow in all fetch
        records=[]
        for record in cur:  
            records.append(record[0])           
        print(records)

        order_recs = []
        for record in records:
            order_rec = {
                'client_code':record['mfor_clientcode'],
                'order_id': record['mfor_orderid'],
                'segment' : record['mfor_producttype']
                #'member_id' : ''
            }
            order_recs.append(order_rec)

        #st = mforderapi.mfallotcallbackreg()
        '''
    db.mydbcloseall(con,cur)

    return True