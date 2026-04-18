# Импорты
from app import app, db

def init_db():
    """Инициализация базы данных"""
    with app.app_context():
        # Создаем все таблицы
        db.create_all()
        print("Таблицы базы данных созданы!")

        # Проверяем существующие таблицы
        from sqlalchemy import inspect

        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print("Существующие таблицы:", tables)


if __name__ == "__main__":
    init_db()
    app.run()
