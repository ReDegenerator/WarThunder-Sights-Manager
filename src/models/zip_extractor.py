import os
import zipfile
import shutil

def process_dropped_files(file_paths, target_repo_dir):
    copied_count = 0
    
    for path in file_paths:
        if not os.path.exists(path):
            continue
            
        if path.lower().endswith('.blk'):
            file_name = os.path.basename(path)
            dest_path = os.path.join(target_repo_dir, file_name)
            try:
                shutil.copy2(path, dest_path)
                copied_count += 1
            except Exception as e:
                print(f"Blk copy error {file_name}: {e}")
                
        elif path.lower().endswith('.zip'):
            try:
                with zipfile.ZipFile(path, 'r') as zip_ref:
                    for zip_info in zip_ref.infolist():
                        if not zip_info.is_dir() and zip_info.filename.lower().endswith('.blk'):
                            base_name = os.path.basename(zip_info.filename)
                            if not base_name: 
                                continue
                                
                            dest_path = os.path.join(target_repo_dir, base_name)
                            
                            with zip_ref.open(zip_info) as source_file, open(dest_path, 'wb') as target_file:
                                shutil.copyfileobj(source_file, target_file)
                            copied_count += 1
            except Exception as e:
                print(f"ZIP archive parsing error {os.path.basename(path)}: {e}")
                
    return copied_count