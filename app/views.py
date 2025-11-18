# Файл для всех роутов
# Импорты
from app import app, db
from flask import render_template, request, redirect, url_for, session, flash
from flask_login import login_required, login_user, current_user, logout_user
from .models import User
import sqlalchemy as sql
from .forms import LoginForm
from .services import run_scanner_service


# Базовая страница
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/profile/")
@login_required
def profile():
    return render_template("profile.html")


# Логин
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("scan"))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sql.select(User).where(User.username == form.username.data)
        )

        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for("index"))
    return render_template("login.html", title="Login", form=form)


@app.route("/registration", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Пользователь с таким именем уже существует!")
            return redirect(url_for("registration"))

        new_user = User(username=username)
        new_user.set_password(password)

        # Сохраняем в БД
        db.session.add(new_user)
        db.session.commit()

        # Автоматически логиним пользователя
        login_user(new_user)
        flash("Регистрация успешна!")
        return redirect("/")
    return render_template("register.html")

# Сам сканнер
@app.route("/profile/scan", methods=["POST", 'GET'])
@login_required  # проверка на авторизацию
def scan():
    # запуск сканера и ввод
    try:
        scanner = run_scanner_service()
        code = request.form.get("code")
        repo = request.form.get("repo_url")
        # проверка входных данных
        if code:
            result = scanner.run_code_scan(code)
        elif repo:
            result = scanner.run_repo_scan(repo)
        else:
            flash("Укажите код или URL репозитория на GitHub")
            return redirect(url_for("index"))
        return render_template("results.html", result=result)

    # если ошибка то кинет на index
    except ValueError as e:
        flash(f"Ошибка конфигурации: {str(e)}")
        return redirect(url_for("index"))
    except RuntimeError as e:
        flash(f"Ошибка сканирования: {str(e)}")
        return redirect(url_for("index"))
    except Exception as e:
        flash(f"Ошибка: {str(e)}")
        return redirect(url_for("index"))

# Результаты скана
@app.route("/profile/results", methods=["POST"])
def results():
    return "Results page"


@app.route("/profile/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы")
    return redirect(url_for("index"))
