import os
import warnings
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.abspath(os.path.dirname(__file__)), "app", ".env"))

app_dir = os.path.abspath(os.path.dirname(__file__))

class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "fallback-dev-key-change-in-production")
    SEMGREP_API_TOKEN: str = os.environ.get("SEMGREP_APP_TOKEN", "")
    GEMINI_API: str = os.environ.get("GEMINI_API_KEY", "")


class DevelopmentConfig(BaseConfig):
    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///default.db"


class ProductionConfig(BaseConfig):
    DEBUG: bool = False
    if not os.environ.get("DATABASE_URL"):
        warnings.warn(
            "DATABASE_URL не задан. Используется SQLite.",
            stacklevel=2,
        )
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL", "sqlite:///production.db"
    )
