from pf import app
#from .hello_world import app
from flask import request, make_response, jsonify, Response, redirect
from datetime import datetime, date, timedelta
from pf import mandateapi


from pf import dbfunc as db
from pf import jwtdecodenoverify as jwtnoverify
from dateutil import tz

from multiprocessing import Process
from decimal import Decimal

import psycopg2
import json
import jwt
import time
import calendar

@app.route('/getmandate',methods=['GET','POST','OPTIONS'])
def getmandate():
#This is called by fund data fetch service
    if request.method=='OPTIONS':
        print("inside getmandate options")
        return make_response(jsonify('inside getmandate options'), 200)  

    elif request.method=='POST':
        print("inside getmandate POST")

        print((request))        
        print(request.headers)
        payload= request.get_json() 
        print(payload)
        status = -1
        failreason = None
        
        prodtyp = payload.get('product', None)
        screenid = payload.get('screen', None)

        userid,entityid=jwtnoverify.validatetoken(request)
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print(userid,entityid,prodtyp,screenid)
        print('after')


        if prodtyp == "BSEMF":

            mand_recs,s,f = get_mf_mandate(userid,entityid,prodtyp,screenid)
            status, failreason = get_status(status, s, failreason, f)

            if status < 0:
                acct_recs,s,f = get_mf_acct(userid,entityid,prodtyp,screenid)
                status, failreason = get_status(status, s, failreason, f)
            print("#@$$%#*********************")
            print(status)
            print(failreason)
            print(mand_recs)
            print(acct_recs)
            print("#@$$%#*********************")

            recs = {
                'mandates'  : mand_recs if status < 0 else [],
                'accounts'  : acct_recs if status < 0 else [],
                'status'    : 'success' if status < 0 else 'failed',
                'failreason': failreason if status > 0 else None,
            }
        
        print(recs)
        if status < 0:
            return make_response(jsonify(recs), 200)
        else:
            return make_response(jsonify(recs), 400)

            

def get_mf_acct(userid,entityid,prodtyp,screenid):
        
    con,cur=db.mydbopncon()
    s = -1
    f = None
    command = cur.mogrify("""
                        select json_agg(a) from (
                        select clientacctype1 actype,clientaccno1 acnum,clientmicrno1 micr,clientifsccode1 ifsc,defaultbankflag1 def,i.bank||' '||i.branch||' '||i.city||' '||i.state bank, clientcode from webapp.uccclientmaster u 
                        JOIN webapp.BANKIFSCMASTER i ON i.ifsc = u.clientifsccode1
                        where u.ucclguserid = %s AND u.uccentityid = %s AND u.clientaccno1 IS NOT NULL
                        UNION
                        select clientacctype2 actype,clientaccno2 acnum,clientmicrno2 micr,clientifsccode2 ifsc,defaultbankflag2 def,i.bank||' '||i.branch||' '||i.city||' '||i.state bank, clientcode from webapp.uccclientmaster u 
                        JOIN webapp.BANKIFSCMASTER i ON i.ifsc = u.clientifsccode1
                        where u.ucclguserid = %s AND u.uccentityid = %s AND u.clientaccno2 IS NOT NULL
                        UNION
                        select clientacctype3 actype,clientaccno3 acnum,clientmicrno3 micr,clientifsccode3 ifsc,defaultbankflag3 def,i.bank||' '||i.branch||' '||i.city||' '||i.state bank, clientcode from webapp.uccclientmaster u 
                        JOIN webapp.BANKIFSCMASTER i ON i.ifsc = u.clientifsccode1
                        where u.ucclguserid = %s AND u.uccentityid = %s AND u.clientaccno3 IS NOT NULL
                        UNION
                        select clientacctype2 actype,clientaccno4 acnum,clientmicrno4 micr,clientifsccode4 ifsc,defaultbankflag4,i.bank||' '||i.branch||' '||i.city||' '||i.state bank, clientcode from webapp.uccclientmaster u 
                        JOIN webapp.BANKIFSCMASTER i ON i.ifsc = u.clientifsccode1
                        where u.ucclguserid = %s AND u.uccentityid = %s AND u.clientaccno4 IS NOT NULL
                        UNION
                        select clientacctype5 actype,clientaccno5 acnum,clientmicrno5 micr,clientifsccode5 ifsc,defaultbankflag5,i.bank||' '||i.branch||' '||i.city||' '||i.state bank, clientcode from webapp.uccclientmaster u 
                        JOIN webapp.BANKIFSCMASTER i ON i.ifsc = u.clientifsccode1 
                        where u.ucclguserid = %s AND u.uccentityid = %s AND u.clientaccno5 IS NOT NULL
                        ) as a
                        """,(userid,entityid,userid,entityid,userid,entityid,userid,entityid,userid,entityid,))

    cur, dbqerr = db.mydbfunc(con,cur,command)
    print("#########################################3")
    print(command)
    print("#########################################3")
    print(cur)
    print(dbqerr)
    print(type(dbqerr))
    print(dbqerr['natstatus'])
    
    if cur.closed == True:
        if(dbqerr['natstatus'] == "error"):
            dbqerr['statusdetails']="mf Account data fetch failed.  Contact support"
            s, f = get_status(s, 1, f, dbqerr['statusdetails'])
            return (None, s, f)

    if cur.rowcount > 1:
        status = 1
        failreason = "mf Account data fetch returned more rows"
        s, f = get_status(s, status, f, failreason)
        return (None, s, f)

    if cur.rowcount == 1:
        record = cur.fetchall()[0][0]
        print(record)
    
    actlist = [] if record == None else record
    db.mydbcloseall(con,cur)
    return (actlist, s, f)


