from flask import Flask
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

from pf import portfolio
from pf import mforder
from pf import mfsiporder
from pf import fund
