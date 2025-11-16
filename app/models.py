from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config.from_object('config.DevelopementConfig')

db = SQLAlchemy(app)

# юзеры для авторизации, если отменяем ее то делитнуть
class users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    scans = db.relationship('scans', backref='users', lazy=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
# сканы для подачи кода в сайт и запуска анализа коода юзера
class scans(db.Model):
    __tablename__ = 'scans'
    vulnerability=db.relationship('vulnerabilities', backref='scans', lazy=True)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_scan = db.Column(db.DateTime, nullable = False, default=datetime.now())
    code_language =db.Column(db.String(20), nullable=False) 
    code = db.Column(db.Text, nullable=False)
    
# уязвимости для вывода результатов
class vulnerabilities(db.Model):
    __tablename__='vulnerabilities'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    line = db.Column(db.Integer, nullable=False)
    code_snippet = db.Column(db.Text)
    type = db.Column(db.String(46), nullable=False)
    risk_level = db.Column(db.String(25), nullable=False)

with app.app_context():
    db.create_all()