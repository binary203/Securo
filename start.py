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


# Инициализация БД при любом способе запуска (python start.py ИЛИ gunicorn start:app)
init_db()


if __name__ == "__main__":
    app.run()
