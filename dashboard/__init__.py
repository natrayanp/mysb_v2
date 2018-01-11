from flask import Flask
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)


from dashboard import test
from dashboard import notification
from dashboard import dbfunc
#This to be removed and moved to allprocessing START
from dashboard import notificationprocessing
#This to be removed and moved to allprocessing END