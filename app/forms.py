# Импорты
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    TextAreaField,
    MultipleFileField,
)
from wtforms.validators import DataRequired, Optional, Length, EqualTo


# Форма для логина
class LoginForm(FlaskForm):
    username = StringField("Имя", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember_me = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")


class RegistrationForm(FlaskForm):
    username = StringField("Имя", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Повторите пароль",
        validators=[
            DataRequired(),
            EqualTo("password", message="Пароли должны совпадать"),
        ],
    )
    submit = SubmitField("Зарегистрироваться")


class ScanForm(FlaskForm):
    code = TextAreaField("Code", validators=[Optional(), Length(max=10000)])
    repo_url = StringField("Repository URL", validators=[Optional()])
    file = MultipleFileField(
        "Upload File",
        validators=[
            Optional(),
        ],
        render_kw={"multiple": True},
    )
    submit = SubmitField("Scan Code")
