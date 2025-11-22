# Файл для всех роутов
# Импорты
from app import app, db
from flask import render_template, request, redirect, url_for, session, flash
from flask_login import login_required, login_user, current_user, logout_user
from .models import User
import sqlalchemy as sql
from .forms import LoginForm, ScanForm
from .services import run_service


# Базовая страница
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/profile/", methods=["GET", "POST"])
@login_required
def profile():
    return render_template("profile.html")


# Логин
@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("profile"))

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
    form = ScanForm()
    
    try:
        if request.method == "POST":
            scanner = run_service()
            code = request.form.get("code", "").strip()
            repo_url = request.form.get("repo", "").strip()
            
            # проверка входных данных
            if code:
                result = scanner.run_code_scan(code)
            elif repo_url:
                result = scanner.run_repo_scan(repo_url)
            else:
                flash("Укажите код или URL репозитория на GitHub")
                return render_template('scan.html', form=form)
            
            # проверка наличия результата
            if not result or not isinstance(result, dict):
                flash("Результаты отсутствуют.")
                return render_template('scan.html', form=form)

            return render_template("results.html", result=result)

    # проверка ошибки, перенаправляет обратно на скан
    except ValueError as e:
        flash(f"Ошибка конфигурации: {str(e)}")
        return render_template('scan.html', form=form)
    except RuntimeError as e:
        flash(f"Ошибка сканирования: {str(e)}")
        return render_template('scan.html', form=form)
    except Exception as e:
        flash(f"Ошибка: {str(e)}")
        return render_template('scan.html', form=form)
    return render_template('scan.html', form=form)

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
