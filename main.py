from flask import Flask
from flask_cors import CORS
from config import SQLALCHEMY_DATABASE_URI
app = Flask(__name__)
CORS(app)
from app import *
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

if __name__ == '__main__':
    app.run(debug=True)
