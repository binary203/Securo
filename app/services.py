from .models import db, Scans, Vulnerability, User
from .LANG_PATTERNS import LANG_PATTERNS
from openai import OpenAI
from dotenv import load_dotenv
import subprocess
import tempfile
import os
import json
import shutil
import re
import sys
import certifi

load_dotenv()

LLM_MODEL = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-Coder-7B-Instruct")

LLM_client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.getenv("HF_TOKEN"),
)


def run_LLM(user_command: str, AI_lang: str, code_snippet: str) -> str:
    MAX_CODE_LENGTH = 10000

    # Валидация входных данных
    if not user_command:
        raise ValueError("запрос не может быть пустым")

    if len(user_command) > MAX_CODE_LENGTH:
        raise ValueError(f"Запрос слишком длинный. Максимум {MAX_CODE_LENGTH} символов")

    if not AI_lang:
        AI_lang = "ru"

    if code_snippet is None:
        code_snippet = ""
    elif len(code_snippet) > MAX_CODE_LENGTH:
        raise ValueError(f"Запрос слишком длинный. Максимум {MAX_CODE_LENGTH} символов")

    system_prompt = """
    You are highly skilled in cybersecurity, secure coding, vulnerability analysis, code quality, refactoring, and debugging. 
    Your responsibilities include:
    detecting vulnerabilities, bugs, and logical errors;

    explaining security issues clearly and professionally;

    fixing and rewriting insecure code;

    improving code quality, performance, and maintainability;

    generating safe, production-ready code.

    Always provide precise, practical, technically accurate explanations and improvements.
    Follow secure coding best practices (OWASP, CERT, SEI, CWE).
    When showing fixed code, return the full corrected snippet.
"""
    if user_command == "/explain" and AI_lang == "ru":
        task = """
        Объясни уязвимости, баги или логические ошибки в данном коде. Опиши:

        в чём заключается проблема;

        почему она опасна или приводит к сбоям;

        как её могут эксплуатировать либо к чему она приведёт;

        как правильно её исправить (концептуально).

        Дай подробное и понятное объяснение.
"""

    elif user_command == "/explain" and AI_lang == "eng":
        task = """
        Explain the vulnerabilities, bugs, or logical issues in the provided code. Describe:

        what the issue is;

        why it is a problem;

        how it can be exploited or cause failures;

        how it should be fixed (conceptually).

        Be clear and detailed.
"""

    elif user_command == "/fix" and AI_lang == "ru":
        task = """Исправь все уязвимости, баги и логические ошибки в коде. Верни полностью исправленную и безопасную версию кода. Соблюдай лучшие практики безопасного кодинга и делай код готовым к продакшену."""
    elif user_command == "/fix" and AI_lang == "eng":
        task = """Fix all vulnerabilities, bugs, and logical errors in the code. Return a fully corrected and secure version of the code. Follow secure coding best practices and ensure the final code is production-ready."""

    elif user_command == "/improve" and AI_lang == "ru":
        task = """Отрефактори и улучшай код. Сделай его чище, безопаснее, быстрее и удобнее для поддержки. Улучшай читаемость, структуру, производительность и соблюдай лучшие практики разработки."""
    elif user_command == "/improve" and AI_lang == "eng":
        task = """Refactor and improve the code. Make it cleaner, faster, safer, and more maintainable. Enhance readability, structure, performance, and follow best engineering practices."""

    else:
        task = f"Answer the user's question or fulfill the request: {user_command}"

    prompt = f"""Task: {task}. Code:\n{code_snippet}"""

    try:
        completion = LLM_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            timeout=120,
        )

        return completion.choices[0].message.content or ""

    except Exception as e:
        if "timeout" in str(e).lower() or "timed out" in str(e).lower():
            raise RuntimeError("Превышено время ожидания ответа от LLM (120 секунд).")
        elif "rate limit" in str(e).lower():
            raise RuntimeError("Превышен лимит запросов к LLM API. Попробуйте позже.")
        else:
            raise RuntimeError(f"Ошибка вызова LLM: {str(e)}")


