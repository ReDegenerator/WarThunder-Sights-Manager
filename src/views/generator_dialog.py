from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
from src.models.generator_worker import GeneratorWorker

class GeneratorDialog(QDialog):
    def __init__(self, parent=None, target_sight_names=None):
        super().__init__(parent)
        self.main_window = parent
        self.setWindowTitle("Мастер генерации превью")
        self.setFixedSize(400, 150)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        self.init_ui()
        self.init_worker(target_sight_names=target_sight_names)

    def init_worker(self, target_sight_names=None):
        self.worker = GeneratorWorker(target_sight_names=target_sight_names)
        
        self.worker.progress_max_set.connect(self.progress_bar.setMaximum)
        self.worker.progress_changed.connect(self.progress_bar.setValue)
        self.worker.status_updated.connect(self.lbl_status.setText)
        self.worker.finished_success.connect(self.on_generation_finished)
        
        self.worker.start()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        self.lbl_status = QLabel("Подготовка к фоновой генерации картинок...")
        self.lbl_status.setStyleSheet("color: #BBBBBB; font-size: 11px;")
        self.lbl_status.setWordWrap(True)
        layout.addWidget(self.lbl_status)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar { background-color: #1E1E1E; border: 1px solid #2D2D2D; border-radius: 4px; text-align: center; color: #FFFFFF; font-weight: bold; }
            QProgressBar::chunk { background-color: #007ACC; border-radius: 3px; }
        """)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.setFixedSize(90, 28)
        self.btn_cancel.clicked.connect(self.on_cancel_clicked)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

    def on_cancel_clicked(self):
        self.worker.stop()
        self.worker.wait() 
        self.reject()

    def on_generation_finished(self, count):
        self.worker.wait()
        
        if count > 0:
            QMessageBox.information(self, "Успех", f"Генерация завершена!\nСоздано векторных превью: {count} шт.")
            if self.main_window and hasattr(self.main_window, 'refresh_all_apps_data'):
                self.main_window.refresh_all_apps_data()
        else:
            QMessageBox.information(self, "Информация", "Нет прицелов требующих генерации превью.")
            
        self.accept()

    def closeEvent(self, event):
        self.worker.stop()
        self.worker.wait()
        event.accept()