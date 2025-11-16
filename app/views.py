#Файл для всех роутов, классов

#Импорты
from app import app
from flask import render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash, gen_salt

#Базовая страница
@app.route('/')
def index():
    return render_template('index.html')
    
        
#Сам сканнер
@app.route('/scan', methods=['POST'])
def scan():
    return render_template('scan.html')

#Результаты скана
@app.route('/results', methods=['POST'])
def results():
    return 