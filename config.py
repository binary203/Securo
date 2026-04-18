# Импорты
import os

# Находит директорию проекта, нужно для того чтобы конфиг применился
app_dir = os.path.abspath(os.path.dirname(__file__))


# Базовый конфиг
class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SECRET_KEY: str = "XP;W/\vD*BOQ_ieHYfEl1GJ!2}Z5[?S:A.7ykd6nL3c8qwpN+$bjt])MV#0z"


class DevelopmentConfig(BaseConfig):
    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///default.db"


class ProductionConfig(BaseConfig):
    DEBUG: bool = False
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL", "sqlite:///production.db"
    )
    SECRET_KEY: str = os.environ.get("SECRET_KEY", BaseConfig.SECRET_KEY)
    SEMGREP_API_TOKEN: str = os.environ.get("SEMGREP_APP_TOKEN", "")
    GEMINI_API: str = os.environ.get("GEMINI_API_KEY", "")
