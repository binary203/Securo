#Импорты
from os import*

#Находит директорию проекта
app_dir = path.abspath(path.dirname(__file__))


#Базовый конфиг
class BaseConfig:
    SECRET_KEY: str = r'XP;W/\vD*BOQ_ieHYfEl1GJ!2}Z5[?S:A.7ykd6nL3c8qwpN+$bjt])MV#0z'
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    
class DevelopmentConfig(BaseConfig):
    DEBUG: bool = False
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///default.db'
    SEMGREP_API_TOKEN=''