def get_mf_mandate(userid,entityid,prodtyp,screenid):
    
    con,cur=db.mydbopncon()
    s = -1
    f = None
    command = cur.mogrify("""
                        select json_agg(a) from (
                        select man_bsemandateid,man_mandatetype,man_amount,man_accno,man_acctype,man_bankname,man_bankbranch,man_enddate,man_ifsc,man_startdate,man_status,man_internalid from webapp.mfmandatdetails m
                        where man_pfuserid = %s AND man_entityid = %s AND man_prodtype = %s
                        ) as a
                        """,(userid,entityid,prodtyp,))
    print(command)
    cur, dbqerr = db.mydbfunc(con,cur,command)
    print("#########################################3")
    print(command)
    print("#########################################3")
    print(cur)
    print(dbqerr)
    print(type(dbqerr))
    print(dbqerr['natstatus'])
    
    if cur.closed == True:
        if(dbqerr['natstatus'] == "error"):
            dbqerr['statusdetails']="mf Mandate fetch failed.  Contact support"
            s, f = get_status(s, 1, f, dbqerr['statusdetails'])
            return (None, s, f)

    if cur.rowcount > 1:
        status = 1
        failreason = "mf Mandate data fetch returned more rows"
        s, f = get_status(s, status, f, failreason)
        return (None, s, f)

    if cur.rowcount == 1:
        record = cur.fetchall()[0][0]
        print(record)
    
    mandlist = [] if record == None else record
    db.mydbcloseall(con,cur)
    return (mandlist, s, f)


@app.route('/mandateops',methods=['GET','POST','OPTIONS'])
def mandateops():
    if request.method=='OPTIONS':
        print("inside getmandate options")
        return make_response(jsonify('inside getmandate options'), 200)  

    elif request.method=='POST':
        print("inside getmandate POST")

        print((request))        
        print(request.headers)
        payload= request.get_json() 
        print(payload)
        status = -1
        failreason = None
        
        prodtyp = payload.get('product', None)
        screenid = payload.get('screenid', None)
        operation = payload.get('operation', None)
        data = payload.get('data', None)

        userid,entityid=jwtnoverify.validatetoken(request)
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print(userid,entityid,prodtyp,screenid,operation,data)
        print('after')


        if operation == "new" or operation == "edit":  # Save new mandate
            s, f = save_new_mandate(operation,prodtyp,userid,entityid,screenid,data)
            status, failreason = get_status(status, s , failreason, f)
            print("back after saving mandate")
            print(status, failreason)
            if status < 0:
                # we are ready to submit to BSE
                s,f = submit_mandate_to_bse(data['man_internalid'],entityid)
                status, failreason = get_status(status, s , failreason, f)
                print("back after submitting mandate to EXCHANGE")
                print(status, failreason)

        elif operation == "del":  # Save new mandate
            pass

        print(status)
        resp = {
            'status': 'success'
        }
        if status < 0:
            print("inside success")
            return make_response(jsonify(resp), 200)
        else:
            print("inside error")
            return make_response('error', 400)


