from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

from pf import portfolio
from pf import mforder
from pf import mfsiporder
from pf import fund
from pf import mforderapi_crawl
from pf import jwtdecodenoverify as jwtnoverify
from pf import loginsignup
from pf import notification
from pf import notificationprocessing
from pf import registrationfatca
from pf import fileupload
from pf import bankifsc
from pf import mforderpaystatus_bg
from pf import mforderapijobs
from pf import dashboard
'''
@app.after_request
def after_request(response):
    userid,entityid=' '*2
    # get the request object somehow
    if request.method!='OPTIONS':
        userid,entityid = jwtnoverify.validatetoken(request)

        print("inside after requetst end ----------------------------------------------------------------------------------")
        print(request.content_length)
        print(userid)
        print(entityid)
        
        
        print (response.content_length)
        print("inside after requetst end ----------------------------------------------------------------------------------")
    
    return response
'''