import os
import shutil

def create_sight_symlink(sight_file_name, repository_path, game_usersights_path):
    if not game_usersights_path or not os.path.exists(game_usersights_path):
        return False, "Invalid game directory path."
        
    game_file_path = os.path.join(game_usersights_path, sight_file_name)
    source_file_path = os.path.abspath(repository_path)
    
    if os.path.exists(game_file_path) or os.path.islink(game_file_path):
        try:
            os.remove(game_file_path)
        except Exception as e:
            return False, f"Failed to clear old file in game folder: {e}"
            
    try:
        os.symlink(source_file_path, game_file_path)
        return True, f"🚀 Symlink created for {sight_file_name}"
    except OSError as e:
        try:
            shutil.copy2(source_file_path, game_file_path)
            return True, f"📋 Copied (Fallback) {sight_file_name}"
        except Exception as copy_err:
            return False, f"Windows blocked link creation: {e}. Copy failed: {copy_err}"

def remove_sight_link_from_game(sight_name, game_path):
    try:
        target_path = os.path.join(game_path, sight_name)
        if os.path.exists(target_path) or os.path.islink(target_path):
            os.remove(target_path) 
            return True
    except Exception as e:
        print(f"Ошибка при удалении симлинка {sight_name}: {e}")
    return False