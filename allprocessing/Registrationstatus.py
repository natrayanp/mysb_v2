from allprocessing import app
from flask import redirect, request,make_response
from datetime import datetime, timedelta
from flask import jsonify
from allprocessing import dbfunc as db

import psycopg2
import jwt
import requests
import json

      
def registrationstatus():

    #This is to be moved to a configurable place
    conn_string = "host='localhost' dbname='postgres' user='postgres' password='password123'"
    #This is to be moved to a configurable place
    con=psycopg2.connect(conn_string)
    cur = con.cursor()

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
    '''
    if cur.length == 0:
        #NO RECORDS TO PROCESS
        pass
    else:
        #HAVE RECORDS TO PROCESS   
        pass     
    '''