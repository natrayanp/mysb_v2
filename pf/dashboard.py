from pf import app
from pf import dbfunc as db
from pf import jwtdecodenoverify as jwtnoverify

from datetime import datetime, date, timedelta
from multiprocessing import Process
from multiprocessing import Pool
import json
import time

from flask import request, make_response, jsonify, Response, redirect
import psycopg2
import requests
import jwt
from dateutil import tz

@app.route('/dashfetchdata',methods=['POST','OPTIONS'])
def dashfetchdata():
#This is called by fund data fetch service
    if request.method=='OPTIONS':
        print("inside dashfetchdata options")
        return make_response(jsonify('inside dashfetchdata options'), 200)  

    elif request.method=='POST':
        print("inside dashfetchdata POST")
        print((request))        
        print(request.headers)
        userid,entityid=jwtnoverify.validatetoken(request)
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print(userid,entityid)

        payload= request.get_json() 
        print(payload)

        pfid = payload.get('pfid', None)
        prodtyp = payload.get('prodtyp', None)
        fundid = payload.get('fundid', None)
        offset = payload.get('offset', 0)
        # data required for dashboard
        datarequired = payload.get('datareq', None)
        # pffull - PF details + Product summary
        # prodfull - funds under the Product 
        # fndsum - Fund transactions under the pf
        # fndfull - Fund transactions under the pf

        print('after')
        #time.sleep(1)

        pfsum_record = None
        pf_prodwise_record = None
        prod_det_record = None
        fund_det_record = None
        request_status = None
        failure_reason = None
        
        
        if datarequired == None:
            request_status = "failed"
            failure_reason = "No details on the data requirment provided by client"

        elif datarequired == "pffull": 
            #This is for the dashboard page
            pfsum_record, request_status, failure_reason = get_dashbord_data(datareq="pfsumrec",pfid=pfid,entityid=entityid,offset=offset)
            pf_prodwise_record, request_status, failure_reason  = get_dashbord_data(datareq="prodsumrec",pfid=pfid,entityid=entityid,offset=offset)

        elif datarequired == "prodfull":
            prod_det_record, request_status, failure_reason = get_dashbord_data(datareq="fundsumrec",prodtyp=prodtyp,pfid=pfid,entityid=entityid,offset=offset)
        
        elif datarequired == "fndfull":
            fund_det_record, request_status, failure_reason = get_dashbord_data(datareq="funddetrec",fundid=fundid,prodtyp=prodtyp,pfid=pfid,entityid=entityid,offset=offset)
        
        # Check for DB error and send user friendly error msg to front end
        if request_status == "dbfail":
            request_status = "failed"
            failure_reason = "Data base Error contact Adminstrator"
        elif request_status == "datafail":
            request_status = "failed"
            failure_reason = "Data Error contact Adminstrator"


        records = {
            'pfsumrec'      :  {} if pfsum_record == None else pfsum_record,             # pffull
            'prodsumrec'    :  [] if pf_prodwise_record == None else pf_prodwise_record, # pffull (product summary for a PF)
            'fundsumrec'    :  {} if prod_det_record == None else prod_det_record,       # prodfull
            'funddetrec'    :  {} if fund_det_record == None else fund_det_record,       # fundfull
            'status'        :  "success" if request_status == None else request_status,
            'failreason'    :  "" if failure_reason == None else failure_reason
        }

    time.sleep(1)
    print("data records:")
    print(records)

    
    if records['status'] == "success":
        return make_response(jsonify(records), 200)
    else:
        return make_response(jsonify(records), 400)

    
