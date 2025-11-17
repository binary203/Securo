#Файл для всех роутов
#Импорты
from app import app
from flask import render_template, request, redirect, url_for, session, flash
from flask_login import login_required, login_user,current_user, logout_user
from werkzeug.security import check_password_hash


#Базовая страница
@app.route('/')
def index():
    return render_template('index.html')

#Логин
@app.route('/login/', methods=['GET', 'POST'])
def login():
    return render_template('login.html')
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        user = user.query.filter_by(username=login)
        if user and check_password_hash(pwhash=password):
            login_user(user)
            return redirect('/scan')

@app.route('/reg', methods=['GET', 'POST'])
def registration():
    return render_template('register.html')
    if request.method == 'POST':
        username = request.form['login']
        password = request.form['password']
        
        existing_user = user.query.filter_by(username=login)
        if existing_user:
            flash('Такой пользователь уже есть!')
            return redirect('/reg')
        
        new_user = user(username=username)
        new_user.set_password(password)
        
        # Сохраняем в БД
        db.session.add(new_user)
        db.session.commit()
        
        # Автоматически логиним пользователя
        login_user(new_user)
        flash('Регистрация успешна!')
        return redirect('/')
        
#Сам сканнер
@app.route('/scan', methods=['POST'])
def scan():
    return render_template('scan.html')

#Результаты скана
@app.route('/results', methods=['POST'])
def results():
    return 