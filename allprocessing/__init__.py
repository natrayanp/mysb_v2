from flask import Flask
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

from allprocessing import notificationprocessing
from allprocessing import dbfunc
from allprocessing import Registrationstatus