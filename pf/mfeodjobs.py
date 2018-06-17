def mfeodmasterjb():
#EOD job for MF
    entityid = 'IN'
    boddate = datetime.now().strftime('%Y-%m-%d')

    #START OF BOD JOB
    print('Daily EOD START job start')
    status = mfeodmasterstart(entityid,boddate)
    if status:
       print('job has error')    
    
    #1) Build daily poision
    print('Daily POSITION BUILD job start')
    status = mfeodposischejb(entityid,boddate)
    if status:
       print('job has error') 

    #END OF BOD JOB
    print('Daily EOD END job start')    
    status = mfeodmasterend(entityid,boddate)
    if status:
       print('job has error')    


def mfeodmasterstart(entityid,boddate):
    
    has_error = False
    jobstarttime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    con,cur=db.mydbopncon()
    command = cur.mogrify(
    """
    INSERT INTO webapp.batchjobstatus_hist
    SELECT * FROM webapp.batchjobstatus WHERE dpos_entityid = %s
    """,(entityid,))
    print(command)
    cur, dbqerr = db.mydbfunc(con,cur,command)
    if cur.closed == True:
        has_error = True
        if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
            if dbqerr['statusdetails'] == None or dbqerr['statusdetails'] == '':
                dbqerr['statusdetails']="mflist daily position history insert Failed"
            else:
                dbqerr['statusdetails'] = dbqerr['statusdetails'] + "|" + "mflist daily position history insert Failed"
        #resp = make_response(jsonify(dbqerr), 400)

    if has_error:        
        resp = {
            'bjs_businessdate':boddate,
            'bjs_jobid':'EODMASTER',
            'bjs_jobgroup':'EOD',
            'bjs_starttime': jobstarttime,
            'bjs_endtime':'',
            'bjs_status':'F',
            'bjs_errormsg':dbqerr['statusdetails'],
            'bjs_octime':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'bjs_lmtime':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'bjs_entityid': entityid
        }
    
    else:
        resp = {
            'bjs_businessdate':boddate,
            'bjs_jobid':'EODMASTER',
            'bjs_jobgroup':'EOD',
            'bjs_starttime': jobstarttime,
            'bjs_endtime':'',
            'bjs_status':'R',
            'bjs_errormsg':'',
            'bjs_octime':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'bjs_lmtime':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'bjs_entityid': entityid
        }

    d = json.dumps(resp)
        
    command = cur.mogrify(
    """
        INSERT INTO webapp.batchjobstatus select * from json_populate_record(NULL::webapp.batchjobstatus,%s) where entityid = %s;
    """,(str(d),entityid,))
    print(command)
    cur, dbqerr = db.mydbfunc(con,cur,command)
    if cur.closed == True:
        has_error = True
        print("fatal in job inserting EOD master batch")
        if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
            if dbqerr['statusdetails'] == None or dbqerr['statusdetails'] == '':
                dbqerr['statusdetails']="mflist daily position history insert Failed"
            else:
                dbqerr['statusdetails'] = dbqerr['statusdetails'] + "|" + "mflist daily position history insert Failed"
        #resp = make_response(jsonify(dbqerr), 400)
    resp = {'has_error': has_error}

    db.mydbcloseall(con,cur)
    return resp



def mfeodmasterend(entityid,boddate):

    con,cur=db.mydbopncon()
    command = cur.mogrify(
    """
        UPDATE webapp.batchjobstatus SET bjs_jobid = 'EODMASTER', bjs_jobgroup = 'EOD', bjs_endtime = CURRENT_TIMESTAMP, bjs_status = 'C', bjs_lmtime =  CURRENT_TIMESTAMP  where entityid = %s;
    """,(str(d),entityid,))
    print(command)
    cur, dbqerr = db.mydbfunc(con,cur,command)
    if cur.closed == True:
        has_error = True
        print("fatal in job inserting EOD master batch")
        if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
            if dbqerr['statusdetails'] == None or dbqerr['statusdetails'] == '':
                dbqerr['statusdetails']="mflist daily position history insert Failed"
            else:
                dbqerr['statusdetails'] = dbqerr['statusdetails'] + "|" + "mflist daily position history insert Failed"
        #resp = make_response(jsonify(dbqerr), 400)

    resp = {'has_error': has_error}
    db.mydbcloseall(con,cur)
    return resp