def save_new_mandate(operation, product,userid,entityid,screenid,data):
    s = -1
    f = None
    con,cur=db.mydbopncon()
    status,failreason = db.mydbbegin(con,cur)
    s, f = get_status(s, 0 if status else -3 , f, failreason)

    #man_clientcode,man_memberid
    command = cur.mogrify("SELECT row_to_json(a) from (SELECT lguserid, lgclientcode, lgmembercode FROM webapp.userlogin WHERE lguserid = %s AND lgentityid = %s) as a;",(userid,entityid,))
    cur, dbqerr = db.mydbfunc(con,cur,command)
    print(command)
    if cur.closed == True:
        if(dbqerr['natstatus'] == "error"):
            dbqerr['statusdetails']="mf Mandate insert failed.  Contact support"
            s, f = get_status(s, 1, f, dbqerr['statusdetails'])
            return (None, s, f)
    print(cur.rowcount)
    if cur.rowcount > 0:
        print("&&&&&&&&&&&&&&&&&&&&&&&&")
        recor = cur.fetchall()[0][0]
        print(recor)
        print("&&&&&&&&&&&&&&&&&&&&&&&&")

    if product == "BSEMF":
        data['man_pfuserid'] = userid
        data['man_clientcode'] = recor['lgclientcode']
        data['man_memberid'] = recor['lgmembercode']
        
        data['man_prodtype'] = product
        savetimestamp = datetime.now()
        pfsavedate=savetimestamp.strftime('%Y%m%d') 
        pfsavetimestamp=savetimestamp.strftime('%Y/%m/%d %H:%M:%S')
        data['man_octime'] = pfsavetimestamp
        data['man_lmtime'] = pfsavetimestamp
        data['man_registdate'] = pfsavetimestamp
        data['man_entityid'] = entityid
        if (operation == "new"):                
            data['man_internalid'] = recor['lgclientcode']+savetimestamp.strftime('%d%m%Y%H%M%S%f')
        data['man_micr'] = data.get('man_micr','')
        #man_bsemandateid  
        #man_approveddate  
        #man_collectiontype
        #man_umrnnum       
        pfmflsordatajsondict = json.dumps(data)

        command = cur.mogrify("""
                INSERT INTO webapp.mfmandatdetails (man_internalid,man_pfuserid,man_clientcode,man_memberid,man_registdate,man_amount,man_mandatetype,man_accno,man_acctype,man_ifsc,man_prodtype,man_micr,man_bankname,man_startdate,man_enddate,
                    man_status,man_octime,man_lmtime,man_entityid)
                    select man_internalid,man_pfuserid,man_clientcode,man_memberid,now(),man_amount,man_mandatetype,man_accno,man_acctype,man_ifsc,man_prodtype,man_micr,man_bankname,man_startdate,man_enddate,
                    man_status,man_octime,man_lmtime,man_entityid from json_populate_record(NULL::webapp.mfmandatdetails,%s) where man_entityid = %s
                    ON CONFLICT ON CONSTRAINT man_unq_ref
                    DO
                        UPDATE 
                        SET man_registdate = %s,man_amount = %s,man_mandatetype = %s,man_accno = %s,man_acctype = %s,man_ifsc = %s,man_prodtype = %s,man_micr = %s,man_bankname = %s,man_startdate = %s,man_enddate = %s, man_status = %s, man_lmtime = %s
                """,(str(pfmflsordatajsondict),entityid,data['man_registdate'],data['man_amount'],data['man_mandatetype'],data['man_accno'],data['man_acctype'],data['man_ifsc'], data['man_prodtype'],data['man_micr'],data['man_bankname'],data['man_startdate'],data['man_enddate'],data['man_status'],data['man_lmtime'],))
        print(command)
        cur, dbqerr = db.mydbfunc(con,cur,command)
        if cur.closed == True:
            if(dbqerr['natstatus'] == "error"):
                dbqerr['statusdetails']="mf Mandate insert failed.  Contact support"
                s, f = get_status(s, 1, f, dbqerr['statusdetails'])
                return (s, f)
    if s < 0:
        con.commit()      
    else:
        con.rollback()
    
    db.mydbcloseall(con,cur)
    time.sleep(6)
    return (s, f)

