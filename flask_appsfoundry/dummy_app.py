from flask import Flask
from flask_babel import Babel


# dummy app for flask appsfoundry test purposes
dummy_app = Flask(__name__)
babel = Babel(dummy_app)