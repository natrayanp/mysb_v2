from flask import Flask
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

from loginservices import loginsignup
from loginservices import dbfunc
from loginservices import jwtdecodenoverify