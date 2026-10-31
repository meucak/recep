import json
import os
import tempfile

CONFIG_DIR = os.path.expanduser("~/.config/cs-bomb")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "code": "316931",
    "duration": 30,
    "max_attempts": 3,
    "url": "https://www.google.com"
}

def load_config():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return dict(DEFAULT_CONFIG)
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure all keys exist
            for k, v in DEFAULT_CONFIG.items():
                if k not in data:
                    data[k] = v
            return data
    except Exception as e:
        print(f"Error loading config: {e}, using defaults.")
        return dict(DEFAULT_CONFIG)

def save_config(data):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    try:
        # Atomic write
        temp_fd, temp_path = tempfile.mkstemp(dir=CONFIG_DIR, prefix="cfg_", suffix=".tmp")
        with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        os.replace(temp_path, CONFIG_PATH)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

if __name__ == "__main__":
    cfg = load_config()
    print("Loaded config:", cfg)