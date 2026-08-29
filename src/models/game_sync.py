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
        print(f"Error deleting the symlink {sight_name}: {e}")
    return False

def migrate_existing_sights_from_game(game_path, target_repo_dir):
    if not game_path or not os.path.exists(game_path):
        return 0

    from src.models.game_sync import create_sight_symlink
    migrated_count = 0

    try:
        for file_name in os.listdir(game_path):
            if file_name.lower().endswith('.blk'):
                file_in_game = os.path.join(game_path, file_name)
                
                if not os.path.islink(file_in_game):
                    dest_repo_path = os.path.join(target_repo_dir, file_name)
                    
                    if not os.path.exists(dest_repo_path):
                        shutil.move(file_in_game, dest_repo_path)
                    else:
                        try: os.remove(file_in_game)
                        except: pass
                        
                    create_sight_symlink(file_name, os.path.abspath(dest_repo_path), game_path)
                    migrated_count += 1
                    
    except Exception as e:
        print(f"Error during the migration of sights from the game: {e}")

    return migrated_count