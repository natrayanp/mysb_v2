from pf import app
from flask import redirect, request,make_response
from datetime import datetime
from flask import jsonify

import jwt
import requests
import json
      
#This job to trigger at 4 PM IST
def mforderallotschejb():
    '''
    mforderstatuspg_web (Purchase & Redemption) - Runs every day at 3,4,5,6,7,8,9,10 PM IST
                if status == "ALLOTMENT DONE":
                status = '6'
            elif status == "SENT TO RTA FOR VALIDATION":
                status = '5'
            elif status == "ORDER CANCELLED BY USER":
                status = '1'
            elif status == "PAYMENT NOT RECEIVED TILL DATE":
                status = '-1'
    '''
    #mforderallotpg_web - Runs every day at 5 (after mforderstatuspg_web),10 (after mforderstatuspg_web) PM IST