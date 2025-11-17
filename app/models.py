from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

db = SQLAlchemy(app)

# юзеры для авторизации, если отменяем ее то делитнуть
class user(db.Model): 
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), nullable=False, unique=True)
    password = db.Column(db.String(32), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    scans = db.relationship('scan', backref='users', lazy=True)
    
    def __repr__(self):
        return "<{}:{}>".format(self.id, self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    
# сканы для подачи кода в сайт и запуска анализа коода юзера
class scan(db.Model):
    __tablename__ = 'scans'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date_scan = db.Column(db.DateTime, nullable = False, default=lambda: datetime.now(timezone.utc))
    code_language = db.Column(db.String(50), nullable=False) 
    code = db.Column(db.Text, nullable=False)
    vulnerabilities = db.relationship('vulnerability', backref='scans', lazy=True)
    
# найденные уязвимости для вывода результатов
class vulnerability(db.Model):
    __tablename__='vulnerabilities'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    line = db.Column(db.Integer, nullable=False)
    code_snippet = db.Column(db.Text)
    vulnerability_type = db.Column(db.String(50), nullable=False)
    risk_level = db.Column(db.String(25), nullable=False)
    scan = db.relationship('scan', backref='vulnerabilities')
