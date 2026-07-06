from django.db import connection
from django.contrib.auth import get_user_model
import requests
import os

def check_database():
    try:
        connection.ensure_connection()
        return True
    except:
        return False

def check_auth_system():
    try:
        User = get_user_model()
        User.objects.first()  # simple query
        return True
    except:
        return False

def check_api_service():
    try:
        response = requests.get("http://127.0.0.1:8000/api/chatbot/", timeout=2)
        return response.status_code == 200
    except:
        return False

def check_backup_system():
    try:
        path = "logs/"  # using logs as backup indicator
        return os.path.exists(path) and os.access(path, os.W_OK)
    except:
        return False

def get_system_health_status():
    return {
        "database": check_database(),
        "auth": check_auth_system(),
        "api": check_api_service(),
        "backup": check_backup_system()
    }