def submit_mandate_to_bse(manintid, entityid):
    s = -1
    f = None
    con,cur=db.mydbopncon()

    command = cur.mogrify("""
                        select json_agg(a) from (
                        select man_internalid internalid, man_clientcode clientcode, man_amount amount, man_mandatetype mandatetype, man_accno accountno, man_acctype actype, 
                        man_ifsc ifsccode, man_micr micrcode, to_char(man_startdate, 'DD/MM/YYYY') startdate,to_char(man_enddate, 'DD/MM/YYYY') enddate 
                        from webapp.mfmandatdetails
                        where man_internalid = %s AND man_entityid = %s AND man_status = 'new'
                        ) as a
                        """,(manintid,entityid,))
    print(command)
    cur, dbqerr = db.mydbfunc(con,cur,command)
    print("#########################################3")
    print(command)
    print("#########################################3")
    print(cur)
    print(dbqerr)
    print(type(dbqerr))
    print(dbqerr['natstatus'])
    
    if cur.closed == True:
        if(dbqerr['natstatus'] == "error"):
            dbqerr['statusdetails']="mf Mandate fetch failed.  Contact support"
            s, f = get_status(s, 1, f, dbqerr['statusdetails'])
            return (s, f)

    if cur.rowcount > 1:
        failreason = "mf Mandate data fetch returned more rows"
        s, f = get_status(s, 0, f, failreason)
        db.mydbcloseall(con,cur)
        return (s, f)

    if cur.rowcount == 1:
        record = cur.fetchall()[0][0]
        print(record)
    
    bse_rec = {
        'data': record,
        'operation': 'mandate'
    }
    
    if s < 0:
        ###  this should be a API call in lambda  #####
        mandateresps = mandateapi.mandate(bse_rec)
        ###  this should be a API call in lambda  #####
        ''' Reponse from API
        if bse_resp['bsestatus'] = '100':
            mandate_resp = {'trans_code': 'NEW', 'order_type': 'mandcreate', 'int_mandate_id': bseorders['internalid'], 'bse_mandate_id': bse_resp['bserespmsg'],'bse_remarks': '', 'success_flag': bse_resp['bsestatus']}
        else:
            mandate_resp = {'trans_code': 'NEW', 'order_type': 'mandcreate', 'int_mandate_id': bseorders['internalid'], 'bse_mandate_id': '','bse_remarks': bse_resp['bserespmsg'], 'success_flag': bse_resp['bsestatus']}
        Reponse from API enddate
        '''
    else:
        mandateresps = None
    print("back to main after bse")
    print(mandateresps)
    if mandateresps == None:
        s, f = get_status(s, 1, f, "Failure in getting EXCHANGE respone.  Contact Support.")
        db.mydbcloseall(con,cur)
        return s, f
    else: 
        print(mandateresps)
        for mandateresp in mandateresps:
            status,failreason = db.mydbbegin(con,cur)
            s, f = get_status(s, 0 if status else -3 , f, failreason)
            if s > 0:
                return s, f

            if mandateresp['success_flag'] == '100':
                command = cur.mogrify("""
                            UPDATE webapp.mfmandatdetails SET man_bsemandateid = %s, man_status = %s WHERE man_internalid = %s and man_entityid = %s;
                        """,(mandateresp['bse_mandate_id'],'REGISTERED BY MEMBER', mandateresp['int_mandate_id'],entityid,))
            else:                
                statremarks = "ERROR" if mandateresp['bse_remarks'] == '' else mandateresp['bse_remarks']
                command = cur.mogrify("""
                UPDATE webapp.mfmandatdetails SET man_status = %s, man_bseremarks = %s WHERE man_internalid = %s and man_entityid = %s;
                """,("ERROR", statremarks, mandateresp['int_mandate_id'],entityid,))
            print(command)
            cur, dbqerr = db.mydbfunc(con,cur,command)
            if cur.closed == True:
                if(dbqerr['natstatus'] == "error"):
                    dbqerr['statusdetails']="mf Mandate status update after EXCHANGE response failed.  Contact support"
                    s, f = get_status(s, 1, f, dbqerr['statusdetails'])
                    print(s,f)
                    return (s, f)

            con.commit()
    
    db.mydbcloseall(con,cur)
    return s, f

def get_status(curstatus,newstatus,curreason, newreason):
    '''
    status =   
                -3 --> success
                -1 --> empty
                0  --> data error
                1  --> db error
                2  --> both data and db error
    '''
    print(curstatus,newstatus,curreason, newreason)
    if curstatus == None:
        curstatus = -1

    setstatus = -1
    
    if newstatus == -3:
        setstatus = -3
        setreason = None
    else:
        if curstatus < 0:
            setstatus = newstatus
        elif curstatus == 2:
            setstatus = curstatus
        elif curstatus == newstatus:
            setstatus = curstatus
        elif curstatus != newstatus:
            setstatus = 2

        if curreason and setstatus > -1:
            setreason = curreason + " | " + newreason
        else:
            setreason = newreason

    return -1 if setstatus == None else setstatus, setreason
