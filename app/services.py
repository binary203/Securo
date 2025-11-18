from flask import current_app
from .models import db, Scans, Vulnerability, User
from flask import request
import time


class SemgrepAPIClient:
    # клиент для semgrep api
    def __init__(
        self, SEMGREP_API_TOKEN: str, base_url: str = "https://semgrep.dev/api/v1"
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
        response = request.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    # создать новый скан
    def create_scan(self, deployment_id: str, payload: dict):
        url = f"{self.base_url}/deployments/{deployment_id}/scans"
        response = request.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    # получение статуса скана
    def get_scan_status(self, deployment_id: str, scan_id: str):
        url = f"{self.base_url}/deployments/{deployment_id}/scans/{scan_id}"
        response = request.get(url, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        return data.get("Scans", {}).get("status", "unknown")

    # получение резултатов скана
    def get_scan_results(self, deployment_id: str, scan_id: str):
        url = f"{self.base_url}/deployments/{deployment_id}/scans/{scan_id}"
        response = request.get(url, headers=self.headers)
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
