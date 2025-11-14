from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import config

#Cоздание приложения
app = Flask(__name__)
app.config.from_object('config.DevelopementConfig')

#Инициализация расширений
db = SQLAlchemy(app)

from . import views

