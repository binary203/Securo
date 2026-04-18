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
from wtforms.validators import DataRequired, Optional, Length, EqualTo, Regexp

class LoginForm(FlaskForm):
    username = StringField("Имя", validators=[DataRequired(), Length(min=3, max=32)])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember_me = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")

class RegistrationForm(FlaskForm):
    username = StringField(
        "Имя пользователя",
        validators=[
            DataRequired(),
            Length(min=3, max=32, message="Имя должно быть от 3 до 32 символов"),
        ],
    )
    password = PasswordField(
        "Пароль",
        validators=[
            DataRequired(),
            Length(min=6, message="Пароль должен содержать минимум 6 символов"),
        ],
    )
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
    repo_url = StringField(
        "Repository URL",
        validators=[
            Optional(),
            Regexp(
                r"^https://(github\.com|gitlab\.com)/.+",
                message="URL должен начинаться с https://github.com/ или https://gitlab.com/",
            ),
        ],
    )
    file = MultipleFileField(
        "Upload File",
        validators=[
            Optional(),
        ],
        render_kw={"multiple": True},
    )
    submit = SubmitField("Scan Code")
