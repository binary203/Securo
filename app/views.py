# Импорты
from app import app, db, limiter
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, login_user, current_user, logout_user
from .models import User
import sqlalchemy as sql
from .forms import LoginForm, ScanForm, RegistrationForm
from .services import run_service, run_LLM
import tempfile
import os
import shutil


# Индекс страница
@app.route("/")
def index():
    return render_template("index.html")


# Профиль
@app.route("/profile/")
@login_required
def profile():
    return render_template("profile.html")


# Логин
@app.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("profile"))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sql.select(User).where(User.username == form.username.data)
        )

        if user is None or not user.check_password(form.password.data):
            flash("Неверное имя пользователя или пароль", "error")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for("index"))
    return render_template("login.html", title="Login", form=form)


# Регистрация
@app.route("/registration", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def registration():
    if current_user.is_authenticated:
        return redirect(url_for("profile"))

    form = RegistrationForm()

    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("Не удалось создать аккаунт. Пользователь уже существует.", "error")
            return redirect(url_for("registration"))

        new_user = User(username=form.username.data)
        new_user.set_password(password=form.password.data)

        db.session.add(new_user)
        db.session.commit()

        flash("Регистрация прошла успешно! Войдите в аккаунт.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


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

            uploaded_files = form.file.data
            uploaded_files = [f for f in uploaded_files if f.filename]

            temp_dir_path = None

            if uploaded_files:
                if len(uploaded_files) > 5:
                    flash("Максимум 5 файлов за раз")
                    return render_template("scan.html", form=form)

                temp_dir_path = tempfile.mkdtemp()

                try:
                    for file in uploaded_files:
                        filename = file.filename
                        if not filename:
                            continue

                        from werkzeug.utils import secure_filename

                        safe_filename = secure_filename(filename)
                        if not safe_filename:
                            safe_filename = "uploaded_file"

                        file.seek(0, 2)
                        size = file.tell()
                        file.seek(0)

                        if size > 20 * 1024 * 1024:
                            flash(f"Файл {filename} слишком большой (>20MB)")
                            shutil.rmtree(temp_dir_path)
                            return render_template("scan.html", form=form)

                        save_path = os.path.join(temp_dir_path, safe_filename)
                        file.save(save_path)

                    result = scanner.run_file_scan(temp_dir_path)

                finally:
                    if temp_dir_path and os.path.exists(temp_dir_path):
                        shutil.rmtree(temp_dir_path)

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


@app.route("/api/ai", methods=["POST"])
@login_required
def AI():
    try:
        data = request.json
        user_command = data.get("user_command")
        AI_lang = data.get("AI_lang", "ru")
        code_snippet = data.get("code_snippet", "")

        if not user_command:
            return jsonify({"error": "Требуется команда или запрос."}), 400

        response = run_LLM(user_command, AI_lang, code_snippet)
        return jsonify({"reply": response})

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Внутренняя ошибка сервера: {str(e)}"}), 500


# Результаты скана
@app.route("/profile/results", methods=["POST"])
def results():
    return "Results page"


# Выход
@app.route("/profile/logout")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из системы")
    return redirect(url_for("index"))


# Обработчик ошибки 429
@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template("429.html"), 429
