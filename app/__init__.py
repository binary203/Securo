from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import config

#Cоздание приложения
app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

#Инициализация расширений
db = SQLAlchemy(app)
migrate = Migrate(app=app, db=db)

from . import views
from . import models