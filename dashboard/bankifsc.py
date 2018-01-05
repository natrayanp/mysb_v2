from dashboard import app
from flask import redirect, request,make_response
from datetime import datetime
from flask import jsonify

import psycopg2
import jwt
import requests
import json


      
@app.route('/bankdet1',methods=['GET','POST','OPTIONS'])
def bankdets1():
#This is called by setjws service
    if request.method=='OPTIONS':
        print("inside bankdets options")
        return 'ok'

    elif request.method=='POST':
        print("inside bankdetails POST")
        payload= request.get_json()
        print(payload)
        reqdataifsc=payload['ifsc']
        print(reqdataifsc)
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
  
        #This is to be moved to a configurable place
        conn_string = "host='localhost' dbname='postgres' user='postgres' password='password123'"
        #This is to be moved to a configurable place
        con=psycopg2.connect(conn_string)
        cur = con.cursor()

        command = cur.mogrify("select * from bankifscmaster ifsc where ifsc = %s;",(reqdataifsc,) )
        cur, dbqerr = mydbfunc(con,cur,command)
        print(cur)
        print(dbqerr)
        print(type(dbqerr))
        print(dbqerr['natstatus'])
        if cur.closed == True:
            if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                dbqerr['statusdetails']="IFSC Fetch failed"
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

        #if len(records) == 0:
        if cur.count == 0:
            bank, ifsc, micr, branch, address, contact, city, district, state = ['']*9
            failed=True
            errormsg='Not a valid IFSC'
        else:
            bank, ifsc, micr, branch, address, contact, city, district, state = records[0]
            failed=False
            errormsg=''

  
        bankdetailresp = bank+' '+address+'    '+city+' '+state
        print(bankdetailresp)
        return (json.dumps({'bank':bank,'ifsc':ifsc,'micr':micr,'branch':branch,'address':address,'contact':contact, 'city':city, 'district':district, 'state':state,'failed':failed,'errormsg':errormsg}))
    
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


