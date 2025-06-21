import json
import os
from datetime import datetime

HISTORY_PATH = "data/signal_history.json"

def load_history():
    if not os.path.exists(HISTORY_PATH):
        return {}
    with open(HISTORY_PATH, "r") as f:
        return json.load(f)

def save_history(data):
    with open(HISTORY_PATH, "w") as f:
        json.dump(data, f, indent=2)

def add_signal_to_history(user_id, signal_text, image_path=None):
    data = load_history()
    uid = str(user_id)
    if uid not in data:
        data[uid] = []
    data[uid].append({
        "text": signal_text,
        "image": image_path,
        "timestamp": datetime.now().isoformat()
    })
    # обмежити до останніх 10
    data[uid] = data[uid][-10:]
    save_history(data)

def get_user_history(user_id):
    data = load_history()
    return data.get(str(user_id), [])