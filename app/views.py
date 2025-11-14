#Файл для всех роутов, классов

#Импорты
from app import app
from flask import render_template, request, redirect, url_for

#Базовая страница
@app.route('/')
def index():
    return render_template('index.html')
    if request.method == 'POST':
        return redirect('/scan')
        
#Сам сканнер
@app.route('/scan', methods=['POST'])
def scan():
    return render_template('scan.html')

#Результаты скана
@app.route('/results')
def results():
    if request.method == 'POST':
        if 'see_results' in request.form:
            return 'sex'