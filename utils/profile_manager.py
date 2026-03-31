import json
import os
import sys

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PROFILE_FILE = os.path.join(BASE_DIR, "profiles.json")


DEFAULT_DATA = {
    "active_profile": "Minecraft Tıklayıcı",
    "saved_key": "",
    "profiles": {
        "Minecraft Tıklayıcı": {
            "left": {
                "hotkey": "f8",
                "trigger": "left",
                "helper_key": "None",
                "sequence": [
                    {"type": "mouse", "action": "down", "target": "left"},
                    {"type": "delay", "ms": 30},
                    {"type": "mouse", "action": "up", "target": "left"},
                    {"type": "delay", "ms": 30}
                ]
            },
            "right": {
                "hotkey": "",
                "trigger": "right",
                "helper_key": "None",
                "sequence": []
            }
        }
    }
}

def migrate_old_data(data):
    if "profiles" not in data:
        return data
    
    for p_name, p_data in data["profiles"].items():
        if "trigger" in p_data or "left" not in p_data:
            old_trigger = p_data.get("trigger", "left")
            old_hk = p_data.get("hotkey", "f8")
            old_seq = p_data.get("sequence", [])
            
            data["profiles"][p_name] = {
                "left": {"hotkey": old_hk if old_trigger == "left" else "", "sequence": old_seq if old_trigger == "left" else []},
                "right": {"hotkey": old_hk if old_trigger == "right" else "", "sequence": old_seq if old_trigger == "right" else []}
            }
    
    if "saved_key" not in data:
        data["saved_key"] = ""
        
    return data

def load_data():
    if not os.path.exists(PROFILE_FILE):
        save_data(DEFAULT_DATA)
        return DEFAULT_DATA.copy()
    try:
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "profiles" not in data or "active_profile" not in data:
                return DEFAULT_DATA.copy()
                
            return migrate_old_data(data)
    except:
        return DEFAULT_DATA.copy()

def save_data(data):
    try:
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"KAYIT HATASI: {e}")
