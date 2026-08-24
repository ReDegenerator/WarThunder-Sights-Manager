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
            self.status_updated.emit(f"Подготовка к перегенерации выделенных прицелов ({len(self.target_sight_names)} шт.)...")
            sights_to_generate = [s for s in all_sights if s["file_name"] in self.target_sight_names]
        else:
            self.status_updated.emit("Авто-проверка отсутствующих превью-картинок...")
            sights_to_generate = [s for s in all_sights if not s.get("has_images", False)]
        
        total_tasks = len(sights_to_generate)
        self.progress_max_set.emit(total_tasks)
        
        if total_tasks == 0:
            self.status_updated.emit("Нет прицелов для обработки.")
            self.finished_success.emit(0)
            return

        generated_count = 0
        
        for idx, sight in enumerate(sights_to_generate):
            if not self.is_running:
                self.status_updated.emit("Процесс принудительно остановлен.")
                break
                
            blk_name = sight["file_name"]
            blk_path = sight["full_path"]
            
            self.status_updated.emit(f"Перерисовка векторной сетки: {blk_name}...")
            
            sight_name_no_ext = os.path.splitext(blk_name)[0].strip()
            output_png_path = os.path.join("data", "SightsImages", sight_name_no_ext, "preview.png")
            
            success, msg = parse_and_render_blk(blk_path, output_png_path)
            if success:
                generated_count += 1
            
        if self.is_running:
            self.status_updated.emit(f"Успешно обработано прицелов: {generated_count}")
            self.finished_success.emit(generated_count)