from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QWidget, QListWidget, QListWidgetItem
from PyQt6.QtCore import Qt, pyqtSignal

from src.models.storage import get_all_sights
from src.models.groups import load_all_groups_data


class GroupCard(QFrame):
    edit_requested = pyqtSignal(str)   
    delete_requested = pyqtSignal(str) 
    expanded_toggled = pyqtSignal(str, bool)

    def __init__(self, group_name, sights_list, parent=None):
        super().__init__(parent)
        self.group_name = group_name
        self.sights_list = sights_list 
        self.is_expanded = False       
        self.main_window = parent 
        
        self.setObjectName("SightCard") 
        self.setFrameShape(QFrame.Shape.StyledPanel)
        
        self.setMinimumHeight(65)
        self.setMaximumHeight(65)
        
        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 12, 12, 12)
        self.main_layout.setSpacing(8)
        
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        self.btn_toggle = QPushButton("[ + ]") 
        self.btn_toggle.setFixedSize(45, 28)
        self.btn_toggle.setStyleSheet("background: #252525; border: 1px solid #3d3d3d; border-radius: 4px; font-size: 11px; color: #007ACC; font-weight: bold;")
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.clicked.connect(self.toggle_expand)
        header_layout.addWidget(self.btn_toggle)
        
        self.title_label = QLabel(f"  {self.group_name} ({len(self.sights_list)} sights)")
        self.title_label.setStyleSheet("font-weight: bold; color: #FFFFFF; font-size: 13px; background: transparent; border: none;")
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        btn_edit = QPushButton("✏️ Edit")
        btn_edit.setStyleSheet("padding: 4px 12px; font-size: 11px;")
        btn_edit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_edit.clicked.connect(lambda: self.edit_requested.emit(self.group_name))
        header_layout.addWidget(btn_edit)
        
        btn_delete = QPushButton("🗑")
        btn_delete.setStyleSheet("background-color: #c0392b; padding: 4px 10px; font-size: 11px; border: none;")
        btn_delete.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_delete.clicked.connect(lambda: self.delete_requested.emit(self.group_name))
        header_layout.addWidget(btn_delete)
        
        self.main_layout.addWidget(header_widget)
        
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget { background-color: #161616; border: 1px solid #252525; border-radius: 4px; }
            QListWidget::item { color: #BBBBBB; padding: 6px; border-bottom: 1px solid #1A1A1A; }
            QListWidget::item:selected { background-color: #0c3c5d; color: #FFFFFF; }
        """)
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        
        from src.models.storage import get_all_sights
        sights_cache = get_all_sights()
        
        if self.sights_list:
            main_win = self.main_window
            sights_cache_memory = getattr(main_win, 'sights_cache_memory', []) if main_win else sights_cache
            
            for sight_name in self.sights_list:
                sight_data = next((s for s in sights_cache_memory if s["file_name"] == sight_name), None)
                
                icon = "🟢 " if sight_data and sight_data.get("is_activated", False) else "📄 "
                img_marker = "  [🖼️]" if sight_data and sight_data.get("has_images", False) else ""
                
                item = QListWidgetItem(f"{icon} {sight_name}{img_marker}")
                item.setData(Qt.ItemDataRole.UserRole, sight_name)
                self.list_widget.addItem(item)
        else:
            item = QListWidgetItem("No sights in this group yet.")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.list_widget.addItem(item)
            
        self.main_layout.addWidget(self.list_widget)
        self.list_widget.hide()

    def toggle_expand(self):
        self.is_expanded = not self.is_expanded
        if self.is_expanded:
            self.btn_toggle.setText("[ - ]")
            self.setMinimumHeight(450)
            self.setMaximumHeight(450)
            
            self.list_widget.show()
        else:
            self.btn_toggle.setText("[ + ]")
            self.list_widget.clearSelection()
            
            self.setMinimumHeight(65)
            self.setMaximumHeight(65)
            
            self.list_widget.hide()
            
            root = self.parent()
            while root and root.__class__.__name__ != "MainWindow":
                root = root.parent()
            if root and hasattr(root, 'edit_preview_list'):
                root.edit_preview_list.clear()
            
        self.expanded_toggled.emit(self.group_name, self.is_expanded)

    def on_selection_changed(self):
        root = self.parent()
        while root and root.__class__.__name__ != "MainWindow":
            root = root.parent()
            
        if not root: return
        
        if hasattr(root, 'edit_preview_list') and hasattr(root, 'render_gallery_waterfall'):
            root.render_gallery_waterfall(self.list_widget, root.edit_preview_list)
            
        if hasattr(root, 'update_gallery_on_group_click'):
            root.update_gallery_on_group_click(self)