from pf import app
from flask import redirect, request,make_response
from datetime import datetime, date, timedelta
from flask import jsonify
from pf import dbfunc as db
from pf import mforderapi_crawl as crawl

import jwt
import requests
import json


def dailyposition_build():
    entityid = 'IN'
    con,cur=db.mydbopncon()

    #Check if entry is there in the job schedule table.  If yes, quit else start processing.
        #Pending work
    #Check if entry is there in the job schedule table.  If yes, quit else start processing.


    command = cur.mogrify(
    """
        select json_agg(b) from (
            SELECT tran_entityid,tran_pfportfolioid,tran_producttype,tran_schemecd,tran_dailypositionflg,count(1) as count FROM webapp.trandetails WHERE tran_dailypositionflg in ('N','P') AND mfor_entityid =%s
            GROUP BY tran_entityid,tran_pfportfolioid,tran_producttype,tran_schemecd,tran_dailypositionflg
            HAVING count(1) = 1 AND tran_dailypositionflg = 'N'
        ) as b;
    """,(entityid,))
    print(command)
    cur, dbqerr = db.mydbfunc(con,cur,command)
                            
    if cur.closed == True:
        if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
            dbqerr['statusdetails']="Data for order multiprocess fetch failed"
        resp = make_response(jsonify(dbqerr), 400)
        return(resp)
    print("cur") 
    print(cur)
    
    records = []
    if cur:
        for record in cur:
                records.append(record[0])
    print(records)
    if records[0] == None:
        records = []
    
    if len(records) > 0:
        print("multiprocessing starts")
        pool = Pool(processes=10)
        result = pool.map_async(process_one_pfrecord, records)
        print(result)   
        result.wait()        
        print(result.get())
        order_resp = result.get()
        pool.close()
        pool.join()    
        print("multiprocessing Ends")
    
    db.mydbcloseall(con,cur)


