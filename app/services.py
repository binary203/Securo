from .models import db, Scans, Vulnerability, User
import subprocess
import tempfile
import os
import json
import shutil
import re


class SemgrepCLIService:
    # список поддерпживаемых языков
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
    }

    _STR_PATTERN = re.compile(
        r"('''.*?'''|\"\"\".*?\"\"\"|'(?:\\.|[^'\\])*'|\"(?:\\.|[^\"\\])*\")",
        re.DOTALL,
    )
    _BLOCK_COMM_PATTERN = re.compile(r"/\*.*?\*/", re.DOTALL)
    _LINE_COMM_PATTERN = re.compile(r"(?m)//.*?$")

    def __init__(self, ruleset="p/ci"):
        self.ruleset = ruleset
        # проверка наличия semgrep
        try:
            subprocess.run(
                ["semgrep", "--version"], capture_output=True, text=True, timeout=5
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            raise RuntimeError("semgrep CLI не найден.")
    # удаление комментариев
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
        code = code.replace("\r\n", "\n").replace("\r", "\n")
        return code

    # определение языка по паттернам
    def _detect_language(self, code: str) -> str:
        code_lower = self._code_cleaner(code)
        stripped_code = code.strip()
        # Python
        if any(
            k in code_lower
            for k in ["def ", "import ", "from ", "print(", "class ", "__init__"]
        ):
            if not any(
                k in code_lower for k in ["function ", "var ", "let ", "const ", "=>"]
            ):
                return "python"

        # JavaScript
        elif any(
            k in code_lower
            for k in [
                "function ",
                "var ",
                "let ",
                "const ",
                "=>",
                "console.log",
                "document.",
            ]
        ):
            if "interface " not in code_lower and "type " not in code_lower:
                return "javascript"

        # TypeScript
        elif any(
            k in code_lower
            for k in ["interface ", "type ", ": string", ": number", ": boolean"]
        ):
            return "typescript"

        # Java
        elif any(
            k in code_lower
            for k in [
                "public class",
                "public static void",
                "import java.",
                "package java",
                "@override",
            ]
        ):
            return "java"

        # C/C++
        elif any(
            k in code_lower
            for k in ["#include", "int main", "printf", "cout", "std::", "namespace "]
        ):
            return (
                "cpp"
                if any(
                    k in code_lower
                    for k in ["cout", "std::", "namespace ", "class ", "template<"]
                )
                else "c"
            )

        # Go
        elif any(
            k in code_lower for k in ["package ", "func ", 'import "', ":= ", "go func"]
        ):
            return "go"

        # Ruby
        elif (
            any(
                k in code_lower
                for k in ["def ", "end", "require ", "class ", "module "]
            )
            and "def " in code_lower
        ):
            if "end" in code_lower and "print(" not in code_lower:
                return "ruby"

        # PHP
        elif any(
            k in code_lower
            for k in ["<?php", "$_", "->", "function ", "class ", "namespace "]
        ):
            if "<?php" in code_lower or "$" in code_lower[:100]:
                return "php"

        # C#
        elif any(
            k in code_lower
            for k in [
                "using system",
                "namespace ",
                "public class",
                "private ",
                "get;",
                "set;",
            ]
        ):
            if "using system" in code_lower or "namespace " in code_lower:
                return "csharp"

        # Scala
        elif any(
            k in code_lower
            for k in ["object ", "def ", "val ", "var ", "def ", "extends ", "trait "]
        ):
            if "object " in code_lower and "extends " in code_lower:
                return "scala"

        # Kotlin
        elif any(
            k in code_lower
            for k in [
                "fun ",
                "val ",
                "var ",
                "class ",
                "data class",
                "companion object",
            ]
        ):
            if "fun " in code_lower:
                return "kotlin"

        # Rust
        elif any(
            k in code_lower
            for k in ["fn ", "let ", "mut ", "struct ", "impl ", "use ", "::"]
        ):
            if "fn " in code_lower and "::" in code_lower:
                return "rust"

        # Swift
        elif any(
            k in code_lower
            for k in [
                "func ",
                "var ",
                "let ",
                "class ",
                "struct ",
                "import swift",
                "guard ",
            ]
        ):
            if "func " in code_lower and "import swift" in code_lower:
                return "swift"

        # Lua
        elif any(
            k in code_lower
            for k in ["function ", "local ", "end", "require(", "print("]
        ):
            if "local " in code_lower and "end" in code_lower:
                return "lua"

        # OCaml
        elif any(
            k in code_lower
            for k in ["let ", "in ", "match ", "with ", "type ", "module "]
        ):
            if "let " in code_lower and "in " in code_lower:
                return "ocaml"

        # Terraform
        elif any(
            k in code_lower
            for k in ["resource ", "provider ", "variable ", "output ", "terraform {"]
        ):
            return "terraform"

        # YAML
        elif any(
            k in code_lower for k in ["---", ":", "apiversion:", "kind:", "metadata:"]
        ):
            if code_lower.count(":") > 3 and "---" in code_lower:
                return "yaml"

        # JSON
        elif stripped_code.startswith("{") or stripped_code.startswith("["):
            try:
                json.loads(stripped_code)
                return "json"
            except json.JSONDecodeError:
                pass

        # HTML
        elif any(
            k in code_lower
            for k in ["<!doctype", "<html", "<head", "<body", "<div", "<script"]
        ):
            return "html"

        # Dockerfile
        elif any(
            k in code_lower
            for k in ["from ", "run ", "copy ", "workdir ", "expose ", "cmd "]
        ):
            if code_lower.startswith("from ") or "from " in code_lower[:50]:
                return "dockerfile"

        # Bash/Shell
        elif any(
            k in code_lower
            for k in ["#!/bin/bash", "#!/bin/sh", "echo ", "export ", "if [", "then "]
        ):
            if code_lower.startswith("#!") or "if [" in code_lower:
                return "bash"

        # Apex (Salesforce)
        elif any(
            k in code_lower
            for k in ["public class", "trigger ", "@istest", "database.", "sobject "]
        ):
            if "trigger " in code_lower or "@istest" in code_lower:
                return "apex"

        # Clojure
        elif any(
            k in code_lower for k in ["(def ", "(defn ", "(let ", "(if ", "(fn ", "ns "]
        ):
            if "(def " in code_lower or "(defn " in code_lower:
                return "clojure"

        # Dart
        elif any(
            k in code_lower
            for k in ["void main()", "class ", "import ", "dart:", "async ", "await "]
        ):
            if "void main()" in code_lower or "dart:" in code_lower:
                return "dart"

        # Elixir
        elif any(
            k in code_lower
            for k in ["defmodule ", "def ", "defp ", "defmacro ", "|>", "do: "]
        ):
            if "defmodule " in code_lower or "|>" in code_lower:
                return "elixir"

        # JSX
        elif any(
            k in code_lower
            for k in ["<div", "<component", "react.", "import react", "jsx", "return ("]
        ):
            if "<div" in code_lower or "react." in code_lower:
                if "interface " not in code_lower and ": string" not in code_lower:
                    return "jsx"

        # Julia
        elif any(
            k in code_lower
            for k in ["function ", "end", "using ", "import ", "::", "println("]
        ):
            if "function " in code_lower and "::" in code_lower:
                return "julia"

        # Jsonnet
        elif any(
            k in code_lower for k in ["local ", "function(", "self.", "super.", "std."]
        ):
            if "local " in code_lower and "std." in code_lower:
                return "jsonnet"

        # Lisp
        elif any(
            k in code_lower
            for k in ["(defun ", "(defvar ", "(setq ", "(if ", "(let ", "(lambda "]
        ):
            if "(defun " in code_lower or "(lambda " in code_lower:
                return "lisp"

        # R
        elif any(
            k in code_lower
            for k in ["<-", "function(", "library(", "data.frame", "ggplot2", "print("]
        ):
            if "<-" in code_lower and "function(" in code_lower:
                return "r"

        # Scheme
        elif any(
            k in code_lower
            for k in [
                "(define ",
                "(lambda ",
                "(let ",
                "(if ",
                "(cond ",
                "(car ",
                "(cdr ",
            ]
        ):
            if "(define " in code_lower and "(lambda " in code_lower:
                return "scheme"

        # Solidity
        elif any(
            k in code_lower
            for k in [
                "pragma solidity",
                "contract ",
                "function ",
                "modifier ",
                "event ",
                "mapping(",
            ]
        ):
            if "pragma solidity" in code_lower or "contract " in code_lower:
                return "solidity"

        # TSX
        elif any(
            k in code_lower
            for k in [
                "<div",
                "<component",
                "react.",
                "import react",
                "interface ",
                ": string",
            ]
        ):
            if "<div" in code_lower and ": string" in code_lower:
                return "tsx"

        # XML
        elif any(k in code_lower for k in ["<?xml", "<root", "<element", "<tag", "</"]):
            if "<?xml" in code_lower or ("<" in code_lower and "</" in code_lower):
                return "xml"

        return "python"  # по умолчанию

    # внутренний метод сканирования кода
    def _run_code_scan(self, code: str) -> dict:
        current_language = self._detect_language(code)
        ext = self.Language.get(current_language, ".py")

        # нормализация код перед записью
        normalized_code = self._code_normalizer(code)

        with tempfile.TemporaryDirectory() as tmpdir:
            # проверка докера
            if current_language == "dockerfile":
                temp_file = os.path.join(tmpdir, "Dockerfile")
            else:
                temp_file = os.path.join(tmpdir, f"code{ext}")
            # запись кода в файл
            with open(temp_file, "w", encoding="utf-8", newline="\n") as f:
                f.write(normalized_code)

            result = subprocess.run(
                ["semgrep", "--config", self.ruleset, "-q", "--json", temp_file],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Неизвестная ошибка"
                raise RuntimeError(
                    f"Ошибка сканирования (язык: {current_language}, файл: {temp_file}): {error_msg}"
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
        if not repo_url.startswith(("https://github.com/")):
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
            )

            if clone.returncode != 0:
                raise RuntimeError(
                    f"Ошибка клонирования: {clone.stderr or clone.stdout}"
                )

            scan = subprocess.run(
                ["semgrep", "--config", self.ruleset, "-q", "--json", repo_dir],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if scan.returncode != 0:
                raise RuntimeError(f"Ошибка сканирования: {scan.stderr or scan.stdout}")

            try:
                return json.loads(scan.stdout)
            except json.JSONDecodeError:
                raise RuntimeError(f"Ошибка парсинга результатов: {scan.stdout[:200]}")

    # публичный метод для сканирования репозитория
    def run_repo_scan(self, repo_url: str) -> dict:
        if not repo_url or not repo_url.strip():
            raise ValueError("Вставьте URL репозитория")
        return self._run_repo_scan(repo_url)


# фабричная функция для views.py
def run_service():
    return SemgrepCLIService()


"""
# использовать если имеется api token
class SemgrepAPIClient:
    # клиент для semgrep api
    def __init__(
        self, SEMGREP_API_TOKEN: str, base_url: str = 'https://semgrep.dev/api/v1'
    ):
        self.SEMGREP_API_TOKEN = SEMGREP_API_TOKEN
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {SEMGREP_API_TOKEN}",
            "Content-Type": "application/json",
        }

    # получить список deployments
    def get_deployments(self):
        url = f"{self.base_url}/deployments"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    # создать новый скан
    def create_scan(self, deployment_id: str, payload: dict):
        url = f"{self.base_url}/deployments/{deployment_id}/scans"
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    # получение статуса скана
    def get_scan_status(self, deployment_id: str, scan_id: str):
        url = f"{self.base_url}/deployments/{deployment_id}/scans/{scan_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        return data.get("Scans", {}).get("status", "unknown")

    # получение резултатов скана
    def get_scan_results(self, deployment_id: str, scan_id: str):
        url = f"{self.base_url}/deployments/{deployment_id}/scans/{scan_id}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

class SemgrepService:
    def __init__(self):
        token = current_app.config.get("SEMGREP_API_TOKEN")
        if not token:
            raise ValueError("API Токен отсутсутсвует")
        self.client = SemgrepAPIClient(SEMGREP_API_TOKEN=token)
        # загрузка deployment_id при инициализации
        try:
            deployments = self.client.get_deployments()
            if deployments.get("deployments") and len(deployments["deployments"]) > 0:
                self.deployment_id = deployments["deployments"][0]["id"]
            else:
                raise ValueError("Deployment не найден.")
        except Exception as e:
            raise ValueError(f"Ошибка получения deployment: {str(e)}")

    def run_code_scan(self, code: str):
        # отправка кода на скан
        payload = {
            "policy": "r2c-ci",
            "source": {"type": "inline",
                       "files": {"input_file": code}
            },
        }
        scan_id = self._create_scan(payload)
        self._wait_for_completion(scan_id)
        return self._fetch_results(scan_id)

    def run_repo_scan(self, repo_url: str):
        # отправка репозитория на скан, на выбор юзеру
        payload = {"policy": "r2c-ci",
                   "source": {"type": "git",
                              "url": repo_url}
        }
        scan_id = self._create_scan(payload)
        self._wait_for_completion(scan_id)
        return self._fetch_results(scan_id)

    def _create_scan(self, payload: dict) -> str:
        # cоздание задачи на сканирование
        response = self.client.create_scan(self.deployment_id, payload)
        scan_id = response.get("Scans", {}).get("id")
        if not scan_id:
            raise RuntimeError("scan_id не получен")
        return scan_id

    def _wait_for_completion(self, scan_id: str):
        # ожидание завершения сканирования
        max_attempts = 60  # +- 1 минута ожидания максимум
        attempt = 0
        while attempt < max_attempts:
            scan_status = self.client.get_scan_status(self.deployment_id, scan_id)
            if (
                scan_status == "succeeded"
                or scan_status == "completed"
                or scan_status == "succeed"
            ):
                break
            elif scan_status == "failed" or scan_status == "error":
                raise RuntimeError("Ошибка сканирования")
            else:
                time.sleep(2)
                attempt += 1
        else:
            raise RuntimeError("Превышено время ожидания завершения сканирования")

    def _fetch_results(self, scan_id: str) -> dict:
        # получение результатов сканирования
        if not scan_id:
            raise ValueError("scan_id пуст")
        results = self.client.get_scan_results(self.deployment_id, scan_id)
        return results


def run_scanner_service():  # фабричная функция
    return SemgrepService()
"""
