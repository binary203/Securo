#Файл для всех роутов
#Импорты
from app import app, db
from flask import render_template, request, redirect, url_for, session, flash
from flask_login import login_required, login_user,current_user, logout_user
from werkzeug.security import check_password_hash
from .models import User
import sqlalchemy as sql
from .forms import LoginForm
#Базовая страница
@app.route('/')
def index():
    return render_template('index.html')

#Логин
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    
    form = LoginForm()    
    if form.validate_on_submit():
        user = db.session.scalar(sql.select(User).where(User.username == form.username.data))
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))  
    return render_template('login.html', title='Login', form=form)
    
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Пользователь с таким именем уже существует!')
            return redirect(url_for('registration'))
        
        new_user = User(username=username)
        new_user.set_password(password)
        
        # Сохраняем в БД
        db.session.add(new_user)
        db.session.commit()
        
        # Автоматически логиним пользователя
        login_user(new_user)
        flash('Регистрация успешна!')
        return redirect('/')    
    return render_template('register.html')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')
        
#Сам сканнер
@app.route('/profile/scan', methods=['POST', 'GET'])
def scan():
    return render_template('scan.html')

#Результаты скана
@app.route('/profile/results', methods=['POST'])
def results():
    return "Results page"

@app.route('/profile/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы')
    return redirect(url_for('index'))