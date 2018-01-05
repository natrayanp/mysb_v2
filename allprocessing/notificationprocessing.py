from allprocessing import app
from flask import redirect, request,make_response
from datetime import datetime, timedelta
from flask import jsonify
from allprocessing import dbfunc as db

import psycopg2
import jwt
import requests
import json

      
@app.route('/notiprocess',methods=['GET','POST','OPTIONS'])
def notiprocess():
    #pending logics to be written    
    #This is called by notification service
    if request.method=='OPTIONS':
        print("inside notification options")
        return 'ok'

    elif request.method=='POST':
        print(request)
        print("inside notification GET")
        payload = request.stream.read().decode('utf8')
        payload1=json.loads(payload)
        print(payload1)
        lazyloadid=payload1['lazldid']          
        screenid=payload1['module']
        userid=payload1['userid']
        entityid= payload1['entityid']
        print('value of lazyload',lazyloadid)
        print('value of screenid',screenid)
        print('value of userid',userid)
        print('value of entityid',entityid)
               
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        

        #This is to be moved to a configurable place
        conn_string = "host='localhost' dbname='postgres' user='postgres' password='password123'"
        #This is to be moved to a configurable place
        con=psycopg2.connect(conn_string)
        cur = con.cursor()

        print(lazyloadid)
        isnotiusrup2dt=cknotiusrup2dt(screenid,userid,entityid,con,cur)

        if screenid == 'signin':
            pass

            '''            
            #processes day and session items here
            print('inside sigin')

            #start the processing multiprocess
            
            #QUERY THAT FETCHES ALL TO BE PROCESSED.  PASS nfuuid,nfuuserid,nfuentityid TO THE SPAWNED PROCESS TO PROCESS THEM
            command = cur.mogrify("SELECT nfuuid,nfuuserid,nfuentityid FROM notifiuser WHERE nfustatus = 'P' AND nfprocessscope IN ('D','S') AND nfuuserid = %s AND nfuentityid = %s;" ,(userid,entityid,))
            cur, dbqerr = db.mydbfunc(con,cur,command)
            print(cur)
            print(dbqerr)
            print(type(dbqerr))
            print(dbqerr['natstatus'])
            if cur.closed == True:
                if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                    dbqerr['statusdetails']="loginuser Fetch failed"
                resp = make_response(jsonify(dbqerr), 400)
                return(resp)
            else:
                pass
            
            records=[]
            for record in cur:  
                print('inside for')
                print(record)             
                records.append(record)

            print(len(records))

            if len(records) == 0:
                #NO RECORDS TO PROCESS
                pass
            else:
                #HAVE RECORDS TO PROCESS   
                pass        


            #start the processing multiprocess      
             
              
            #return 'ok'
            '''

        elif screenid == 'dashboard':
            #process the everypage load items + Newly added day and session(flag to find this is nfuprocesbypgldsvc = 'Y')
            print('inside dashboard')
            
            command = cur.mogrify("UPDATE notifiuser SET nfulazyldid = %s WHERE nfuuserid = %s AND nfuentityid = %s AND nfuscreenid = %s;",(lazyloadid,userid,entityid,screenid,))
            #command1 = cur.mogrify("select json_agg(c) from (SELECT nfuuid,nfumessage,nfumsgtype FROM notifiuser WHERE nfuuserid = %s AND nfuentityid = %s AND nfuscreenid='dashboard' AND nfustatus = 'C' and nfulazyldid = %s) as c;",(userid,entityid,lazyloadid) )
            print('after lazid update')               
            cur, dbqerr = db.mydbfunc(con,cur,command)
            print(dbqerr['natstatus'])
            if cur.closed == True:
                if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                    dbqerr['statusdetails']="pf Fetch failed"
                resp = make_response(jsonify(dbqerr), 400)
                return(resp)
            con.commit()                  
            print(cur)
            print('consider insert or update is successful')
            
            # Send the response back and continue processing

            #start the processing multiprocess
            #QUERY THAT FETCHES ALL TO BE PROCESSED.  PASS nfuuid,nfuuserid,nfuentityid TO THE SPAWNED PROCESS TO PROCESS THEM
            '''
            cmdqry = 'SELECT nfuuid,nfuuserid,nfuentityid FROM notifiuser WHERE nfustatus = 'P' AND nfprocessscope NOT IN ('D','S') AND nfuuserid = %s AND nfuentityid = %s'
            cmdqry = cmdqry + 'UNION'
            cmdqry = cmdqry + 'SELECT nfuuid,nfuuserid,nfuentityid FROM notifiuser WHERE nfustatus = 'P' AND nfprocessscope IN ('D','S') AND nfuprocesbypgldsvc = 'Y' AND nfuuserid = %s AND nfuentityid = %s;'
                        
            command = cur.mogrify(cmdqry,(userid,entityid,userid,entityid,))
            '''

            #start the processing multiprocess END


        elif lazyloadid != 'dashboard' or lazyloadid != 'signin':
            pass
    
    return 'ok from notiprocess'
       
