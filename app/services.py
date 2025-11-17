from flask import current_app
from .models import db, scan, vulnerability, user
from semgrep_api_client import SemgrepAPIClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
