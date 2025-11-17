#Импорты
from app import app, db

app.config.from_object('config.DevelopmentConfig')

if __name__ == '__main__':
    app.run()