class SemgrepCLIService:
    # список поддерживаемых языков
    Language = {
        "python": ".py",
        "javascript": ".js",
        "typescript": ".ts",
        "java": ".java",
        "c": ".c",
        "cpp": ".cpp",
        "go": ".go",
        "ruby": ".rb",
        "php": ".php",
        "csharp": ".cs",
        "scala": ".scala",
        "kotlin": ".kt",
        "rust": ".rs",
        "swift": ".swift",
        "lua": ".lua",
        "ocaml": ".ml",
        "terraform": ".tf",
        "yaml": ".yaml",
        "json": ".json",
        "html": ".html",
        "dockerfile": "Dockerfile",
        "bash": ".sh",
        "apex": ".cls",
        "clojure": ".clj",
        "dart": ".dart",
        "elixir": ".ex",
        "jsx": ".jsx",
        "julia": ".jl",
        "jsonnet": ".jsonnet",
        "lisp": ".lisp",
        "r": ".r",
        "scheme": ".scm",
        "solidity": ".sol",
        "tsx": ".tsx",
        "xml": ".xml",
        "cairo": ".cairo",
        "circom": ".circom",
        "hack": ".hack",
        "move": ".move",
    }

    _STR_PATTERN = re.compile(
        r"('''.*?'''|\"\"\".*?\"\"\"|'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\")",
        re.DOTALL,
    )
    _BLOCK_COMM_PATTERN = re.compile(r"/\*.*?\*/", re.DOTALL)
    _LINE_COMM_PATTERN = re.compile(r"(?m)//.*?$")

    _semgrep_path = None

    @staticmethod
    def _get_env():
        env = os.environ.copy()
        env["SEMGREP_SKIP_VERSION_CHECK"] = "1"
        env["SEMGREP_SEND_METRICS"] = "off"

        env["SSL_CERT_FILE"] = certifi.where()

        return env

    @classmethod
    def reset_semgrep_cache(cls):
        cls._semgrep_path = None

    @classmethod
    def _find_semgrep(cls):
        if cls._semgrep_path is not None and cls._semgrep_path != "":
            return cls._semgrep_path

        if cls._semgrep_path == "":
            return None

        possible_paths = []

        path = shutil.which("semgrep")
        if path:
            possible_paths.append(path)

        if hasattr(sys, "prefix") and sys.prefix != sys.base_prefix:
            if os.name == "nt":  # Windows
                venv_semgrep = os.path.join(sys.prefix, "Scripts", "semgrep.exe")
            else:  # Linux
                venv_semgrep = os.path.join(sys.prefix, "bin", "semgrep")

            if os.path.exists(venv_semgrep):
                possible_paths.append(venv_semgrep)

        for path in possible_paths:
            try:
                result = subprocess.run(
                    [path, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    env=cls._get_env(),
                )
                if (
                    result.returncode == 0
                    or "semgrep" in result.stdout.lower()
                    or "semgrep" in result.stderr.lower()
                ):
                    cls._semgrep_path = path
                    return cls._semgrep_path
            except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
                continue

        try:
            result = subprocess.run(
                [sys.executable, "-m", "semgrep", "--version"],
                capture_output=True,
                text=True,
                timeout=10,
                env=cls._get_env(),
            )
            if (
                result.returncode == 0
                or "semgrep" in result.stdout.lower()
                or "semgrep" in result.stderr.lower()
            ):
                cls._semgrep_path = [sys.executable, "-m", "semgrep"]
                return cls._semgrep_path
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        cls._semgrep_path = ""
        return None

    def __init__(self, ruleset="p/security-audit"):
        self.ruleset = ruleset
        semgrep_cmd = self._find_semgrep()
        if semgrep_cmd is None:
            raise RuntimeError(
                "semgrep CLI не найден. Убедитесь, что semgrep установлен (pip install semgrep) и доступен в PATH."
            )

        if isinstance(semgrep_cmd, list):
            self._semgrep_cmd = semgrep_cmd
        else:
            self._semgrep_cmd = [semgrep_cmd]

    # удаление комментарие и строк
    def _code_cleaner(self, code: str) -> str:
        cleaned = self._STR_PATTERN.sub(" ", code)
        cleaned = self._BLOCK_COMM_PATTERN.sub(" ", cleaned)
        cleaned = self._LINE_COMM_PATTERN.sub(" ", cleaned)
        return cleaned.lower()

    # удаление скрытых символов
    def _code_normalizer(self, code: str) -> str:
        if code.startswith("\ufeff"):
            code = code[1:]
        # Zero-Widths
        code = code.replace("\u200b", "")
        code = code.replace("\u200c", "")
        code = code.replace("\u200d", "")
        # BOM
        code = code.replace("\ufeff", "")
        # нормализация переносов строк
        code = code.replace("\u202a", "")
        code = code.replace("\r\n", "\n").replace("\r", "\n")
        return code

    # определение языка по паттернам
    def _detect_language(self, code: str) -> str:
        code_lower = self._code_cleaner(code)
        stripped_code = code.strip()

        if stripped_code.startswith("{") or stripped_code.startswith("["):
            try:
                json.loads(stripped_code)
                return "json"
            except json.JSONDecodeError:
                pass

        best_match = "python"  # по умолчанию
        max_matches = 0

        for lang, patterns in LANG_PATTERNS.items():
            matches = 0
            for pattern in patterns:
                if re.search(
                    pattern,
                    code_lower,
                    (
                        re.IGNORECASE
                        if lang in ["dockerfile", "bash", "html", "yaml", "xml"]
                        else 0
                    ),
                ):
                    matches += 1

            if lang == "bash" and code_lower.startswith("#!"):
                matches += 5
            if lang == "php" and "<?php" in code_lower:
                matches += 5
            if lang == "html" and "<!doctype" in code_lower:
                matches += 5
            if lang == "python" and "import os" in code_lower:
                matches += 1

            if matches > max_matches:
                max_matches = matches
                best_match = lang

        if max_matches == 0:
            return "python"

        return best_match

    # внутренний метод сканирования кода
    def _run_code_scan(self, code: str) -> dict:
        current_language = self._detect_language(code)
        ext = self.Language.get(current_language, ".py")

        # нормализация кода перед записью
        normalized_code = self._code_normalizer(code)

        local_tmp_path = os.path.join(os.getcwd(), "local_temp")
        os.makedirs(local_tmp_path, exist_ok=True)

        with tempfile.TemporaryDirectory(dir=local_tmp_path) as tmpdir:
            # проверка докера
            if current_language == "dockerfile":
                temp_file = os.path.join(tmpdir, "Dockerfile")
            else:
                temp_file = os.path.join(tmpdir, f"code{ext}")
            # запись кода в файл
            with open(temp_file, "w", encoding="utf-8", newline="\n") as f:
                f.write(normalized_code)

            result = subprocess.run(
                self._semgrep_cmd
                + [
                    "--config",
                    self.ruleset,
                    "-q",
                    "--max-memory",
                    "3000",
                    "--json",
                    temp_file,
                ],
                capture_output=True,
                text=True,
                timeout=300,
                env=self._get_env(),
            )

            if result.returncode != 0:
                error_msg = (
                    result.stderr
                    or result.stdout
                    or "Неизвестная ошибка (пустой вывод)"
                )
                raise RuntimeError(
                    f"Ошибка сканирования (язык: {current_language}, файл: {temp_file}, код выхода: {result.returncode}): {error_msg}"
                )

            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                raise RuntimeError(
                    f"Ошибка парсинга результатов: {result.stdout[:200]}"
                )

    # публичный метод для сканирования кода
    def run_code_scan(self, code: str) -> dict:
        if not code or not code.strip():
            raise ValueError("Вставьте код для сканирования")
        return self._run_code_scan(code)

    # внутренний метод сканирования репозитория
    def _run_repo_scan(self, repo_url: str) -> dict:
        if not repo_url.startswith(("https://github.com/")) and not repo_url.startswith(
            ("https://gitlab.com/")
        ):
            raise ValueError("Поддерживаются только репозитории GitHub")

        git_path = shutil.which("git")
        if not git_path:
            raise RuntimeError("Клонировать репозиторий не получилось.")

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_dir = os.path.join(tmpdir, "repo")

            clone = subprocess.run(
                [git_path, "clone", "--depth", "1", repo_url, repo_dir],
                capture_output=True,
                text=True,
                timeout=60,
                # git clone обычно не требует этих переменных, но можно оставить env=None или os.environ
            )

            if clone.returncode != 0:
                raise RuntimeError(
                    f"Ошибка клонирования: {clone.stderr or clone.stdout}"
                )

            scan = subprocess.run(
                self._semgrep_cmd
                + [
                    "--config",
                    self.ruleset,
                    "-q",
                    "--max-memory",
                    "3000",
                    "--json",
                    repo_dir,
                ],
                capture_output=True,
                text=True,
                timeout=300,
                encoding="utf-8",
                errors="replace",
                env=self._get_env(),
            )

            if scan.returncode != 0:
                print("STDERR:", scan.stderr)
                print("STDOUT:", scan.stdout)
                raise RuntimeError(
                    f"Ошибка сканирования (код {scan.returncode}): {scan.stderr or scan.stdout}"
                )
            try:
                return json.loads(scan.stdout)
            except json.JSONDecodeError:
                raise RuntimeError(f"Ошибка парсинга результатов: {scan.stdout[:200]}")

    # публичный метод для сканирования репозитория
    def run_repo_scan(self, repo_url: str) -> dict:
        if not repo_url or not repo_url.strip():
            raise ValueError("Вставьте URL репозитория")
        return self._run_repo_scan(repo_url)

    # внутренний метод сканирования файла
    def _run_file_scan(self, file_path: str) -> dict:
        if not os.path.exists(file_path):
            raise ValueError(f"Файл не найден: {file_path}")

        if not os.path.isfile(file_path):
            raise ValueError(f"Указанный путь не является файлом: {file_path}")

        file_ext = os.path.splitext(file_path)[1].lower()
        file_name = os.path.basename(file_path).lower()

        detected_language = None
        for lang, ext in self.Language.items():
            if file_ext == ext or (file_name == "dockerfile" and lang == "dockerfile"):
                detected_language = lang
                break

        if not detected_language:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    code_content = f.read()
                detected_language = self._detect_language(code_content)
            except Exception as e:
                raise RuntimeError(f"Не удалось определить язык: {str(e)}")

        file_scan = subprocess.run(
            self._semgrep_cmd
            + [
                "--config",
                self.ruleset,
                "-q",
                "--max-memory",
                "3000",
                "--json",
                file_path,
            ],
            capture_output=True,
            text=True,
            timeout=300,
            env=self._get_env(),
        )

        if file_scan.returncode != 0:
            error = file_scan.stderr or file_scan.stdout or "Неизвестная ошибка"
            raise RuntimeError(
                f"Ошибка сканирования файла (язык: {detected_language}, файл: {file_path}): {error}"
            )

        try:
            return json.loads(file_scan.stdout)
        except json.JSONDecodeError:
            raise RuntimeError(f"Ошибка парсинга результата: {file_scan.stdout[:200]}")

    # публичный метод для сканирования файла
    def run_file_scan(self, file_path: str) -> dict:
        if not file_path or not file_path.strip():
            raise ValueError("Путь к файлу не указан")
        return self._run_file_scan(file_path)


# фабричная функция для views.py
def run_service():
    return SemgrepCLIService()
