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
            """,(payload,entityid,))
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
            """,(payload,entityid,))
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
        print("portfolio sum and product wise records returned for user: " + userid + " and portfolio id : " + payload )        
            
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
        prodid = data.get('prodid', None)
        fundid = data.get('fundid', None)
        fromdt = None
        todt = None

        if pfid == None:
            return make_response(jsonify('Invalid data'), 400)
        
        if pfid:
            recs = get_char_data(pfid,prodid,fundid,fromdt,todt,entityid)

        chart_data = {
            'data': recs
        }

        return make_response(jsonify(chart_data), 200)


def get_char_data(pfid,prodid,fundid,fromdt,todt,entityid):

        con,cur=db.mydbopncon()        
        print(con)
        print(cur)
        
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

        pf_record = None
        if cur.rowcount == 1:
            pf_record = cur.fetchall()[0][0]
        pf_record.insert(0,['Date', 'Investment', 'Growth'])
        print(pf_record)
        for pf in pf_record:
            print (pf)
            print(type(pf))

        

        return pf_record