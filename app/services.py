from flask import current_app
from .models import db, scan, vulnerability, user
from semgrep_api_client import SemgrepAPIClient
import datetime
import sys
import os

# добавляет корневую папку в путь для импорта semgrep_api
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class SemgrepService:
    def __init__(self):
        token = current_app.config("SEMGREP_API_TOKEN")
        if not token:
            raise ValueError("API Токен не загружен")
        self.client = SemgrepAPIClient(
            api_token=token
        )  # загрузка токена при инициализации

# отправка кода на скан
def run_code_scan(self, code):
    payload = {
        "policy": "r2c-ci",
        "source": {"type": "inline",
                   "files": {"input_file": code}}
    }
    scan_id = self._create_scan(payload)
    self._wait_for_completion(scan_id)
    return self._fetch_results(scan_id)

#отправка репозитория на скан
def run_repo_scan(self, repo_url):
    payload = {
        'policy': 'r2c-ci',
        'source': {'type': 'git',
                    'url': repo_url}
    }
    scan_id = self.create.scan(payload)
    return self._fetch_results(scan_id)

# создание задачи на сканирование
def _create_scan(self, payload: dict) -> str:
    response = self.clients.scan.create_scans(payload)
    scan_id = response.get('scan', {}).get('id')
    if not scan_id:
        raise RuntimeError('scan_id не получен')
    return scan_id

# получение результатов сканирования
def _get_results(self, scan_id: str) -> dict:
    if not scan_id:
        raise ValueError('scan_id пуст')
    while True:
        scan_status = self.clients.scans.get_scan_status(scan_id)
        if scan_status == 'succeed':
            break
        elif scan_status == 'failed':
            raise RuntimeError('Ошибка сканирования')
        else:
            datetime.time.sleep(2)
    results = self.clients.scans.get_scan_results(scan_id)
    return results

def run_scanner_service():
    return SemgrepService()
