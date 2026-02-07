# utils.py
import os, json, datetime

SAVED_DIR = "saved_pdfs"
HISTORY_FILE = os.path.join(SAVED_DIR, "history.json")

os.makedirs(SAVED_DIR, exist_ok=True)

if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)

def save_history(filename, action):
    entry = {
        "filename": filename,
        "action": action,
        "timestamp": datetime.datetime.now().isoformat()
    }
    with open(HISTORY_FILE, "r+") as f:
        data = json.load(f)
        data.insert(0, entry)
        f.seek(0); f.truncate()
        json.dump(data, f, indent=2)

def read_history():
    with open(HISTORY_FILE) as f:
        return json.load(f)

def save_pdf(data, name):
    path = os.path.join(SAVED_DIR, name)
    with open(path, "wb") as f:
        f.write(data)
    return path
