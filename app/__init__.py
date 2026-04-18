import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

_config_map = {
    "production": "config.ProductionConfig",
    "development": "config.DevelopmentConfig",
}
_flask_config = os.environ.get("FLASK_CONFIG", "development").lower()
app.config.from_object(_config_map.get(_flask_config, "config.DevelopmentConfig"))

db = SQLAlchemy(app)
migrate = Migrate(app=app, db=db)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Для доступа к этой странице необходимо войти."
login_manager.login_message_category = "warning"

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)

from . import views
from . import models
