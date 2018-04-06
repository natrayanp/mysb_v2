from bsestarmfapi import app
#from .hello_world import app
from flask import request, make_response, jsonify, Response, redirect
from bsestarmfapi import settings
from datetime import datetime

import requests
import json
import zeep


@app.route('/executepf',methods=['POST','OPTIONS'])
def executepf():
    print("try")
    if request.method=='OPTIONS':
        print ("inside executepf options")
        return jsonify({'body':'success'})

    elif request.method=='POST':   
        print ("inside executepf post")
        
        print((request))        
        print(request.headers)
        userid,entityid=jwtnoverify.validatetoken(request)
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print(userid,entityid)
        payload= request.get_json()
        print(payload)
        
        #This code should be there in webapp and not in API START
        con,cur=db.mydbopncon()

        #update the pf values to INPROGRESS.  Only for NEW items
        command = cur.mogrify("""update webapp.pfmforlist set ormffndstatus = 'INPROGRESS'
                                WHERE orormflistid IN (select ormflistid FROM webapp.pfmflist 
                                WHERE orportfolioid = (SELECT DISTINCT pfPortfolioid FROM webapp.pfmaindetail where pfPortfolioid = %s AND pfuserid = %s AND entityid = %s ) AND entityid = %s)
                                AND UPPER(ormffndstatus) = 'NEW' AND entityid = %s;
                                """,(payload,userid,entityid,entityid,entityid,))
        print(command)
        cur, dbqerr = db.mydbfunc(con,cur,command)

        if cur.closed == True:
            if(dbqerr['natstatus'] == "error" or dbqerr['natstatus'] == "warning"):
                dbqerr['statusdetails']="main update  Failed"
            resp = make_response(jsonify(dbqerr), 400)
            return(resp)
        
        con.commit()
        #This code should be there in webapp and not in API END
        
        command = cur.mogrify("""SELECT orormfpflistid webapp.pfmforlist
                        WHERE orormflistid IN (select ormflistid FROM webapp.pfmflist 
                        WHERE orportfolioid = (SELECT DISTINCT pfPortfolioid FROM webapp.pfmaindetail where pfPortfolioid = %s AND pfuserid = %s AND entityid = %s ) AND entityid = %s)
                        AND UPPER(ormffndstatus) = 'INPROGRESS' AND entityid = %s;
                        """,(payload,userid,entityid,entityid,entityid,))

        records=[]
        for record in cur:  
            records.append(record[0])  
        
        print(records)
        #to be deleted when deploying: END
        '''
        client = boto3.client(‘lambda’)
        d = {'calID': '92dqiss5bg87etcqeeamlmob2g@group.calendar.google.com', 'datada': '2017-12-22T16:40:00+01:00', 'dataa': '2017-12-22T17:55:00+01:00', 'email': 'example@hotmail.com'}
        responselam = client.invoke(
            FunctionName='arn:aws:lambda:eu-west-1:13737373737:function:test',
            LogType='None',
            Payload=json.dumps(d)
        )
        if(responselam['StatusCode']==202):
            print(success)
            send success response with message processing in progress
        else:
            print(failure)
            update the pf values back to NEW
            send error response      
        '''



        # call lamdba function without expecting response to start background processing 
       
        cur.close()
        con.close()
        return jsonify({'body':'success fss'})
