from natrayan import app
from flask import redirect, request
#from kiteconnect import KiteConnect
from datetime import datetime

import firebase_admin
from firebase_admin import credentials

import jwt
import requests
import json
import boto3

@app.route('/login',methods=['GET'])
def loginroute():
    print("inside login route")
    kite = KiteConnect(api_key="uptxfbd1y845rxva")
    print(kite.login_url())
    return redirect(kite.login_url(), code=302)



@app.route('/nat',methods=['GET'])
def redirets():
    print(request.args.get("status"))
    if (request.args.get("status") == "success"):  
        print ("inside login success handler")    
        print ("requesttoken is:")    
        print(request.args.get("request_token"))
        
        try:
            kite = KiteConnect(api_key="uptxfbd1y845rxva")
            
            '''
            #prod code START

            user = kite.request_access_token(request.args.get("request_token"), secret="your_secret")
            
            #prod code END
            '''

            #######################   mock STARTS  #######################

            #url = "http://mockbin.org/bin/b43a20ad-54c8-498c-b5fe-868f14d41dda"  --> full json
            url = "http://mockbin.org/bin/7cfccdc7-fda7-41fe-8662-0e4b4456790d"


            querystring = {"foo":["bar","baz"]}

            payload = "foo=bar&bar=baz"
            headers = {
                'accept': "application/json",
                'content-type': "application/x-www-form-urlencoded"
                }

            response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

            print(response.text)
            

            user=json.loads(response.text)
            print(user)
            print(type(user))
            print(user["access_token"])

            #######################   mock ENDS  #######################


            kite.set_access_token(user["access_token"])           


            natkey=user["public_token"]
            print(user["public_token"])
            # Code to save this in DynamoDB
            #   1)Save access token against user id and set userid as the cookie
            #dynamodb = boto3.resource('dynamodb')   #for production
            dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8081')
            table = dynamodb.Table('tknmgr')
            table.put_item(
                Item={
                     'publictoken': user["public_token"],                     
                     'userid': user["user_id"],
                     'email': user["email"],
                     'accesstoken': user["access_token"],                     
                     'username': user["user_name"]
                }
            )


            print(user["user_id"], "has logged in")
            # Code to save this in DynamoDB


        except Exception as e:
            print("Authentication failed", str(e))
            raise
        
        '''
        # Get the list of positions.
        # Save these in Dynamodb and do the analysis to see any diff between holding and our records
        print(kite.positions())
        print(kit.holdings())
        print(kite.margins("equity"))
        print(kite.margins("commodity"))


        '''
        #set cookies and return to Dashboard
        #return redirect ("http://localhost:4200/loginchk?natkey="+natkey,302)
        print("before return")
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        #Redirected to angular authchk
        return redirect ("http://localhost:4200/authchk?natkey="+natkey,302)
   

      

    elif (request.args.get("status") == "cancelled"):
        #Order was cancelled by user in the order placement screen.  we can go back to order placement screen
        print("inside order cancelled")
        #Don't do anything here
        return("ordercancelled")

        
    elif (request.args.get("status") == "completed"):
        print("inside order completed")
        #Order was placed
        kite = KiteConnect(api_key="uptxfbd1y845rxva")        
        #   1) Check the cookie to get the user details and get the access token

        kite.set_access_token("access_token_from_db")
        #   2) Immediately check for the placed order and get order id 
        print(kite.positions())
        orderdata = kite.positions()
        
        #   4) Update the data base with the order id and status
        print(orderdata["status"])
        print(orderdata["order_id"])
        #   5) Respond to user with order placement completed, go and check the status.
        if(orderdate["status"] == "REJECTED"):
            print(orderdata["status_message"])
        elif(orderdata["status"] == "OPEN"):
            print("order placed:  Check back status later")
        elif(orderdata["status"] == "COMPLETE"):          
            print("order completed")
        elif(orderdata["status"] == "CANCELLED"):            
            print(orderdata["status_message"])

    else:
        #This should not happen
        print("inside Unknown postback url handler")
        
@app.route('/natkeys',methods=['POST'])
def setkeyw():
    #This is called by setjws service

    cred = credentials.Certificate('path/to/serviceAccountKey.json')
    default_app = firebase_admin.initialize_app(cred)


    print("inside natkeys")
    payload1 = request.stream.read().decode('utf8')

    payload1=json.loads(payload1)
    print(type(payload1))
    print(payload1['natkey'])
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    #Generate JWT START

    #Retrive natkey from DB START
    
    #dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8081')
    dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8081')
    table = dynamodb.Table('tknmgr')
    response = table.get_item(
                Key={
                    'publictoken': '5dd3f8d7c8aa91cff362de9f73212e28'        
                    }
    )
    item=response['Item']    
    dbnatkey = item['publictoken']
    username = item['username']
    userid = item['userid']
    print(item)
    print(username)
    
    #dbnatkey = item
    #dbnatkey="5dd3f8d7c8aa91cff362de9f73212e28"
         
    
    #Retrive natkey from DB END

    if(payload1.get("natkey") == dbnatkey):
        print("inside if of natkeys")
        
        #get secret key from DB START

        dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8081')
        table = dynamodb.Table('natseckeymgr')
        response = table.get_item(
                                Key={
                                    'natseckey': 'secret'        
                                }
        )
        items=response['Item']   
        natseckey=items['secretkey']       

        #natseckey="secret" 
        
        #get secret key from DB END

        #Call JWT to generate JWT START
        natjwt =  jwt.encode({"natkey": dbnatkey,"username": username,"userid": userid}, natseckey, algorithm="HS256")
        
        #Call JWT to generate JWT END

        return (json.dumps({"natjwt" :natjwt.decode("utf-8")}))
    else:
        print("inside elseif of natkeys")
        pass


@app.route('/Portfolio',methods=['POST'])
def pfscreen():
    pass
