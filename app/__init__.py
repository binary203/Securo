import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import config
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Cоздание приложения
app = Flask(__name__)
_config_name = os.environ.get('FLASK_CONFIG', 'DevelopmentConfig')
app.config.from_object(f'config.{_config_name}')

# Инициализация расширений
db = SQLAlchemy(app)
migrate = Migrate(app=app, db=db)
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Для доступа к этой странице необходимо войти."
login_manager.login_message_category = "warning"

# Rate limiter
# memory:// сбрасывается при рестарте сервера.
# Для продакшена Redis: storage_uri="redis://localhost:6379"
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)

from . import views
from . import models