def get_dashbord_data(datareq,pfid=None,prodtyp=None,fundid=None,fromdt=None,todt=None,entityid=None,offset=0):
    con,cur=db.mydbopncon()
    print(con)
    print(cur)
    status = None
    failreason = None
    print(datareq,pfid,entityid,offset,prodtyp,fundid,fromdt,todt)

    if pfid == None:
        status = "datafail"
        if failreason:
            failreason = failreason + "pfid is not None|"
        else:
            failreason = "pfid is not None|"
    if entityid == None:
        status = "datafail"
        if failreason:
            failreason = failreason + "entity id is None|"
        else:
            failreason = "entity id is None|"
    if prodtyp ==None:
        if datareq == "fundsumrec" or datareq == "funddetrec": 
            status = "datafail"
            if failreason:
                failreason = failreason + "product type id is None|"
            else:
                failreason = "product type id is None|"
    if fundid ==None:
        if datareq == "funddetrec" : 
            status = "datafail"
            if failreason:
                failreason = failreason + "Fund id is None|"
            else:
                failreason = "Fund id is None|"
    print("status: %s and Failreason: %s",(status,failreason,))
    
    if datareq == "pfsumrec": 
        #This is for the dashboard page        
        if status == None:
            #cur.execute("select row_to_json(art) from (select a.*, (select json_agg(b) from (select * from pfstklist where pfportfolioid = a.pfportfolioid ) as b) as pfstklist, (select json_agg(c) from (select * from pfmflist where pfportfolioid = a.pfportfolioid ) as c) as pfmflist from pfmaindetail as a where pfuserid =%s ) art",(userid,))
            #command = cur.mogrify("select row_to_json(art) from (select a.*,(select json_agg(b) from (select * from webapp.pfstklist where pfportfolioid = a.pfportfolioid ) as b) as pfstklist, (select json_agg(c) from (select c.*,(select json_agg(d) from (select * from webapp.pfmforlist where orormflistid = c.ormflistid AND ormffndstatus='INCART' AND entityid=%s) as d) as ormffundorderlists from webapp.pfmflist c where orportfolioid = a.pfportfolioid ) as c) as pfmflist from webapp.pfmaindetail as a where pfuserid =%s AND entityid=%s) art",(entityid,userid,entityid,))
            command = cur.mogrify(
                """
                SELECT row_to_json(b) FROM (
                    SELECT dpos_pfportfolioid AS pfid, sum(dpos_invamount) AS invamt,sum(dpos_curvalue) AS curval,sum(dpos_totalpnl) AS pnl, (sum(dpos_curvalue)/sum(dpos_invamount))*100 AS percentgr
                    FROM webapp.dailyposition WHERE dpos_pfportfolioid = %s AND dpos_entityid = %s
                    GROUP BY dpos_pfportfolioid
                ) b;
                """,(pfid,entityid,))
            
    elif datareq == "prodsumrec":
        if status == None:
            command = cur.mogrify(
                """
                SELECT json_agg(b) FROM (
                    SELECT 
                        dpos_producttype AS prodtyp,
                        CASE 
                            WHEN dpos_producttype = 'BSEMF' THEN 'MUTUAL FUNDS'
                            WHEN dpos_producttype = 'SGB' THEN 'SGB'
                            WHEN dpos_producttype = 'EQ' THEN 'Equity'
                            WHEN dpos_producttype = 'HEQ' THEN 'Home Equity'
                        END AS product,	
                        dpos_pfportfolioid AS pfid,
                        sum(dpos_invamount) AS invamt,sum(dpos_curvalue) AS curval,sum(dpos_totalpnl) AS pnl, (sum(dpos_curvalue)/sum(dpos_invamount))*100 AS percentgr
                    FROM webapp.dailyposition WHERE dpos_pfportfolioid = %s AND dpos_entityid = %s
                    GROUP BY dpos_producttype,dpos_pfportfolioid
                ) b;
                """,(pfid,entityid,))

    elif datareq == "fundsumrec": 
        #This is for the dashboard details page
        print(status)
        print(failreason)
        if status == None:
            command = cur.mogrify(
                """
                SELECT json_agg(b) FROM (
                    SELECT          
                        dpos_schemecd AS schemecode,
                        b.fnddisplayname as schemename,
                        dpos_producttype AS prodtyp,
                        CASE                         
                            WHEN dpos_producttype = 'BSEMF' THEN 'MUTUAL FUNDS'                        
                            WHEN dpos_producttype = 'SGB' THEN 'SGB'                        
                            WHEN dpos_producttype = 'EQ' THEN 'Equity'                        
                            WHEN dpos_producttype = 'HEQ' THEN 'Home Equity' 
                        END AS product,
                        dpos_pfportfolioid AS pfid,
                        sum(dpos_unit) AS units, sum(dpos_avgnav) AS avgnav, sum(dpos_curnav) AS curnav, sum(dpos_invamount) AS invamt,sum(dpos_curvalue) AS curval,sum(dpos_totalpnl) AS pnl, (sum(dpos_curvalue)/sum(dpos_invamount))*100 AS percentgr
                    FROM webapp.dailyposition a
                    LEFT JOIN webapp.fundmaster b ON b.fndschcdfrmbse = dpos_schemecd 
                    WHERE dpos_producttype = %s AND dpos_pfportfolioid = %s AND dpos_entityid = %s
                    GROUP BY dpos_schemecd,b.fnddisplayname,dpos_producttype,dpos_pfportfolioid
                ) b;
                """,(prodtyp,pfid,entityid,))		
            
    elif datareq == "funddetrec": 
        #This is for the dashboard details page
        
        if status == None:
            command = cur.mogrify(
                """
                SELECT json_agg(b) FROM (
                    SELECT
                        tran_orderdate AS trandate,
                        tran_schemecd AS schemecode,
                        fndmas.fnddisplayname as schemename,
                        tran_producttype AS prodtyp,
                        CASE
                            WHEN tran_producttype = 'BSEMF' THEN 'MUTUAL FUNDS'
                            WHEN tran_producttype = 'SGB' THEN 'SGB'
                            WHEN tran_producttype = 'EQ' THEN 'Equity'
                            WHEN tran_producttype = 'HEQ' THEN 'Home Equity'
                        END AS product,
                        tran_pfportfolioid AS pfid, tran_unit AS units, tran_nav AS trannav, tran_invamount AS invamt,
                        (
                            SELECT fndnav.navc_value curnav
                            FROM webapp.navcurload fndnav
                            WHERE fndnav.navc_date = (SELECT MAX(A.navc_date) FROM webapp.navcurload A WHERE A.navc_schmcdbse = tran.tran_schemecd)
                            AND fndnav.navc_schmcdbse = tran.tran_schemecd
                        ) AS curnav                        
                    FROM webapp.trandetails tran
                    LEFT JOIN webapp.fundmaster fndmas ON fndmas.fndschcdfrmbse = tran_schemecd 
                    WHERE tran_schemecd = %s AND tran_producttype = %s AND tran_pfportfolioid = %s AND tran_entityid = %s
                    ORDER BY tran_orderdate,tran_schemecd,tran_producttype,tran_pfportfolioid
                    OFFSET %s
                ) b;
                """,(fundid, prodtyp, pfid, entityid, offset,))	
        
    print(command)
    cur, dbqerr = db.mydbfunc(con,cur,command)
    print(cur)
    print(dbqerr)
    print(type(dbqerr))
    print(dbqerr['natstatus'])

    if cur.closed == True:
        if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
            status = "dbfail"
            failreason = "pf product wise fetch failed with DB error"
            print(status)
            
    if cur.rowcount > 1:
        status = "dbfail"
        failreason = "pf product wise fetch returned more rows"
        print(status)

    record = None
    data_record = None
    if cur.rowcount == 1:
        record = cur.fetchall()
    
    if record:
        data_record = record[0][0]
    
    print(data_record)
    
    db.mydbcloseall(con,cur)


    return data_record, status, failreason

