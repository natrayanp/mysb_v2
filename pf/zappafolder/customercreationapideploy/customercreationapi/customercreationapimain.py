from flask import Flask
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

from customercreationapi import cust
from customercreationapi import filuploadapi
#import views