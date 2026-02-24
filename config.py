# Импорты
import os
from dotenv import load_dotenv

# Загружаем .env из папки app/
load_dotenv(os.path.join(os.path.abspath(os.path.dirname(__file__)), "app", ".env"))

# Находит директорию проекта
app_dir = os.path.abspath(os.path.dirname(__file__))


# Базовый конфиг
class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SECRET_KEY: str = os.environ.get(
        "SECRET_KEY", "fallback-dev-key-change-in-production"
    )


class DevelopmentConfig(BaseConfig):
    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///default.db"


class ProductionConfig(BaseConfig):
    DEBUG: bool = False
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL", "sqlite:///production.db"
    )
    SEMGREP_API_TOKEN: str = os.environ.get("SEMGREP_APP_TOKEN", "")
    GEMINI_API: str = os.environ.get("GEMINI_API_KEY", "")
