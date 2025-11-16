#Импорты
from app import app, db

app.config.from_object('config.DevelopementConfig')
def init_db():
    with app.app_context():
        db.create_all()
        print("Таблицы созданы!")
        
        #Проверка созданных таблиц
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Список созданных таблиц: {tables}")

if __name__ == '__main__':
    init_db()
    app.run()
