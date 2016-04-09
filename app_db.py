from flask.ext.sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask import Flask
import os

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
socketio = SocketIO(app, async_mode='threading')
db = SQLAlchemy(app)
