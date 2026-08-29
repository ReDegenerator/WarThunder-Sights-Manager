import os
from PyQt6.QtCore import QThread, pyqtSignal
from src.models.storage import get_all_sights
from src.models.sight_renderer import parse_and_render_blk

class GeneratorWorker(QThread):
    progress_changed = pyqtSignal(int)      
    progress_max_set = pyqtSignal(int)     
    status_updated = pyqtSignal(str)       
    finished_success = pyqtSignal(int)     

    def __init__(self, target_sight_names=None):
        super().__init__()
        self.is_running = True
        self.target_sight_names = target_sight_names 

    def stop(self):
        self.is_running = False

    def run(self):
        all_sights = get_all_sights()
        
        if self.target_sight_names is not None:
            self.status_updated.emit(f"Preparation for the regeneration of allocated sights ({len(self.target_sight_names)})...")
            sights_to_generate = [s for s in all_sights if s["file_name"] in self.target_sight_names]
        else:
            self.status_updated.emit("Auto‑check for missing image previews...")
            sights_to_generate = [s for s in all_sights if not s.get("has_images", False)]
        
        total_tasks = len(sights_to_generate)
        self.progress_max_set.emit(total_tasks)
        
        if total_tasks == 0:
            self.status_updated.emit("There are no sights for processing.")
            self.finished_success.emit(0)
            return

        generated_count = 0
        
        for idx, sight in enumerate(sights_to_generate):
            if not self.is_running:
                self.status_updated.emit("The process has been forcibly stopped.")
                break
                
            blk_name = sight["file_name"]
            blk_path = sight["full_path"]
            
            self.status_updated.emit(f"Перерисовка векторной сетки: {blk_name}...")
            
            sight_name_no_ext = os.path.splitext(blk_name)[0].strip()
            
            from src.models.storage import IMAGES_DIR
            output_dir_path = os.path.join(IMAGES_DIR, sight_name_no_ext)
            
            success, msg = parse_and_render_blk(blk_path, output_dir_path)
            if success:
                generated_count += 1
            
        if self.is_running:
            self.status_updated.emit(f"The sights have been successfully processed: {generated_count}")
            self.finished_success.emit(generated_count)