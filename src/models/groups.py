import os
import json

GROUPS_CONFIG_DIR = os.path.join("data", "GroupsConfig")

def init_groups_folder():
    os.makedirs(GROUPS_CONFIG_DIR, exist_ok=True)

def load_all_groups_data():
    init_groups_folder()
    combined_config = {}
    
    if not os.path.exists(GROUPS_CONFIG_DIR):
        return combined_config
        
    for file_name in os.listdir(GROUPS_CONFIG_DIR):
        if file_name.lower().endswith('.json'):
            group_name = os.path.splitext(file_name)[0]
            full_path = os.path.join(GROUPS_CONFIG_DIR, file_name)
            
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    sights_list = json.load(f)
                    if isinstance(sights_list, list):
                        combined_config[group_name] = sights_list
            except Exception as e:
                print(f"Error reading group config {file_name}: {e}")
                
    return combined_config

def save_single_group_config(group_name, sights_list):
    init_groups_folder()
    file_path = os.path.join(GROUPS_CONFIG_DIR, f"{group_name}.json")
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(sights_list, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"Error saving group file {group_name}.json: {e}")
        return False

def get_all_groups():
    config = load_all_groups_data()
    groups_list = []
    for group_name in config.keys():
        groups_list.append({
            "group_name": group_name
        })
    return groups_list

def create_new_group(group_name):
    group_name = group_name.strip()
    if not group_name:
        return False, "Group name cannot be empty!"
        

    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        group_name = group_name.replace(char, '')
        
    init_groups_folder()
    file_path = os.path.join(GROUPS_CONFIG_DIR, f"{group_name}.json")
    
    if os.path.exists(file_path):
        return False, "A group with this name already exists!"
        
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        return True, f"Group file '{group_name}.json' created successfully!"
    except Exception as e:
        return False, f"Failed to create group file: {e}"
    
def rename_group_file(old_name, new_name):
    new_name = new_name.strip()
    if not new_name or old_name == new_name:
        return False, "Invalid or identical name."
        
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        new_name = new_name.replace(char, '')
        
    old_path = os.path.join(GROUPS_CONFIG_DIR, f"{old_name}.json")
    new_path = os.path.join(GROUPS_CONFIG_DIR, f"{new_name}.json")
    
    if os.path.exists(new_path):
        return False, "A group with this name already exists!"
        
    try:
        if os.path.exists(old_path):
            os.rename(old_path, new_path)
            return True, f"Group renamed to '{new_name}'"
    except Exception as e:
        print(f"Error renaming file: {e}")
        
    return False, "Failed to rename file."