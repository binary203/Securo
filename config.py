#Импорты
from os import*

#Находит директорию проекта, нужно для того чтобы конфиг применился
app_dir = path.abspath(path.dirname(__file__))


#Базовый конфиг
class BaseConfig:
    SECRET_KEY: str = r'XP;W/\vD*BOQ_ieHYfEl1GJ!2}Z5[?S:A.7ykd6nL3c8qwpN+$bjt])MV#0z' #! Секретный ключ сгенерированный лично мной, не палить, пока не нужен
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    
#! Конфиг для разработки, делитнуть на релизе!
class DevelopmentConfig(BaseConfig):
    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = 'sqlite:///default.db'