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

      
@app.route('/natkeys',methods=['POST'])
def setkeyw():
    #This is called by setjws service

    cred = credentials.Certificate('./serviceAccountKey.json')
    default_app = firebase_admin.initialize_app(cred)

    print("inside natkeys")
    payload1 = request.stream.read().decode('utf8')

    payload1=json.loads(payload1)
    id_token=id_token
    print(type(payload1))
    print(id_token)
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    decoded_token = auth.verify_id_token(id_token)
    uid = decoded_token['uid']


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
