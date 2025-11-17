from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import config
from flask_login import LoginManager

#Cоздание приложения
app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

#Инициализация расширений
db = SQLAlchemy(app)
migrate = Migrate(app=app, db=db)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from . import views

@login_manager.user_loader
def load_user():
    return models.user.query.get(int(user_id))


