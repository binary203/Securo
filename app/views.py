# Файл для всех роутов
# Импорты
from app import app, db
from flask import render_template, request, redirect, url_for, session, flash
from flask_login import login_required, login_user, current_user, logout_user
from .models import User
import sqlalchemy as sql
from .forms import LoginForm, ScanForm
from .services import run_service
import tempfile
import os


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
@app.route("/profile/scan", methods=["POST", "GET"])
@login_required  # проверка на авторизацию
def scan():
    # запуск сканера и ввод
    form = ScanForm()

    try:
        if form.validate_on_submit():
            scanner = run_service()
            code = form.code.data.strip() if form.code.data else ""
            repo_url = form.repo_url.data.strip() if form.repo_url.data else ""
            uploaded_file = form.file.data
            temp_file_path = None

            if uploaded_file and uploaded_file.filename:
                if uploaded_file.filename.strip() == "":
                    flash("Имя файла не должно быть пустым")
                    return render_template("scan.html", form=form)

                # проверка размера файла
                uploaded_file.seek(0, 2)
                file_size = uploaded_file.tell()
                uploaded_file.seek(0)

                if file_size == 0:
                    flash("Файл не должен быть пустым")
                    return render_template("scan.html", form=form)
                elif file_size > 20 * 1024 * 1024:  # 20 MB (подсчет в байтах)
                    flash("Файл не должен превышать 20 МБ")
                    return render_template("scan.html", form=form)

                file_ext = os.path.splitext(uploaded_file.filename)[1]
                if uploaded_file.filename.lower() == "dockerfile":
                    suffix = ""
                else:
                    suffix = file_ext

                # сохранение временного файла
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=suffix
                ) as tmp_file:
                    uploaded_file.save(tmp_file.name)
                    temp_file_path = tmp_file.name
                try:
                    # сканирование
                    result = scanner.run_file_scan(temp_file_path)
                finally:
                    # удаление в конце
                    if temp_file_path and os.path.exists(temp_file_path):
                        os.remove(temp_file_path)
            # проверка входных данных
            elif code:
                result = scanner.run_code_scan(code)
            elif repo_url:
                result = scanner.run_repo_scan(repo_url)
            else:
                flash("Вставьте код, URL репозиторий на GitHub или загрузите файл")
                return render_template("scan.html", form=form)

            # проверка наличия результата
            if not result or not isinstance(result, dict):
                flash("Результаты отсутствуют.")
                return render_template("scan.html", form=form)

            return render_template("results.html", result=result)

    # проверка ошибки, перенаправляет обратно на скан
    except ValueError as e:
        flash(f"Ошибка конфигурации: {str(e)}")
        return render_template("scan.html", form=form)
    except RuntimeError as e:
        flash(f"Ошибка сканирования: {str(e)}")
        return render_template("scan.html", form=form)
    except Exception as e:
        flash(f"Ошибка: {str(e)}")
        return render_template("scan.html", form=form)
    return render_template("scan.html", form=form)


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