@app.route('/dashchart',methods=['POST','OPTIONS'])
def dashchart():
    #This is called by fund data fetch service
    if request.method=='OPTIONS':
        print("inside dashchart options")
        return make_response(jsonify('inside dashchart options'), 200)  

    elif request.method=='POST':
        print("inside dashchart POST")
        print((request))        
        print(request.headers)
        userid,entityid=jwtnoverify.validatetoken(request)
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print(userid,entityid)

        payload= request.get_json()
        print(payload)
        data = payload
        print(data)
        
        pfid = data.get('pfid', None)
        prodtyp = data.get('prodtyp', None)
        fundid = data.get('fundid', None)
        fromdt = None
        todt = None
        # data required for dashboard
        datarequired = payload.get('datareq', None)
        # pffull - PF full data
        # prodfull - funds under the Product 
        # pffull - Fund transactions under the pf

        pffulldata = None
        prodfulldata = None
        fundfulldata = None
        request_status = None
        failure_reason = None

        if datarequired == None:
            request_status = "failed"
            failure_reason = "No details on the data requirment provided by client"

        elif datarequired == 'pffull':
            pffulldata, request_status, failure_reason = get_char_data("pffulldata",pfid,prodtyp,fundid,fromdt,todt,entityid)

        elif datarequired == 'prodfull':
            prodfulldata, request_status, failure_reason = get_char_data("prodfulldata",pfid,prodtyp,fundid,fromdt,todt,entityid)
            
        elif datarequired == 'fndfull':
            fundfulldata, request_status, failure_reason = get_char_data("fundfulldata",pfid,prodtyp,fundid,fromdt,todt,entityid)

        # Check for DB error and send user friendly error msg to front end
        if request_status == "dbfail":
            request_status = "failed"
            failure_reason = "Chart Data base Error contact Adminstrator"
        elif request_status == "datafail":
            request_status = "failed"
            failure_reason = "Chart Data Error contact Adminstrator"


    chart_data = {
        'pffulldata'  :     [] if pffulldata == None else pffulldata,
        'prodfulldata':     [] if prodfulldata == None else prodfulldata,
        'fundfulldata':     [] if fundfulldata == None else fundfulldata,
        'status'      :     'success' if request_status == None else request_status,
        'failreason'  :     '' if failure_reason == None else failure_reason
    }

    time.sleep(2)
    print("chart data records:")
    print(chart_data)

    
    if chart_data['status'] == "success":
        return make_response(jsonify(chart_data), 200)
    else:
        return make_response(jsonify(chart_data), 400)

