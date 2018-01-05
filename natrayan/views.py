from natrayan import app
#from .hello_world import app
from flask import request, make_response, jsonify, Response, redirect


import requests
import json



@app.route('/api',methods=['GET','POST','OPTIONS'])
def index():
    if request.method=='OPTIONS':
        print ("inside options")
        return 'natrayan in OPTIONS'

    elif request.method=='POST':
        print ("inside POST")
        payload = request.stream.read().decode('utf8')
        print(type(payload))
        print(payload)
        
        #Include code to store the order details in DB before sending it to API
        
        

        #Post request forwarded to Kite
        return redirect("https://kite.trade/connect/basket", code=307)


        '''
        print(request.headers)
        urlss = "https://kite.trade/connect/basket"
        kiteresp = requests.post(urlss, data=payload, headers=request.headers, allow_redirects=False)
        print('########### watch ##########')
        print(kiteresp.request.headers)
        print('########### watch ##########')
        print (request.environ)
        #Code to Check if the request is getting redirected
        if kiteresp.history:
            print ("Request was redirected")
            for resp in kiteresp.history:
                print (resp.status_code, resp.url)
        else:
            print ("Request was not redirected")
            for resp in kiteresp.history:
                print (resp.status_code, resp.url)
            print ("Final destination:")
            print (kiteresp.status_code, kiteresp.url)

        #make the response to return the redirected url
        #kiteresp.headers['Location']= kiteresp.headers['Location'].replace('https://90jr17xd3j.execute-api.ap-southeast-1.amazonaws.com', 'https://kite.trade')        
        kiteresp.headers['Location']= kiteresp.headers['Location'].replace('https://127.0.0.1', 'https://kite.trade')    
        

        headers = [(name, value) for (name, value) in kiteresp.headers.items()]
        print(headers)
        #print (request.environ['HTTP_ORIGIN'])
        my_response = Response(kiteresp.content, kiteresp.status_code, headers) 
        print ("Response prepared...Forwarding it to browser")
        
        return my_response
        '''
    else:
        print ("inside ELSE")
        return 'natrayan in ELSE'