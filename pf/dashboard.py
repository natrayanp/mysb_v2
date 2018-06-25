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

@app.route('/dashpfdet',methods=['POST','OPTIONS'])
def dashpfdet():
#This is called by fund data fetch service
    if request.method=='OPTIONS':
        print("inside dashpfonly options")
        return make_response(jsonify('inside dashpfonly options'), 200)  

    elif request.method=='POST':
        print("inside dashpfonly POST")
        print((request))        
        print(request.headers)
        userid,entityid=jwtnoverify.validatetoken(request)
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print(userid,entityid)
    
        payload= request.get_json() 
        print(payload)

        pfid = payload
        print('after')
        #time.sleep(1)
        con,cur=db.mydbopncon()
        
        print(con)
        print(cur)
        
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
        print(command)
        cur, dbqerr = db.mydbfunc(con,cur,command)
        print("#########################################3")
        
        print(cur)
        print(dbqerr)
        print(type(dbqerr))
        print(dbqerr['natstatus'])

        if cur.closed == True or cur.rowcount > 1:
            if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                dbqerr['statusdetails']="pf sum Fetch failed"
            resp = make_response(jsonify(dbqerr), 400)
            return(resp)

        pfsum_record = None
        if cur.rowcount == 1:
            pfsum_record = cur.fetchall()

        print(pfsum_record)

     #cur.execute("select row_to_json(art) from (select a.*, (select json_agg(b) from (select * from pfstklist where pfportfolioid = a.pfportfolioid ) as b) as pfstklist, (select json_agg(c) from (select * from pfmflist where pfportfolioid = a.pfportfolioid ) as c) as pfmflist from pfmaindetail as a where pfuserid =%s ) art",(userid,))
        #command = cur.mogrify("select row_to_json(art) from (select a.*,(select json_agg(b) from (select * from webapp.pfstklist where pfportfolioid = a.pfportfolioid ) as b) as pfstklist, (select json_agg(c) from (select c.*,(select json_agg(d) from (select * from webapp.pfmforlist where orormflistid = c.ormflistid AND ormffndstatus='INCART' AND entityid=%s) as d) as ormffundorderlists from webapp.pfmflist c where orportfolioid = a.pfportfolioid ) as c) as pfmflist from webapp.pfmaindetail as a where pfuserid =%s AND entityid=%s) art",(entityid,userid,entityid,))
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
        print(command)
        cur, dbqerr = db.mydbfunc(con,cur,command)
        print("#########################################3")
        
        print(cur)
        print(dbqerr)
        print(type(dbqerr))
        print(dbqerr['natstatus'])

        if cur.closed == True or cur.rowcount > 1:
            if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                dbqerr['statusdetails']="pf product wise fetch failed"
            resp = make_response(jsonify(dbqerr), 400)
            return(resp)
        
        pf_prodwise_record = None
        if cur.rowcount == 1:
            pf_prodwise_record = cur.fetchall()
        
        print(pf_prodwise_record)
        
        records = {
            'sumrec'   :  {} if pfsum_record == None else pfsum_record[0][0],
            'prodrecs' :  {} if pf_prodwise_record == None else pf_prodwise_record[0][0]
        }
        print("portfolio sum and product wise records returned for user: " + userid + " and portfolio id : " + pfid )        
            
        print(records)
        return json.dumps(records)



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
        # data required for dashboard
        datarequired = payload.get('datareq', None)
        # pffull - PF details + Product summary
        # prodfull - funds under the Product 
        # pffull - Fund transactions under the pf

        print('after')
        #time.sleep(1)
        con,cur=db.mydbopncon()

        print(con)
        print(cur)
        pfsum_record = None
        pf_prodwise_record = None
        prod_det_record = None
        fund_record = None
        fund_det_record = None
        request_status = None
        failure_reason = None
        
        if datarequired == None:
            request_status = "failed"
            failure_reason = "No details on the data requirment provided by client"

        elif datarequired == "pffull": 
            #This is for the dashboard page

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
            print(command)
            cur, dbqerr = db.mydbfunc(con,cur,command)
            print("#########################################3")
            
            print(cur)
            print(dbqerr)
            print(type(dbqerr))
            print(dbqerr['natstatus'])

            if cur.closed == True or cur.rowcount > 1:
                if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                    dbqerr['statusdetails']="pf sum Fetch failed"
                resp = make_response(jsonify(dbqerr), 400)
                return(resp)

            pfsum_record = None
            if cur.rowcount == 1:
                pfsum_record = cur.fetchall()

            print(pfsum_record)

        #cur.execute("select row_to_json(art) from (select a.*, (select json_agg(b) from (select * from pfstklist where pfportfolioid = a.pfportfolioid ) as b) as pfstklist, (select json_agg(c) from (select * from pfmflist where pfportfolioid = a.pfportfolioid ) as c) as pfmflist from pfmaindetail as a where pfuserid =%s ) art",(userid,))
            #command = cur.mogrify("select row_to_json(art) from (select a.*,(select json_agg(b) from (select * from webapp.pfstklist where pfportfolioid = a.pfportfolioid ) as b) as pfstklist, (select json_agg(c) from (select c.*,(select json_agg(d) from (select * from webapp.pfmforlist where orormflistid = c.ormflistid AND ormffndstatus='INCART' AND entityid=%s) as d) as ormffundorderlists from webapp.pfmflist c where orportfolioid = a.pfportfolioid ) as c) as pfmflist from webapp.pfmaindetail as a where pfuserid =%s AND entityid=%s) art",(entityid,userid,entityid,))
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
            print(command)
            cur, dbqerr = db.mydbfunc(con,cur,command)
            print("#########################################3")
            
            print(cur)
            print(dbqerr)
            print(type(dbqerr))
            print(dbqerr['natstatus'])

            if cur.closed == True or cur.rowcount > 1:
                if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                    dbqerr['statusdetails']="pf product wise fetch failed"
                resp = make_response(jsonify(dbqerr), 400)
                return(resp)
            
            pf_prodwise_record = None
            if cur.rowcount == 1:
                pf_prodwise_record = cur.fetchall()
            
            print(pf_prodwise_record)

            print("portfolio sum and product wise records returned for user: " + userid + " and portfolio id : " + pfid )

        elif datarequired == "prodfull": 
            #This is for the dashboard details page

                    #cur.execute("select row_to_json(art) from (select a.*, (select json_agg(b) from (select * from pfstklist where pfportfolioid = a.pfportfolioid ) as b) as pfstklist, (select json_agg(c) from (select * from pfmflist where pfportfolioid = a.pfportfolioid ) as c) as pfmflist from pfmaindetail as a where pfuserid =%s ) art",(userid,))
            #command = cur.mogrify("select row_to_json(art) from (select a.*,(select json_agg(b) from (select * from webapp.pfstklist where pfportfolioid = a.pfportfolioid ) as b) as pfstklist, (select json_agg(c) from (select c.*,(select json_agg(d) from (select * from webapp.pfmforlist where orormflistid = c.ormflistid AND ormffndstatus='INCART' AND entityid=%s) as d) as ormffundorderlists from webapp.pfmflist c where orportfolioid = a.pfportfolioid ) as c) as pfmflist from webapp.pfmaindetail as a where pfuserid =%s AND entityid=%s) art",(entityid,userid,entityid,))
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
            print(command)
            cur, dbqerr = db.mydbfunc(con,cur,command)
            print("#########################################3")
            
            print(cur)
            print(dbqerr)
            print(type(dbqerr))
            print(dbqerr['natstatus'])

            if cur.closed == True or cur.rowcount > 1:
                if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                    dbqerr['statusdetails']="pf product wise fetch failed"
                resp = make_response(jsonify(dbqerr), 400)
                return(resp)
            
            prod_det_record = None
            if cur.rowcount == 1:
                prod_det_record = cur.fetchall()
            
            print(prod_det_record)
        


        records = {
            'sumrec'      :  {} if pfsum_record == None else pfsum_record[0][0],             # pffull
            'prodrecs'    :  {} if pf_prodwise_record == None else pf_prodwise_record[0][0], # pffull (product summary for a PF)
            'proddetrecs' :  {} if prod_det_record == None else prod_det_record[0][0],       # prodfull
            'fundrcs'     :  {} if fund_record == None else fund_record[0][0],               # fundfull
            'funddetrecs' :  {} if fund_det_record == None else fund_det_record[0][0],
            'status'      :  'success' if request_status == None else request_status,
            'failreason'  :  '' if failure_reason == None else failure_reason
        }
        
        
        
        db.mydbcloseall(con,cur)
        print(records)
        return json.dumps(records)

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
        request_status = None
        failure_reason = None

        if datarequired == None:
            request_status = "failed"
            failure_reason = "No details on the data requirment provided by client"

        elif datarequired == 'pffull':
            pffulldata = get_char_data(datarequired,pfid,prodtyp,fundid,fromdt,todt,entityid)

        elif datarequired == 'prodfull':
            prodfulldata = get_char_data(datarequired,pfid,prodtyp,fundid,fromdt,todt,entityid)

    chart_data = {
        'pffulldata'  :     {} if pffulldata == None else pffulldata,
        'prodfulldata':     {} if prodfulldata == None else prodfulldata,
        'status'      :     'success' if request_status == None else request_status,
        'failreason'  :     '' if failure_reason == None else failure_reason
    }

    return make_response(jsonify(chart_data), 200)


