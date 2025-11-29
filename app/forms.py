# Импорты
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional, Length


# Форма для логина
class LoginForm(FlaskForm):
    username = StringField("Имя", validators=[DataRequired()])
    password = PasswordField("Пароль", validators=[DataRequired()])
    remember_me = BooleanField("Запомнить меня")
    submit = SubmitField("Войти")


class ScanForm(FlaskForm):
    code = TextAreaField("Code", validators=[Optional(), Length(max=10000)])
    repo_url = StringField("Repository URL", validators=[Optional()])
    file = FileField(
        "Upload File",
        validators=[
            Optional(),
            FileAllowed(
                [
                    "py",
                    "js",
                    "ts",
                    "java",
                    "c",
                    "cpp",
                    "go",
                    "rb",
                    "php",
                    "cs",
                    "scala",
                    "kt",
                    "rs",
                    "swift",
                    "lua",
                    "ml",
                    "tf",
                    "yaml",
                    "json",
                    "html",
                    "sh",
                    "cls",
                    "clj",
                    "dart",
                    "ex",
                    "jsx",
                    "jl",
                    "jsonnet",
                    "lisp",
                    "r",
                    "scm",
                    "sol",
                    "tsx",
                    "xml",
                    "", # dockerfile
                ],
                "Неподдерживаемый тип файла",
            ),
        ],
    )
    submit = SubmitField("Scan Code")
