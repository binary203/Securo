#Файл для всех роутов
#Импорты
from app import app, db
from flask import render_template, request, redirect, url_for, session, flash
from flask_login import login_required, login_user,current_user, logout_user
from werkzeug.security import check_password_hash
from .models import User


#Базовая страница
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user/')
def profile():
    return render_template('profile.html')

#Логин
@app.route('/user/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authinticated:
        return redirect('/scan')
    if request.method == 'POST':
        user = session.get(User)


@app.route('/user/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        new_user = User(username=username)
        new_user.set_password(password)
        
        # Сохраняем в БД
        db.session.add(new_user)
        db.session.commit()
        
        # Автоматически логиним пользователя
        login_user()
        flash('Регистрация успешна!')
        return redirect('/')    
    return render_template('register.html')

        
#Сам сканнер
@app.route('user/scan', methods=['POST'])
def scan():
    return render_template('scan.html')

#Результаты скана
@app.route('user/results', methods=['POST'])
def results():
    return 