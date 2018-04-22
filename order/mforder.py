from order import app
from flask import request, make_response, jsonify, Response, redirect
from datetime import datetime
from order import dbfunc as db
from order import jwtdecodenoverify as jwtnoverify
from dateutil import tz
from datetime import datetime
from datetime import date
from multiprocessing import Process

import psycopg2
import json
import jwt
import time

@app.route('/mforderdatafetch',methods=['GET','OPTIONS'])
def pforderdatafetch():
#This is called by fund data fetch service
    if request.method=='OPTIONS':
        print("inside pforderdatafetch options")
        return make_response(jsonify('inside FUNDDATAFETCH options'), 200)  

    elif request.method=='GET':
        print("inside pforderdatafetch GET")
        print((request))        
        print(request.headers)
        userid,entityid=jwtnoverify.validatetoken(request)
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print(userid,entityid)
        print('after')
        
        con,cur=db.mydbopncon()
        
        print(con)
        print(cur)
        
        #cur.execute("select row_to_json(art) from (select a.*, (select json_agg(b) from (select * from pfstklist where pfportfolioid = a.pfportfolioid ) as b) as pfstklist, (select json_agg(c) from (select * from pfmflist where pfportfolioid = a.pfportfolioid ) as c) as pfmflist from pfmaindetail as a where pfuserid =%s ) art",(userid,))
        #command = cur.mogrify("select row_to_json(art) from (select a.*,(select json_agg(b) from (select * from webapp.pfstklist where pfportfolioid = a.pfportfolioid ) as b) as pfstklist, (select json_agg(c) from (select c.*,(select json_agg(d) from (select * from webapp.pfmforlist where orormflistid = c.ormflistid AND ormffndstatus='INCART' AND entityid=%s) as d) as ormffundorderlists from webapp.pfmflist c where orportfolioid = a.pfportfolioid ) as c) as pfmflist from webapp.pfmaindetail as a where pfuserid =%s AND entityid=%s) art",(entityid,userid,entityid,))
        command = cur.mogrify(
            """
        	WITH portport as (select ororportfolioid,orormflistid,orormfpflistid from webapp.pfmforlist where ormffndstatus = 'INCART' AND ororpfuserid = %s AND entityid = %s) 
            select row_to_json(art) from (
            select a.*,
            (select json_agg(b) from (select * from webapp.pfstklist where pfportfolioid = a.pfportfolioid ) as b) as pfstklist, 
            (select json_agg(c) from (select c.*,(select json_agg(d) from (select * from webapp.pfmforlist where orormflistid in (SELECT distinct orormflistid FROM PORTPORT) AND ororportfolioid =a.pfportfolioid AND orormflistid=c.ormflistid AND ormffndstatus = 'INCART' AND entityid = %s) as d) as ormffundorderlists 
            from webapp.pfmflist c where ormflistid in (SELECT distinct orormflistid FROM portport) AND  entityid = %s AND orportfolioid =a .pfportfolioid ) as c) as pfmflist 
	        from webapp.pfmaindetail as a where pfuserid = %s AND entityid = %s AND pfportfolioid IN (SELECT distinct ororportfolioid FROM portport) ORDER BY pfportfolioid  ) art
            """,(userid,entityid,entityid,entityid,userid,entityid,))

        cur, dbqerr = db.mydbfunc(con,cur,command)
        print("#########################################3")
        print(command)
        print("#########################################3")
        print(cur)
        print(dbqerr)
        print(type(dbqerr))
        print(dbqerr['natstatus'])
        
        if cur.closed == True:
            if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                dbqerr['statusdetails']="pf Fetch failed"
            resp = make_response(jsonify(dbqerr), 400)
            return(resp)


        #Model to follow in all fetch
        records=[]
        for record in cur:  
            records.append(record[0])           



        print("portfolio details returned for user: "+userid)
        
        
        resp = json.dumps(records)
    
    return resp