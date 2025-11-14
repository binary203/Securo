#Импорты
from os import*

#Находит директорию проекта, нужно для того чтобы конфиг применился
app_dir = path.abspath(path.dirname(__file__))


#Базовый конфиг
class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
#! Конфиг для разработки, делитнуть на релизе!
class DevelopementConfig(BaseConfig):
    DEBUG = True
    
    SQLALCHEMY_DATABASE_URI = 'sqlite:///vulns.db'
    
    