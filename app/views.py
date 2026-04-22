# Импорты
from app import app, db, limiter
from flask import render_template, request, redirect, url_for, flash, jsonify, Response
from flask_login import login_required, login_user, current_user, logout_user
from .models import User, Scans, Vulnerability
import sqlalchemy as sql
from .forms import LoginForm, ScanForm, RegistrationForm, LogoutForm
from .services import run_service, run_LLM
from werkzeug.utils import secure_filename
import tempfile
import os
import shutil
import json


# Форма для CSRF токена на глобальных кнопках выхода
@app.context_processor
def inject_logout_form():
    return {"logout_form": LogoutForm()}


# Индекс страница
@app.route("/")
def index():
    return render_template("index.html")


# Профиль
@app.route("/profile/")
@login_required
def profile():
    scan_count = Scans.query.filter_by(user_id=current_user.id).count()
    vuln_base = (
        db.session.query(Vulnerability)
        .join(Scans)
        .filter(Scans.user_id == current_user.id)
    )
    vuln_count = vuln_base.count()
    high_count = vuln_base.filter(
        Vulnerability.risk_level.in_(["ERROR", "error", "CRITICAL", "critical", "HIGH", "high"])
    ).count()
    medium_count = vuln_base.filter(
        Vulnerability.risk_level.in_(["WARNING", "warning", "MEDIUM", "medium"])
    ).count()
    low_count = vuln_base.filter(
        Vulnerability.risk_level.in_(["INFO", "info", "LOW", "low"])
    ).count()
    return render_template(
        "profile.html",
        scan_count=scan_count,
        vuln_count=vuln_count,
        high_count=high_count,
        medium_count=medium_count,
        low_count=low_count,
    )


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
            flash(
                "Не удалось зарегистрироваться. Проверьте данные и попробуйте ещё раз.",
                "error",
            )
            return render_template("register.html", form=form)

        new_user = User(username=form.username.data)
        new_user.set_password(password=form.password.data)

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash("Регистрация прошла успешно!", "success")
        return redirect(url_for("profile"))

    return render_template("register.html", form=form)


# Сам сканнер
@app.route("/profile/scan", methods=["POST", "GET"])
@login_required
@limiter.limit("20 per hour; 5 per minute", methods=["POST"])
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

            # Сохранение результатов в БД
            try:
                scan_record = Scans(
                    user_id=current_user.id,
                    code_language=result.get("language", "unknown"),
                    code=code or repo_url or "file upload",
                )
                db.session.add(scan_record)
                db.session.flush()

                for finding in result.get("results", []):
                    severity = "unknown"
                    if isinstance(finding.get("extra"), dict):
                        severity = finding["extra"].get("severity", "unknown")

                    vuln = Vulnerability(
                        scan_id=scan_record.id,
                        title=finding.get("check_id", "Unknown")[:100],
                        description=finding.get("message", ""),
                        line=finding.get("start", {}).get("line", 0),
                        code_snippet=finding.get("extra", {}).get("lines", ""),
                        vulnerability_type=finding.get("check_id", "unknown")[:50],
                        risk_level=severity[:25],
                    )
                    db.session.add(vuln)

                db.session.commit()
            except Exception:
                db.session.rollback()
                scan_record = None

            return render_template(
                "results.html",
                result=result,
                scan_id=scan_record.id if scan_record else None,
            )

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
        history = data.get("history", [])

        if not user_command:
            return jsonify({"error": "Требуется команда или запрос."}), 400

        response = run_LLM(user_command, AI_lang, code_snippet, history=history)
        return jsonify({"reply": response})

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        return jsonify({"error": f"Внутренняя ошибка сервера: {str(e)}"}), 500




# История сканирований
@app.route("/profile/history")
@login_required
def history():
    page = request.args.get("page", 1, type=int)
    if page < 1:
        page = 1
    per_page = 15

    pagination = (
        Scans.query.filter_by(user_id=current_user.id)
        .order_by(Scans.date_scan.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    scan_data = []
    for s in pagination.items:
        vulns = Vulnerability.query.filter_by(scan_id=s.id).all()
        high = sum(
            1 for v in vulns
            if v.risk_level.upper() in ("ERROR", "CRITICAL", "HIGH")
        )
        medium = sum(
            1 for v in vulns
            if v.risk_level.upper() in ("WARNING", "MEDIUM")
        )
        low = sum(
            1 for v in vulns
            if v.risk_level.upper() in ("INFO", "LOW")
        )
        scan_data.append({
            "scan": s,
            "total": len(vulns),
            "high": high,
            "medium": medium,
            "low": low,
        })
    return render_template("history.html", scan_data=scan_data, pagination=pagination)


# Просмотр результатов из истории
@app.route("/profile/history/<int:scan_id>")
@login_required
def scan_detail(scan_id):
    scan = Scans.query.filter_by(id=scan_id, user_id=current_user.id).first_or_404()
    vulns = Vulnerability.query.filter_by(scan_id=scan_id).all()
    result = {
        "language": scan.code_language,
        "results": [
            {
                "check_id": v.title,
                "message": v.description,
                "start": {"line": v.line},
                "extra": {
                    "severity": v.risk_level,
                    "lines": v.code_snippet,
                },
            }
            for v in vulns
        ],
        "errors": [],
    }
    return render_template("results.html", result=result, scan_id=scan_id, scan=scan)


# Экспорт результатов сканирования в JSON
@app.route("/api/export/<int:scan_id>")
@login_required
def export_scan(scan_id):
    scan = Scans.query.filter_by(id=scan_id, user_id=current_user.id).first_or_404()
    vulns = Vulnerability.query.filter_by(scan_id=scan_id).all()
    data = {
        "scan_id": scan.id,
        "date": scan.date_scan.isoformat(),
        "language": scan.code_language,
        "vulnerabilities": [
            {
                "id": v.id,
                "title": v.title,
                "description": v.description,
                "line": v.line,
                "code_snippet": v.code_snippet,
                "vulnerability_type": v.vulnerability_type,
                "risk_level": v.risk_level,
            }
            for v in vulns
        ],
    }
    return Response(
        json.dumps(data, ensure_ascii=False, indent=2),
        mimetype="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=securo_scan_{scan_id}.json"
        },
    )


# Выход
@app.route("/profile/logout", methods=["POST"])
@login_required
def logout():
    form = LogoutForm()
    if form.validate_on_submit():
        logout_user()
        flash("Вы вышли из системы")
        return redirect(url_for("index"))
    flash("Не удалось выйти. Попробуйте ещё раз.", "error")
    return redirect(url_for("profile"))


# Обработчик HTTP 429
@app.errorhandler(429)
def ratelimit_handler(e):
    return render_template("429.html"), 429
