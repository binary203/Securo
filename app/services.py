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

load_dotenv(override=True)

LLM_MODEL = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-Coder-7B-Instruct")

_APP_DIR = os.path.abspath(os.path.dirname(__file__))
_PROJECT_ROOT = os.path.abspath(os.path.join(_APP_DIR, os.pardir))
_DEFAULT_LOCAL_RULESET = os.path.join(_APP_DIR, "semgrep_rules", "default.yml")

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

        # Если токен задан, но пуст (например, SEMGREP_APP_TOKEN= в .env), удаляем его
        if "SEMGREP_APP_TOKEN" in env and not env["SEMGREP_APP_TOKEN"].strip():
            del env["SEMGREP_APP_TOKEN"]

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

        # Project-local venv (works even if venv is not activated)
        if os.name == "nt":
            local_venv_semgrep = os.path.join(
                _PROJECT_ROOT, ".venv", "Scripts", "semgrep.exe"
            )
        else:
            local_venv_semgrep = os.path.join(_PROJECT_ROOT, ".venv", "bin", "semgrep")
        if os.path.exists(local_venv_semgrep):
            possible_paths.append(local_venv_semgrep)

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

        cls._semgrep_path = ""
        return None

    def __init__(self, ruleset: str | None = None):
        # Default to offline local ruleset to avoid semgrep.dev timeouts.
        self.fallback_ruleset = (
            _DEFAULT_LOCAL_RULESET if os.path.exists(_DEFAULT_LOCAL_RULESET) else None
        )
        self.ruleset = ruleset or os.getenv("SEMGREP_RULESET") or "p/owasp-top-ten"
        semgrep_cmd = self._find_semgrep()
        if semgrep_cmd is None:
            raise RuntimeError("semgrep CLI не найден.")

        if isinstance(semgrep_cmd, list):
            self._semgrep_cmd = semgrep_cmd
        else:
            self._semgrep_cmd = [semgrep_cmd]

    @staticmethod
    def _should_replace_lines(existing_lines) -> bool:
        if existing_lines is None:
            return True
        if not isinstance(existing_lines, str):
            return True
        s = existing_lines.strip()
        if s == "":
            return True
        s_low = s.lower()
        return s_low in {"requires login", "login required", "unauthorized"}

    @staticmethod
    def _read_text_file(path: str) -> str | None:
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except OSError:
            return None

    @classmethod
    def _extract_snippet(
        cls,
        file_path: str,
        start_line: int | None,
        end_line: int | None,
        context: int = 2,
    ) -> str | None:
        if not file_path or not isinstance(file_path, str):
            return None
        if not start_line or not isinstance(start_line, int) or start_line < 1:
            return None
        if not end_line or not isinstance(end_line, int) or end_line < 1:
            end_line = start_line

        content = cls._read_text_file(file_path)
        if content is None:
            return None

        lines = content.splitlines()
        if not lines:
            return None

        start_idx = max(1, start_line - context) - 1
        end_idx = min(len(lines), end_line + context)  # slicing end is exclusive
        snippet_lines = lines[start_idx:end_idx]
        if not snippet_lines:
            return None
        return "\n".join(snippet_lines).strip("\n")

    @classmethod
    def _hydrate_result_snippets(
        cls, semgrep_json: dict, base_dir: str | None = None
    ) -> dict:
        if not isinstance(semgrep_json, dict):
            return semgrep_json

        results = semgrep_json.get("results")
        if not isinstance(results, list):
            return semgrep_json

        for finding in results:
            if not isinstance(finding, dict):
                continue

            extra = finding.get("extra")
            if extra is None or not isinstance(extra, dict):
                extra = {}
                finding["extra"] = extra

            if not cls._should_replace_lines(extra.get("lines")):
                continue

            rel_path = finding.get("path")
            if not isinstance(rel_path, str) or not rel_path:
                continue

            if base_dir:
                file_path = os.path.join(base_dir, rel_path)
            else:
                file_path = rel_path

            start_line = None
            end_line = None
            start = finding.get("start")
            end = finding.get("end")
            if isinstance(start, dict):
                start_line = start.get("line")
            if isinstance(end, dict):
                end_line = end.get("line")

            snippet = cls._extract_snippet(file_path, start_line, end_line, context=2)
            if snippet:
                extra["lines"] = snippet

        return semgrep_json

    def _run_semgrep_json(self, target: str, ruleset: str) -> dict:
        print(f"DEBUG: Запуск Semgrep с набором правил: {ruleset}")
        result = subprocess.run(
            self._semgrep_cmd
            + [
                "--config",
                ruleset,
                "--max-memory",
                "5000",
                "--json",
                target,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,
            env=self._get_env(),
        )

        if result.returncode != 0:
            # Попытка извлечь читаемую ошибку из JSON ответа Semgrep
            try:
                err_data = json.loads(result.stdout)
                if "errors" in err_data and err_data["errors"]:
                    error_msg = "; ".join(
                        [e.get("message", "Unknown error") for e in err_data["errors"]]
                    )
                else:
                    error_msg = (result.stderr or result.stdout or "").strip()
            except (json.JSONDecodeError, TypeError):
                error_msg = (result.stderr or result.stdout or "").strip()

            if "401" in error_msg:
                error_msg += " [HINT: Проверьте SEMGREP_APP_TOKEN в .env. Если он неверный, удалите переменную.]"

            if error_msg == "":
                error_msg = (
                    "Semgrep завершился с ошибкой без текста. "
                    "Частая причина: недоступен ruleset или проблемы сети/прокси."
                )
            raise RuntimeError(
                f"Ошибка сканирования (код {result.returncode}): {error_msg}"
            )

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            raise RuntimeError(f"Ошибка парсинга результатов: {result.stdout[:200]}")

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

            try:
                semgrep_json = self._run_semgrep_json(temp_file, self.ruleset)
            except RuntimeError as e:
                # Фоллбек на локальные правила (полезно, если ruleset = p/... и semgrep.dev недоступен)
                if self.fallback_ruleset and self.ruleset != self.fallback_ruleset:
                    print(
                        f"DEBUG: Ошибка с правилами '{self.ruleset}'. Переключение на fallback: {self.fallback_ruleset}"
                    )
                    print(f"DEBUG: Текст ошибки: {e}")
                    semgrep_json = self._run_semgrep_json(
                        temp_file, self.fallback_ruleset
                    )
                else:
                    raise e

            return self._hydrate_result_snippets(semgrep_json)

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

            print(f"DEBUG: Запуск Semgrep (repo) с набором правил: {self.ruleset}")
            scan = subprocess.run(
                self._semgrep_cmd
                + [
                    "--config",
                    self.ruleset,
                    "--max-memory",
                    "8000",
                    "--json",
                    "--exclude",
                    "test/",
                    "--exclude",
                    "tests/",
                    "--exclude",
                    "*.min.js",
                    "--exclude",
                    "*.test.js",
                    "--exclude",
                    "*.spec.js",
                    repo_dir,
                ],
                capture_output=True,
                text=True,
                timeout=1200,
                encoding="utf-8",
                errors="replace",
                env=self._get_env(),
            )

            if scan.returncode != 0:
                # Попробуем фоллбек на локальные правила, если основной ruleset не сработал
                if self.fallback_ruleset and self.ruleset != self.fallback_ruleset:
                    print(
                        f"DEBUG: Ошибка с правилами '{self.ruleset}'. Переключение на fallback: {self.fallback_ruleset}"
                    )
                    try:
                        err_data = json.loads(scan.stdout)
                        for err in err_data.get("errors", []):
                            print(f"DEBUG: Semgrep API Error: {err.get('message')}")
                    except json.JSONDecodeError:
                        print(f"DEBUG: Ошибка Semgrep (stderr): {scan.stderr}")
                        print(f"DEBUG: Ошибка Semgrep (stdout): {scan.stdout}")
                    semgrep_json = self._run_semgrep_json(
                        repo_dir, self.fallback_ruleset
                    )
                    return self._hydrate_result_snippets(
                        semgrep_json, base_dir=repo_dir
                    )

                error_msg = (scan.stderr or scan.stdout or "").strip()
                if error_msg == "":
                    error_msg = (
                        "Semgrep завершился с ошибкой без текста. "
                        "Частая причина: недоступен ruleset (например, semgrep.dev) или проблемы сети/прокси."
                    )
                raise RuntimeError(
                    f"Ошибка сканирования (код {scan.returncode}): {error_msg}"
                )
            try:
                semgrep_json = json.loads(scan.stdout)
                # Для репозитория path обычно относительный — используем base_dir
                return self._hydrate_result_snippets(semgrep_json, base_dir=repo_dir)
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

        try:
            semgrep_json = self._run_semgrep_json(file_path, self.ruleset)
        except RuntimeError as e:
            if self.fallback_ruleset and self.ruleset != self.fallback_ruleset:
                print(
                    f"DEBUG: Ошибка с правилами '{self.ruleset}'. Переключение на fallback: {self.fallback_ruleset}"
                )
                print(f"DEBUG: Текст ошибки: {e}")
                semgrep_json = self._run_semgrep_json(file_path, self.fallback_ruleset)
            else:
                raise e

        return self._hydrate_result_snippets(semgrep_json)

    # публичный метод для сканирования файла
    def run_file_scan(self, file_path: str) -> dict:
        if not file_path or not file_path.strip():
            raise ValueError("Путь к файлу не указан")
        return self._run_file_scan(file_path)


# фабричная функция для views.py
def run_service():
    return SemgrepCLIService()
