#Импорты
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional, Length

#Форма для логина
class LoginForm(FlaskForm):
  username = StringField('Имя', validators=[DataRequired()])
  password = PasswordField('Пароль', validators=[DataRequired()])
  remember_me = BooleanField('Запомнить меня')
  submit = SubmitField('Войти')

class ScanForm(FlaskForm):
    code = TextAreaField('Code', validators=[Optional(), Length(max=10000)])
    repo_url = StringField('Repository URL', validators=[Optional()])
    submit = SubmitField('Scan Code') 