def mfeodposischejb(entityid,boddate):
 #EOD logic
    #Put a logic to put entity ids that needs EOD
    # For now hard code it here
    #START OF JOB 1
    jobstarttime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    jobid = 'EOD01'
    jobgroup = 'EOD'
    con,cur=db.mydbopncon()    
    
    command = cur.mogrify("BEGIN;")

    cur, dbqerr = db.mydbfunc(con,cur,command)
    if cur.closed == True:
        has_error = True
        if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
            dbqerr['statusdetails']="DB query failed, BEGIN failed"
        resp = make_response(jsonify(dbqerr), 400)
        return(resp)

    command = cur.mogrify(
    """
    INSERT INTO webapp.dailyposition_hist
    SELECT * FROM webapp.dailyposition WHERE dpos_entityid = %s
    """,(entityid,))
    print(command)
    cur, dbqerr = db.mydbfunc(con,cur,command)
    if cur.closed == True:
        has_error = True
        if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
            if dbqerr['statusdetails'] == None or dbqerr['statusdetails'] == '':
                dbqerr['statusdetails']="mflist daily position history insert Failed"
            else:
                dbqerr['statusdetails'] = dbqerr['statusdetails'] + "|" + "mflist daily position history insert Failed"
        #resp = make_response(jsonify(dbqerr), 400)
        #return(resp)
    

    command = cur.mogrify(
    """
    UPDATE webapp.dailyposition SET dpso_date = %s, dpos_octime = CURRENT_TIMESTAMP, dpos_lmtime = CURRENT_TIMESTAMP 
    WHERE dpos_entityid = %s
    """,(boddate,entityid,))
    print(command)
    cur, dbqerr = db.mydbfunc(con,cur,command)
    if cur.closed == True:
        if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
            has_error = True
            if dbqerr['statusdetails'] == None or dbqerr['statusdetails'] == '':
                dbqerr['statusdetails']="mflist daily position new date update Failed"
            else:
                dbqerr['statusdetails'] = dbqerr['statusdetails'] + "|" + "mflist daily position new date update Failed"
        #resp = make_response(jsonify(dbqerr), 400)
        return(resp)

    con.commit()

    jobendtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if has_error = True:        
        resp = {
            'bjs_businessdate':boddate,
            'bjs_jobid':jobid,
            'bjs_jobgroup':jobgroup,
            'bjs_starttime': jobstarttime,
            'bjs_endtime':'',
            'bjs_status':'F',
            'bjs_errormsg':dbqerr['statusdetails'],
            'bjs_octime':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'bjs_lmtime':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'bjs_entityid': entityid
        }
    
    else:
        resp = {
            'bjs_businessdate':boddate,
            'bjs_jobid':jobid,
            'bjs_jobgroup':jobgroup,
            'bjs_starttime': jobstarttime,
            'bjs_endtime':jobendtime,
            'bjs_status':'C',
            'bjs_errormsg':'',
            'bjs_octime':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'bjs_lmtime':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'bjs_entityid': entityid
        }
    
    d = json.dumps(resp)
        
    command = cur.mogrify(
    """
        INSERT INTO webapp.batchjobstatus select * from json_populate_record(NULL::webapp.batchjobstatus,%s) where entityid = %s;
    """,(str(d),entityid,))
    print(command)
    cur, dbqerr = db.mydbfunc(con,cur,command)
    if cur.closed == True:
        has_error = True
        print("fatal in job inserting EOD master batch")
        if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
            if dbqerr['statusdetails'] == None or dbqerr['statusdetails'] == '':
                dbqerr['statusdetails']="mflist daily position history insert Failed"
            else:
                dbqerr['statusdetails'] = dbqerr['statusdetails'] + "|" + "mflist daily position history insert Failed"
        #resp = make_response(jsonify(dbqerr), 400)
    resp = {'has_error': has_error}

    db.mydbcloseall(con,cur)
    return resp