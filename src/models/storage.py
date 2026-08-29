import os
import sys
import json
import shutil
from PyQt6.QtWidgets import QFileDialog

if hasattr(sys, 'frozen'):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = os.path.join(BASE_DIR, "data")
REPOSITORY_DIR = os.path.join(DATA_DIR, "UserSights")
IMAGES_DIR = os.path.join(DATA_DIR, "SightsImages")
CACHE_FILE = os.path.join(DATA_DIR, "sights_cache.json")

def init_app_folders():
    os.makedirs(REPOSITORY_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)

def rebuild_sights_cache():
    if not os.path.exists(REPOSITORY_DIR):
        return

    from src.models.groups import load_all_groups_data
    all_groups_data = load_all_groups_data()
    
    sights_in_groups = []
    for g_name, g_list in all_groups_data.items():
        sights_in_groups.extend(g_list)

    cache_data = []

    for sight in os.listdir(REPOSITORY_DIR):
        if sight.lower().endswith('.blk'):
            sight_name_no_ext = os.path.splitext(sight)[0].strip()
            
            images_path = os.path.join(IMAGES_DIR, sight_name_no_ext)
            
            has_images = False
            if os.path.exists(images_path) and os.path.isdir(images_path):
                valid_exts = ('.png', '.jpg', '.jpeg')
                try:
                    images_in_dir = [f for f in os.listdir(images_path) if f.lower().endswith(valid_exts)]
                    if images_in_dir:
                        has_images = True
                except:
                    has_images = False

            in_group = sight in sights_in_groups

            cache_data.append({
                "file_name": sight,
                "full_path": os.path.abspath(os.path.join(REPOSITORY_DIR, sight)),
                "has_images": has_images,
                "in_group": in_group,
                "is_activated": False 
            })

    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=4)
        print(f"The cache has been successfully updated! {len(cache_data)} sights have been recorded.")
    except Exception as e:
        print(f"Critical error writing cache file: {e}")

def get_all_sights(force_refresh=False):

    if force_refresh or not os.path.exists(CACHE_FILE):
        return rebuild_sights_cache()
        
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Cache read error, we’ll rebuild it: {e}")
        return rebuild_sights_cache()

def import_sights_files(parent_window):

    files, _ = QFileDialog.getOpenFileNames(
        parent_window, "Import Custom Sights", "", "War Thunder Sights (*.blk)"
    )
    if files:
        init_app_folders()
        imported_count = 0
        for src_path in files:
            file_name = os.path.basename(src_path)
            dest_path = os.path.join(REPOSITORY_DIR, file_name)
            try:
                shutil.copy2(src_path, dest_path)
                imported_count += 1
            except Exception as e:
                print(f"Error importing {file_name}: {e}")
        
        rebuild_sights_cache()
        return imported_count
    return 0