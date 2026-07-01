import json
import os

CONFIG_FILE = "config.json"

DEFAULT_SETTINGS = {
    "cpu-max-temperature" : 85,
    "gpu-max-temperature" : 80,
    "cpu-max-usage" : 95,
    "gpu-max-usage" : 100,
    "ntfy-topic" : None,
    "widget-visible": False,
    "widget-x": 100,
    "widget-y": 100,
}

def load_settings():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE,"r",encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_SETTINGS
    else:
        save_settings(DEFAULT_SETTINGS)
    return DEFAULT_SETTINGS

def save_settings(settings):
    try:
        with open(CONFIG_FILE,"w",encoding="utf-8") as f:
            json.dump(settings,f,indent=4,)
            return True
    except Exception:
        return False

if __name__ == "__main__":
    current_settings = load_settings()
    print("Mevcut Ayarlar:",current_settings)