def get_char_data(datareq,pfid,prodtyp,fundid,fromdt,todt,entityid):
    status  = None 
    failreason = None 
    con,cur=db.mydbopncon()        
    print(con)
    print(cur)
    pf_record = None


    if pfid == None:
        status = "datafail"
        if failreason:
            failreason = failreason + "pfid is not None|"
        else:
            failreason = "pfid is not None|"
    if entityid == None:
        status = "datafail"
        if failreason:
            failreason = failreason + "entity id is None|"
        else:
            failreason = "entity id is None|"
    if prodtyp ==None:
        if datareq == "prodfulldata" or datareq == "fundfulldata": 
            status = "datafail"
            if failreason:
                failreason = failreason + "product type id is None|"
            else:
                failreason = "product type id is None|"
    if fundid ==None:
        if datareq == "fundfulldata" : 
            status = "datafail"
            if failreason:
                failreason = failreason + "Fund id is None|"
            else:
                failreason = "Fund id is None|"
    print("status: %s and Failreason: %s",(status,failreason,))



    if datareq == "pffulldata":
        command = cur.mogrify(
        """
        SELECT json_agg(info)
        FROM (
            SELECT json_build_array("Date","investment","Growth") AS info
            FROM 
                (
                        SELECT dpos_date AS Date,SUM(dpos_invamount) AS investment, SUM(dpos_curvalue) AS Growth FROM webapp.dailyposition_hist
                        WHERE dpos_pfportfolioid = %s AND dpos_entityid = %s
                        GROUP BY dpos_date
                        UNION ALL
                        SELECT dpos_date AS Date,SUM(dpos_invamount) AS investment, SUM(dpos_curvalue) AS Growth FROM webapp.dailyposition
                        WHERE dpos_pfportfolioid = %s AND dpos_entityid = %s
                        GROUP BY dpos_date
                ) AS x("Date","investment","Growth")
        ) as t;
        """,(pfid,entityid,pfid,entityid,))
        
    if datareq == "prodfulldata":
        command = cur.mogrify(
        """
        SELECT json_agg(info)
        FROM (
            SELECT json_build_array("Date","investment","Growth") AS info
            FROM 
                (
                        SELECT dpos_date AS Date,SUM(dpos_invamount) AS investment, SUM(dpos_curvalue) AS Growth FROM webapp.dailyposition_hist
                        WHERE dpos_producttype = %s AND dpos_pfportfolioid = %s AND dpos_entityid = %s
                        GROUP BY dpos_date                            
                        UNION ALL
                        SELECT dpos_date AS Date,SUM(dpos_invamount) AS investment, SUM(dpos_curvalue) AS Growth FROM webapp.dailyposition
                        WHERE dpos_producttype = %s AND dpos_pfportfolioid = %s AND dpos_entityid = %s
                        GROUP BY dpos_date
                ) AS x("Date","investment","Growth")
        ) as t;
        """,(prodtyp,pfid,entityid,prodtyp,pfid,entityid,))
    
    if datareq == "fundfulldata":
        #This is for the fund details page
        command = cur.mogrify(
        """
        SELECT json_agg(info)
        FROM (
            SELECT json_build_array("Date","investment","Growth") AS info
            FROM 
                (
                        SELECT dpos_date AS Date,SUM(dpos_invamount) AS investment, SUM(dpos_curvalue) AS Growth FROM webapp.dailyposition_hist
                        WHERE dpos_schemecd = %s AND dpos_producttype = %s AND dpos_pfportfolioid = %s AND dpos_entityid = %s
                        GROUP BY dpos_date                            
                        UNION ALL
                        SELECT dpos_date AS Date,SUM(dpos_invamount) AS investment, SUM(dpos_curvalue) AS Growth FROM webapp.dailyposition
                        WHERE dpos_schemecd = %s AND dpos_producttype = %s AND dpos_pfportfolioid = %s AND dpos_entityid = %s
                        GROUP BY dpos_date
                ) AS x("Date","investment","Growth")
        ) as t;
        """,(fundid,prodtyp,pfid,entityid,fundid,prodtyp,pfid,entityid,))
        
    print(command)
    cur, dbqerr = db.mydbfunc(con,cur,command)
    print("#########################################3")

    print(cur)
    print(dbqerr)
    print(type(dbqerr))
    print(dbqerr['natstatus'])

    if cur.closed == True:
        if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
            status = "dbfail"
            failreason = "pf product wise fetch failed with DB error"
            print(status,failreason)
            
    if cur.rowcount > 1:
        status = "dbfail"
        failreason = "pf product wise fetch returned more rows"
        print(status,failreason)

    if cur.rowcount == 1:
        record = cur.fetchall()[0][0]
        print(record)
        if record:
            record.insert(0,['Date', 'Investment', 'Growth'])
        print(record)               

    
    return record, status, failreason