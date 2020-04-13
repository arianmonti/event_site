from flask import Flask
from app.config import Config

app = Flask(__name__)
app.config.from_object(Config)

from . import db
db.init_app(app)



from app import routes




