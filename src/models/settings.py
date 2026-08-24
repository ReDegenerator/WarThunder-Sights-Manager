import os
import json
from PyQt6.QtWidgets import QFileDialog

CONFIG_FILE = os.path.join("data", "app_settings.json")

def load_settings():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("game_path", "")
        except Exception as e:
            print(f"Error loading config: {e}")
    return ""

def save_settings(game_path):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"game_path": game_path}, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving config: {e}")

def choose_game_directory(parent_window):
    dir_path = QFileDialog.getExistingDirectory(
        parent_window, 
        "Select War Thunder Sights Directory (UserSights)", 
        os.path.expanduser("~") 
    )
    
    if dir_path:
        dir_path = os.path.normpath(dir_path)
        save_settings(dir_path)
        return dir_path
        
    return None