def process_one_pfrecord(criteria):
    
    con,cur=db.mydbopncon()    
    reloop = True
    prossesedcnt = 0


    while reloop:
        has_db_error = False
        has_db_warn = False
        curproccnt = 100
        prossesedcnt = prossesedcnt + curproccnt
        if prossesedcnt >= criteria['count']:
            reloop = False
        
        command = cur.mogrify(
        """
            select row_to_json (t) from (
                SELECT * FROM webapp.trandetails 
                WHERE tran_dailypositionflg = 'N'
                AND tran_entityid =%s
                AND tran_pfportfolioid = %s
                AND tran_producttype = %s
                AND tran_schemecd  = %s
                ORDER BY tran_orderdate,tran_pfportfolioid,tran_producttype,tran_schemecd,tran_id ASC
                LIMIT 100
                ) as t
        """,(criteria['tran_entityid'],criteria['tran_pfportfolioid'],criteria['tran_producttype'],criteria['tran_schemecd']))
        print(command)

        cur, dbqerr = db.mydbfunc(con,cur,command)
        if cur.closed == True:            
            mm = None
            if(dbqerr['natstatus'] == "error"):
                mm = "trandetails : error : onepf record fetch failed" 
                has_db_error = True
            if dbqerr['natstatus'] == "warning"):
                mm = "trandetails :  : warning : onepf record fetch failed" 
                has_db_warn = True
            if mm:
                if dbqerr['statusdetails'] == None or dbqerr['statusdetails'] == '':
                    dbqerr['statusdetails']= mm
                else:
                    dbqerr['statusdetails'] = dbqerr['statusdetails'] + "|" + mm

        records = []
        if cur:
            for record in cur:
                if record:
                    records.append(record)
                else:
                    records = []
        
        posrec_req_date = datetime.strptime(records[0]['tran_orderdate'], '%Y-%m-%d').date()
        posrec_pre_date = posrec_req_date + timedelta(days=-1)

        if len(records) > 0:
            command = cur.mogrify(
            """
                SELECT row_to_json (t) FROM (
                    SELECT * FROM webapp.dailyposition_hist 
                    WHERE dpos_entityid =%s
                    AND dpos_pfportfolioid = %s
                    AND dpos_producttype = %s
                    AND dpos_schemecd  = %s
                    AND dpso_date >= %s
                    UNION ALL
                    SELECT * FROM webapp.dailyposition 
                    WHERE dpos_entityid =%s
                    AND dpos_pfportfolioid = %s
                    AND dpos_producttype = %s
                    AND dpos_schemecd  = %s
                    AND dpso_date >= %s                    
                    ORDER BY dpso_date ASC
                    ) as t
            """,(criteria['tran_entityid'],criteria['tran_pfportfolioid'],criteria['tran_producttype'],criteria['tran_schemecd'],posrec_pre_date,criteria['tran_entityid'],criteria['tran_pfportfolioid'],criteria['tran_producttype'],criteria['tran_schemecd'],posrec_pre_date,))
            print(command)

            cur, dbqerr = db.mydbfunc(con,cur,command)

            if cur.closed == True:            
                mm = None
                if(dbqerr['natstatus'] == "error"):
                    mm = "trandetails : error : dailyposition & hist record fetch failed" 
                    has_db_error = True
                if dbqerr['natstatus'] == "warning"):
                    mm = "trandetails :  : warning : dailyposition & hist record fetch failed" 
                    has_db_warn = True
                if mm:
                    if dbqerr['statusdetails'] == None or dbqerr['statusdetails'] == '':
                        dbqerr['statusdetails']= mm
                    else:
                        dbqerr['statusdetails'] = dbqerr['statusdetails'] + "|" + mm

            positionrecs = []
            if cur:
                for record in cur:
                    if record:
                        positionrecs.append(record)
                    else:
                        positionrecs = []
        else:
            pass

        tran_ids=[]
        movefromdlypos = False
        for rec in records:
            tran_ids.append(rec['tran_id'])
            prev_prec = ''
            match_cnt = 0
            for prec in positionrecs:
                if match_cnt == 0:
                    if prec['dpso_date'] == rec['tran_orderdate']:
                        match_cnt = 1                
                        

                if match_cnt == 1:
                    if rec['tran_buysell'] == 'P':
                        prec['dpos_unit'] = prec['dpos_unit'] + rec['tran_unit']
                        prec['dpos_invamount'] = prec['dpos_invamount'] + rec['tran_invamount']
                        prec['dpos_avgnav'] = prec['dpos_invamount'] / prec['dpos_unit']
                        prec['dpos_curvalue'] = prec['dpos_unit'] * prec['dpos_curnav']
                        prec['dpos_lmtime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    if rec['tran_buysell'] == 'R':
                        prec['dpos_unit'] = prec['dpos_unit'] - rec['tran_unit']
                        prec['dpos_invamount'] = prec['dpos_unit'] * prec['dpos_avgnav']
                        prec['dpos_totalpnl'] = prec['dpos_totalpnl'] + (rec['tran_invamount']-(tran['tran_unit']*prec['dpos_avgnav']))
                        #don't change the order
                        prec['dpos_avgnav'] = prec['dpos_invamount'] / prec['dpos_unit']
                        prec['dpos_curvalue'] = prec['dpos_unit'] * prec['dpos_curnav']
                        prec['dpos_lmtime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')                
                    
                    match_cnt = match_cnt + 1

                elif match_cnt > 1:
                    #this loop is to just built the next day positions for the transaction happened on previous day
                    if rec['tran_buysell'] == 'P':
                        prec['dpos_unit'] = prec['dpos_unit'] + prev_prec['dpos_unit']
                        prec['dpos_invamount'] = prec['dpos_invamount'] + prev_prec['dpos_invamount']
                        prec['dpos_avgnav'] = prec['dpos_invamount'] / prec['dpos_unit']
                        prec['dpos_curvalue'] = prec['dpos_unit'] * prec['dpos_curnav']
                        prec['dpos_lmtime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                    if rec['tran_buysell'] == 'R':
                        prec['dpos_unit'] = prec['dpos_unit'] - prev_prec['dpos_unit']
                        prec['dpos_invamount'] = prec['dpos_invamount'] - prev_prec['dpos_invamount']
                        prec['dpos_avgnav'] = prec['dpos_invamount'] / prec['dpos_unit']
                        prec['dpos_curvalue'] = prec['dpos_unit'] * prec['dpos_curnav']
                        prec['dpos_totalpnl'] = prec['dpos_totalpnl'] + prev_prec['dpos_totalpnl']
                        prec['dpos_lmtime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                prev_prec = prec

            if match_cnt == 0:
                movefromdlypos = True
                if posrec_req_date > datetime.now().strftime('%Y-%m-%d'):                
                    print("Fatal: transaction date is a future date")
                else:
                    #First time record, incase there is no entry inpostition table for the tran date
                    if prev_prec = '':
                        prev_prec={}
                        prev_prec['dpos_schemecd'] = rec['tran_schemecd']
                        prev_prec['dpos_schmname'] = rec['tran_schmname']
                        prev_prec['dpos_unit'] = 0
                        prev_prec['dpos_invamount'] = 0
                        prev_prec['dpos_curnav'] = rec['tran_nav']
                        prev_prec['dpos_totalpnl'] = 0
                        prev_prec['dpos_pfportfolioid'] = rec['tran_pfportfolioid']
                        prev_prec['dpos_producttype'] = rec['tran_producttype']
                        prev_prec['dpos_entityid'] = rec['tran_entityid']

                    if rec['tran_buysell'] == 'P':
                        newprec['dpso_date'] = rec['tran_orderdate']
                        newprec['dpos_schemecd'] = prev_prec['dpos_schemecd']
                        newprec['dpos_schmname'] = prev_prec['dpos_schmname']
                        newprec['dpos_invamount'] = prev_prec['dpos_invamount'] + rec['tran_invamount']
                        newprec['dpos_unit'] = prev_prec['dpos_unit'] + rec['tran_unit']
                        newprec['dpos_avgnav'] = newprec['dpos_invamount'] / newprec['dpos_unit']
                        newprec['dpos_curnav'] = prev_prec['dpos_curnav']
                        newprec['dpos_curvalue'] = newprec['dpos_unit'] * newprec['dpos_curnav']
                        newprec['dpos_totalpnl'] = prev_prec['dpos_totalpnl']
                        newprec['dpos_pfportfolioid'] = prev_prec['dpos_pfportfolioid']
                        newprec['dpos_producttype'] = prev_prec['dpos_producttype']
                        newprec['dpos_octime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        newprec['dpos_lmtime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        newprec['dpos_entityid'] = prev_prec['dpos_entityid']

                    if rec['tran_buysell'] == 'R':
                        newprec['dpso_date'] = rec['tran_orderdate']
                        newprec['dpos_schemecd'] = prev_prec['dpos_schemecd']
                        newprec['dpos_schmname'] = prev_prec['dpos_schmname']
                        newprec['dpos_invamount'] = prev_prec['dpos_invamount'] + rec['tran_invamount']
                        newprec['dpos_unit'] = prev_prec['dpos_unit'] + rec['tran_unit']
                        newprec['dpos_avgnav'] = newprec['dpos_invamount'] / newprec['dpos_unit']
                        newprec['dpos_curnav'] = prev_prec['dpos_curnav']
                        newprec['dpos_curvalue'] = newprec['dpos_unit'] * newprec['dpos_curnav']
                        newprec['dpos_totalpnl'] = prev_prec['dpos_totalpnl']
                        newprec['dpos_pfportfolioid'] = prev_prec['dpos_pfportfolioid']
                        newprec['dpos_producttype'] = prev_prec['dpos_producttype']
                        newprec['dpos_octime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        newprec['dpos_lmtime'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        newprec['dpos_entityid'] = prev_prec['dpos_entityid']

                    positionrecs.append(newprec)

        command = cur.mogrify("BEGIN;")
        cur, dbqerr = db.mydbfunc(con,cur,command)
        if cur.closed == True:            
            mm = None
            if(dbqerr['natstatus'] == "error"):
                mm = "trandetails : error : DB query failed, BEGIN failed" 
                has_db_error = True
            if dbqerr['natstatus'] == "warning"):
                mm = "trandetails :  : warning : DB query failed, BEGIN failed" 
                has_db_warn = True
            if mm:
                if dbqerr['statusdetails'] == None or dbqerr['statusdetails'] == '':
                    dbqerr['statusdetails']= mm
                else:
                    dbqerr['statusdetails'] = dbqerr['statusdetails'] + "|" + mm

        prec_last_rec = positionrecs.pop()
        prec_2nd_last_rec_date = positionrecs[-1]['dpso_date']
        
        #Example record : [1,2,3,4,5]
        #Move the last but 2nd record (ie.4th records date) to history table, only if exists in main table
        command = cur.mogrify(
        """
        INSERT INTO webapp.dailyposition_hist
        SELECT * FROM webapp.dailyposition 
        WHERE dpos_entityid = %s
        AND dpos_pfportfolioid = %s
        AND dpos_producttype = %s
        AND dpos_schemecd  = %s
        AND dpso_date = %s
        """,(criteria['tran_entityid'],criteria['tran_pfportfolioid'],criteria['tran_producttype'],criteria['tran_schemecd'],prec_2nd_last_rec_date,))
        print(command)
        cur, dbqerr = db.mydbfunc(con,cur,command)
        if cur.closed == True:            
            mm = None
            if(dbqerr['natstatus'] == "error"):
                mm = prec_2nd_last_rec_date + " : error : daily position movement to history Failed" 
                has_db_error = True
            if dbqerr['natstatus'] == "warning"):
                mm = prec_2nd_last_rec_date + " : warning : daily position movement to history Failed" 
                has_db_warn = True
            if mm:
                if dbqerr['statusdetails'] == None or dbqerr['statusdetails'] == '':
                    dbqerr['statusdetails']= mm
                else:
                    dbqerr['statusdetails'] = dbqerr['statusdetails'] + "|" + mm


        #INSERT the last record (ie.5th records) to main table.        
        d = json.dumps(prec_last_rec)
        command = cur.mogrify("""
            INSERT INTO webapp.dailyposition select * from json_populate_record(NULL::webapp.dailyposition,%s)
            ON CONFICT (dpos_entityid,dpos_pfportfolioid,dpos_producttype,dpos_schemecd,dpso_date)
            UPDATE webapp.dailyposition_hist SET dpos_unit = %s, dpos_invamount = %s, dpos_avgnav = %s, dpos_curvalue = %s, dpos_totalpnl = %s, dpos_lmtime = %s
            WHERE dpos_entityid =%s
            AND dpos_pfportfolioid = %s
            AND dpos_producttype = %s
            AND dpos_schemecd  = %s
            AND dpso_date = %s        
        """,(str(d),prec_last_rec['dpos_unit'], prec_last_rec['dpos_invamount'], prec_last_rec['dpos_avgnav'], prec_last_rec['dpos_curvalue'], prec_last_rec['dpos_totalpnl'], prec_last_rec['dpos_lmtime'],criteria['tran_entityid'],criteria['tran_pfportfolioid'],criteria['tran_producttype'],criteria['tran_schemecd'],prec_last_rec['dpso_date'],))
        print(command)
        cur, dbqerr = db.mydbfunc(con,cur,command)
        if cur.closed == True:            
            mm = None
            if(dbqerr['natstatus'] == "error"):
                mm = prec_last_rec['dpso_date'] + " : error : daily position INSERT Failed" 
                has_db_error = True
            if dbqerr['natstatus'] == "warning"):
                mm = prec_last_rec['dpso_date'] + " : warning : daily position INSERT Failed" 
                has_db_warn = True
            if mm:
                if dbqerr['statusdetails'] == None or dbqerr['statusdetails'] == '':
                    dbqerr['statusdetails']= mm
                else:
                    dbqerr['statusdetails'] = dbqerr['statusdetails'] + "|" + mm
        

        #UPDATE all records except last (ie.1-4 records) to history table.
        for prec in positionrecs:
            command = cur.mogrify(
            """
            UPDATE webapp.dailyposition_hist SET dpos_unit = %s, dpos_invamount = %s, dpos_avgnav = %s, dpos_curvalue = %s, dpos_totalpnl = %s, dpos_lmtime = %s
            WHERE dpos_entityid =%s
            AND dpos_pfportfolioid = %s
            AND dpos_producttype = %s
            AND dpos_schemecd  = %s
            AND dpso_date = %s                    
            """,(prec['dpos_unit'], prec['dpos_invamount'], prec['dpos_avgnav'], prec['dpos_curvalue'], prec['dpos_totalpnl'], prec['dpos_lmtime'],criteria['tran_entityid'],criteria['tran_pfportfolioid'],criteria['tran_producttype'],criteria['tran_schemecd'],prec['dpso_date'],))       
            print(command)
            cur, dbqerr = db.mydbfunc(con,cur,command)
            if cur.closed == True:            
                mm = None
                if(dbqerr['natstatus'] == "error"):
                    mm = prec['dpso_date'] + " : error : daily position UPDATE in history table Failed" 
                    has_db_error = True
                if dbqerr['natstatus'] == "warning"):
                    mm = prec['dpso_date'] + " : warning : daily position UPDATE in history table Failed" 
                    has_db_warn = True
                if mm:
                    if dbqerr['statusdetails'] == None or dbqerr['statusdetails'] == '':
                        dbqerr['statusdetails']= mm
                    else:
                        dbqerr['statusdetails'] = dbqerr['statusdetails'] + "|" + mm

        print(dbqerr['statusdetails'])
        
        if has_db_error:
            con.rollback()
        else:
            str2 = tuple(tran_ids)           
            command = cur.mogrify(
            """
                UPDATE webapp.trandetails SET tran_dailypositionflg = 'Y'                
                    WHERE tran_dailypositionflg = 'N'
                    AND tran_entityid =%s
                    AND tran_pfportfolioid = %s
                    AND tran_producttype = %s
                    AND tran_schemecd  = %s
                    AND tran_id IN %s
                    
            """,(criteria['tran_entityid'],criteria['tran_pfportfolioid'],criteria['tran_producttype'],criteria['tran_schemecd'],str2,))
            print(command)

            cur, dbqerr = db.mydbfunc(con,cur,command)
            if cur.closed == True:            
                mm = None
                if(dbqerr['natstatus'] == "error"):
                    mm = "trandetails : error : onepf record fetch failed" 
                    has_db_error = True
                if dbqerr['natstatus'] == "warning"):
                    mm = "trandetails :  : warning : onepf record fetch failed" 
                    has_db_warn = True
                if mm:
                    if dbqerr['statusdetails'] == None or dbqerr['statusdetails'] == '':
                        dbqerr['statusdetails']= mm
                    else:
                        dbqerr['statusdetails'] = dbqerr['statusdetails'] + "|" + mm
            
            con.commit()



    db.mydbcloseall(con,cur)

    return (dbqerr['statusdetails'])