import json
from datetime import datetime, timedelta
import os

# Шлях до файлу
ACCESS_FILE = "data/user_access.json"

# Завантажити всі доступи
def load_access_data():
    if not os.path.exists(ACCESS_FILE):
        return {}
    with open(ACCESS_FILE, "r") as f:
        return json.load(f)

# Зберегти
def save_access_data(data):
    with open(ACCESS_FILE, "w") as f:
        json.dump(data, f)

# Перевірка чи є активний доступ
def has_access(user_id: int) -> bool:
    data = load_access_data()
    uid = str(user_id)
    if uid not in data:
        # перший вхід — зберігаємо час старту
        data[uid] = {"start": datetime.now().isoformat()}
        save_access_data(data)
        return True
    start_time = datetime.fromisoformat(data[uid]["start"])
    return datetime.now() - start_time < timedelta(hours=24)

def is_premium(user_id: int) -> bool:
    data = load_access_data()
    uid = str(user_id)
    if uid not in data or "premium_until" not in data[uid]:
        return False
    until = datetime.fromisoformat(data[uid]["premium_until"])
    return datetime.now() < until

def grant_premium(user_id: int, days: int):
    data = load_access_data()
    uid = str(user_id)
    now = datetime.now()
    until = now + timedelta(days=days)
    if uid not in data:
        data[uid] = {"start": now.isoformat()}
    data[uid]["premium_until"] = until.isoformat()
    save_access_data(data)