'''
def mydbfunc(con,cur,command):
    try:
        cur.execute(command)        
        myerror={'natstatus':'success','statusdetails':''}
    except psycopg2.Error as e:
        print(e)
        myerror= {'natstatus':'error','statusdetails':''}
    except psycopg2.Warning as e:
        print(e)
        myerror={'natstatus':'warning','statusdetails':''}
        #myerror = {'natstatus':'warning','statusdetails':e}
    finally:
        if myerror['natstatus'] != "success":    
            con.rollback()
            cur.close()
            con.close()
            
    return cur,myerror
'''

def cknotiusrup2dt(screenid,userid,entityid,con,cur):
    print('inside cknotiusrup2dt')
    command = cur.mogrify("select distinct nfuoctime from notifiuser where nfuuserid = %s and nfuentityid = %s;",(userid,entityid,) )
    cur, dbqerr = db.mydbfunc(con,cur,command)
    print(cur)
    print(dbqerr)
    print(type(dbqerr))
    print(dbqerr['natstatus'])
    rowcount = cur.rowcount

    if rowcount != 0:
        records=[]
        for record in cur:  
            print('inside for')
            print(record)             
            records.append(record)
        datetimenf, = records[0]
                 
    elif rowcount == 0:
        #just to make sure the if condition fails
        datetimenf = datetime.now()- timedelta(1)
    else:
        pass

    print('current time : ',datetime.utcnow().date())
    print('datetimemnf',datetimenf.date())   
    if datetimenf.date() == datetime.utcnow().date():
        print('inside elifse')
        #notification user table is done today so no action required
        query = "INSERT INTO notifiuser (nfumid,nfuuserid,nfuscreenid,nfumessage,nfumsgtype,nfprocessscope,nfuhvnxtact,nfunxtactmsg,nfunxtactnavtyp,nfunxtactnavdest,nfulazyldidstatus,nfustatus,nfuprocesbypgldsvc,nfutodayshowncount,nfuoctime,nfulmtime,nfuentityid) "
        query = query+ "(SELECT nfmid,nfmuserid,nfmscreenid,nfmessage,nfmsgtype,nfprocessscope,nfmnxtact,nfmnxtactmsg,nfmnxtactnavtyp,nfmnxtactnavdest,'N','P','Y',0,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,%s"
        query = query + "FROM notifimaster WHERE nfmuserid IN (%s,'ALL') AND nfmentityid = %s "
        query = query + "AND nfmlmtime > (SELECT MAX(nfuoctime) FROM notifiuser WHERE nfuuserid IN (%s,'ALL') AND nfuentityid = %s) )"
        command = cur.mogrify(query,(entityid,userid,entityid,userid,entityid,))
    else:
        print('inside else')
        #notification user table is old, create from master now
        command = cur.mogrify("DELETE FROM notifiuser WHERE nfuuserid = %s AND nfuentityid = %s",(userid,entityid,))
        print(command)
        cur, dbqerr = db.mydbfunc(con,cur,command)
        print(cur)
        print(dbqerr)
        print(type(dbqerr))
        print(dbqerr['natstatus'])

        if cur.closed == True:
            if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                dbqerr['statusdetails']="usernotify delete failed"
            resp = make_response(jsonify(dbqerr), 400)
            return(resp)
        con.commit()                  
        print(cur)
        print('consider delete is successful')

        query = "INSERT INTO notifiuser (nfumid,nfuuserid,nfuscreenid,nfumessage,nfumsgtype,nfprocessscope,nfuhvnxtact,nfunxtactmsg,nfunxtactnavtyp,nfunxtactnavdest,nfulazyldidstatus,nfustatus,nfutodayshowncount,nfuoctime,nfulmtime,nfuentityid) "
        query = query+ "(SELECT nfmid,nfmuserid,nfmscreenid,nfmessage,nfmsgtype,nfprocessscope,nfmnxtact,nfmnxtactmsg,nfmnxtactnavtyp,nfmnxtactnavdest,'N','P',0,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,%s "
        query = query + "FROM notifimaster WHERE nfmuserid IN (%s,'ALL') AND nfmentityid = %s)"
        command = cur.mogrify(query,(entityid,userid,entityid,))

    print(command)
    cur, dbqerr = db.mydbfunc(con,cur,command)
    print(cur)
    print(dbqerr)
    print(type(dbqerr))
    print(dbqerr['natstatus'])

    if cur.closed == True:
        if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
            dbqerr['statusdetails']="pf Fetch failed"
        resp = make_response(jsonify(dbqerr), 400)
        return(resp)
    
    con.commit()                  
    print(cur)
    print('consider insert or update is successful')
    
    print('cknotiusrup2dt completed')
    return True



