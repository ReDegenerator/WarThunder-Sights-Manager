from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal

class SightCard(QFrame):

    clicked = pyqtSignal(object, Qt.KeyboardModifier) 

    def __init__(self, sight_data, parent=None):
        super().__init__(parent)
        self.sight_data = sight_data
        self.is_selected = False
        
        self.setObjectName("SightCard")
        self.setProperty("selected", "false")
        self.setProperty("activated", "true" if sight_data.get("is_activated", False) else "false")
        

        self.setFixedHeight(32)
        
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(6)
        

        status_icon = "🟢 " if self.sight_data.get("is_activated", False) else "⚪ "
        self.name_label = QLabel(f"{status_icon}{self.sight_data['file_name']}")
        self.name_label.setStyleSheet("font-weight: 500; color: #E0E0E0; background: transparent; border: none; font-size: 12px;")
        layout.addWidget(self.name_label)

        
        if self.sight_data.get("has_images", False):
            self.img_icon = QLabel("pic")
            self.img_icon.setStyleSheet("background: transparent; border: none; font-size: 11px;")
            layout.addStretch()
            layout.addWidget(self.img_icon)
            
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def set_selection(self, selected):
        self.is_selected = selected
        self.setProperty("selected", "true" if selected else "false")
        
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self, event.modifiers())
        super().mousePressEvent(event)