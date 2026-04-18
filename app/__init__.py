from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import config
import os
from flask_login import LoginManager

# Создание приложения
app = Flask(__name__)

_config_map = {
    "production": "config.ProductionConfig",
    "development": "config.DevelopmentConfig",
}
_flask_config = os.environ.get("FLASK_CONFIG", "development").lower()
app.config.from_object(_config_map.get(_flask_config, "config.DevelopmentConfig"))

# Инициализация расширений
db = SQLAlchemy(app)
migrate = Migrate(app=app, db=db)
login_manager = LoginManager(app)
login_manager.login_view = "login"

from . import views
from . import models
