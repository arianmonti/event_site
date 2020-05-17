from . import db
from flask import Flask
import app.config as config

app = Flask(__name__)
app.config.from_object(config.Config)
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER 

db.init_app(app)

from app import routes
