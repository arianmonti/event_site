from flask import Flask


app = Flask(__name__)

from . import db
db.init_app(app)


from app import routes