def get_char_data(datareq,pfid,prodtyp,fundid,fromdt,todt,entityid):

        con,cur=db.mydbopncon()        
        print(con)
        print(cur)
        pf_record = None

        if datareq == 'pffull':
            #cur.execute("select row_to_json(art) from (select a.*, (select json_agg(b) from (select * from pfstklist where pfportfolioid = a.pfportfolioid ) as b) as pfstklist, (select json_agg(c) from (select * from pfmflist where pfportfolioid = a.pfportfolioid ) as c) as pfmflist from pfmaindetail as a where pfuserid =%s ) art",(userid,))
            #command = cur.mogrify("select row_to_json(art) from (select a.*,(select json_agg(b) from (select * from webapp.pfstklist where pfportfolioid = a.pfportfolioid ) as b) as pfstklist, (select json_agg(c) from (select c.*,(select json_agg(d) from (select * from webapp.pfmforlist where orormflistid = c.ormflistid AND ormffndstatus='INCART' AND entityid=%s) as d) as ormffundorderlists from webapp.pfmflist c where orportfolioid = a.pfportfolioid ) as c) as pfmflist from webapp.pfmaindetail as a where pfuserid =%s AND entityid=%s) art",(entityid,userid,entityid,))
            command = cur.mogrify(
            """
            SELECT json_agg(info)
            FROM (
                SELECT json_build_array("Date","investment","Growth") AS info
                FROM 
                    (
                            SELECT dpos_date AS Date,SUM(dpos_invamount) AS investment, SUM(dpos_curvalue) AS Growth from webapp.dailyposition_hist
                            WHERE dpos_pfportfolioid = %s AND dpos_entityid = %s
                            GROUP BY dpos_date
                            UNION ALL
                            SELECT dpos_date AS Date,SUM(dpos_invamount) AS investment, SUM(dpos_curvalue) AS Growth from webapp.dailyposition
                            WHERE dpos_pfportfolioid = %s AND dpos_entityid = %s
                            GROUP BY dpos_date
                    ) AS x("Date","investment","Growth")
            ) as t;
            """,(pfid,entityid,pfid,entityid,))
            print(command)
            cur, dbqerr = db.mydbfunc(con,cur,command)
            print("#########################################3")

            print(cur)
            print(dbqerr)
            print(type(dbqerr))
            print(dbqerr['natstatus'])

            if cur.closed == True or cur.rowcount > 1:
                if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                    dbqerr['statusdetails']="pf sum Fetch failed"
                resp = make_response(jsonify(dbqerr), 400)
                return(resp)

            if cur.rowcount == 1:
                pf_record = cur.fetchall()[0][0]
                pf_record.insert(0,['Date', 'Investment', 'Growth'])
                print(pf_record)   

        if datareq == 'prodfull':
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
            print(command)
            cur, dbqerr = db.mydbfunc(con,cur,command)
            print("#########################################3")

            print(cur)
            print(dbqerr)
            print(type(dbqerr))
            print(dbqerr['natstatus'])

            if cur.closed == True or cur.rowcount > 1:
                if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                    dbqerr['statusdetails']="pf sum Fetch failed"
                resp = make_response(jsonify(dbqerr), 400)
                return(resp)

            if cur.rowcount == 1:
                pf_record = cur.fetchall()[0][0]
                pf_record.insert(0,['Date', 'Investment', 'Growth'])
                print(pf_record)               

           
        return pf_record