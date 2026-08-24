import os
from PyQt6.QtWidgets import QMainWindow, QListWidget, QListWidgetItem, QMessageBox, QInputDialog, QFrame, QVBoxLayout, QLabel, QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap
from PyQt6 import uic

from src.models.settings import load_settings, choose_game_directory
from src.models.storage import init_app_folders, get_all_sights, rebuild_sights_cache
from src.models.groups import init_groups_folder, create_new_group
from src.views.group_card import GroupCard

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        init_app_folders()
        init_groups_folder()
        
        ui_path = os.path.join("src", "views", "assets", "MainWindow.ui")
        uic.loadUi(ui_path, self)
        
        game_path = load_settings()
        if hasattr(self, 'input_game_path') and game_path:
            self.input_game_path.setText(str(game_path))
            
        self.init_signals()
        self.setup_list_widgets()
        self.refresh_all_apps_data()
        
        if hasattr(self, 'widget_edit_panel'):
            self.widget_edit_panel.hide()

        self.run_silent_auto_generation()

    def run_silent_auto_generation(self):

        from src.models.generator_worker import GeneratorWorker
        

        self.auto_generator_worker = GeneratorWorker()
        
        self.auto_generator_worker.finished_success.connect(self.on_auto_generation_finished)
        
        self.auto_generator_worker.start()

    def on_auto_generation_finished(self, count):

        if hasattr(self, 'auto_generator_worker'):
            self.auto_generator_worker.wait()
            
        if count > 0:
            print(f"[АВТО-ГЕНЕРАТОР]: Успешно создано {count} новых превью-картинок для прицелов!")
            self.refresh_all_apps_data()

    def setup_list_widgets(self):
        if hasattr(self, 'repo_list'):
            self.repo_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
            self.repo_list.itemSelectionChanged.connect(self.on_repo_selection_changed)
            self.repo_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        if hasattr(self, 'active_list'):
            self.active_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
            self.active_list.itemSelectionChanged.connect(self.on_active_selection_changed)
            self.active_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        for name in ['repo_preview_list', 'active_preview_list', 'edit_preview_list', 'groups_preview_list']:
            if hasattr(self, name):
                widget = getattr(self, name)
                widget.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
                widget.verticalScrollBar().setSingleStep(15)

    def init_signals(self):
        if hasattr(self, 'btn_browse_path'): self.btn_browse_path.clicked.connect(self.on_browse_clicked)
        if hasattr(self, 'btn_refresh'): self.btn_refresh.clicked.connect(self.refresh_all_apps_data)
        if hasattr(self, 'input_search'): self.input_search.textChanged.connect(self.filter_repository)
        if hasattr(self, 'check_hide_grouped'): self.check_hide_grouped.stateChanged.connect(self.filter_repository)
        if hasattr(self, 'btn_select_all'): self.btn_select_all.clicked.connect(self.select_all_sights)
        if hasattr(self, 'btn_clear_select'): self.btn_clear_select.clicked.connect(self.clear_sights_selection)
        if hasattr(self, 'btn_activate'): self.btn_activate.clicked.connect(self.activate_selected_sights)
        if hasattr(self, 'btn_delete'): self.btn_delete.clicked.connect(self.delete_selected_sights)
        if hasattr(self, 'btn_group_create_new'): self.btn_group_create_new.clicked.connect(self.on_create_group_clicked)
        if hasattr(self, 'btn_deactivate'): self.btn_deactivate.clicked.connect(self.deactivate_selected_sights)
        if hasattr(self, 'btn_rebuild_selected_previews'): self.btn_rebuild_selected_previews.clicked.connect(self.on_rebuild_selected_previews_clicked)

        connected = False
        if hasattr(self, 'input_search_in_groups'):
            self.input_search_in_groups.textChanged.connect(self.filter_groups_by_global_search)
            connected = True
            print("Сигнал input_search_in_groups успешно привязан по имени объекта!")
            
        if not connected:
            from PyQt6.QtWidgets import QLineEdit
            all_inputs = self.findChildren(QLineEdit)
            for inp in all_inputs:
                inp_name = inp.objectName().lower()
                if "group" in inp_name and "edit" not in inp_name:
                    inp.textChanged.connect(self.filter_groups_by_global_search)
                    self.input_search_in_groups = inp
                    connected = True
                    print(f"Сигнал глобального поиска принудительно привязан к виджету: '{inp.objectName()}'")
                    break
                    
        if not connected:
            print("Предупреждение: Текстовое поле глобального поиска групп не найдено на форме MainWindow.ui!")

    def on_browse_clicked(self):
        new_path = choose_game_directory(self)
        if new_path: self.input_game_path.setText(new_path)

    def refresh_all_apps_data(self):
        print("Полная синхронизация...")
        rebuild_sights_cache()
        
        self.sights_cache_memory = get_all_sights()
        
        if hasattr(self, 'label_total_sights_counter'):
            self.label_total_sights_counter.setText(f"Total Sights inside Repository: {len(self.sights_cache_memory)}")
            
        self.refresh_repository_ui()
        self.refresh_groups_ui()
        self.refresh_activated_ui()
        if hasattr(self, 'widget_edit_panel') and self.widget_edit_panel.isVisible():
            self.refresh_edit_dialog_ui()
        print("Все разделы синхронизированы!")

    def refresh_repository_ui(self):
        if not hasattr(self, 'repo_list'): return
        self.repo_list.clear()
        
        game_path = self.input_game_path.text().strip() if hasattr(self, 'input_game_path') else ""
        
        try:
            active_files_in_game = [f for f in os.listdir(game_path) if f.lower().endswith('.blk')] if (game_path and os.path.exists(game_path)) else []
        except:
            active_files_in_game = []
            
        sights_data = getattr(self, 'sights_cache_memory', [])
        
        for sight in sights_data:
            name = sight["file_name"]
            
            if name in active_files_in_game:
                sight["is_activated"] = True
                icon = "🟢 "
            else:
                sight["is_activated"] = False
                icon = "📄 "
                
            img_marker = "  [🖼️]" if sight.get("has_images", False) else ""
            item = QListWidgetItem(f"{icon}{name}{img_marker}")
            item.setData(Qt.ItemDataRole.UserRole, name)
            self.repo_list.addItem(item)

    def refresh_groups_ui(self):
        target_list = getattr(self, 'groups_list', None)
        if target_list is None or target_list.__class__.__name__ != "QListWidget":
            for l in self.findChildren(QListWidget):
                if l.objectName() not in ["repo_list", "active_list", "left_list_widget", "right_list_widget", "repo_preview_list", "active_preview_list", "edit_preview_list", "groups_preview_list"]:
                    target_list = l
                    break
        if target_list is None: return
        target_list.clear()
        
        from src.models.groups import load_all_groups_data
        from src.views.group_card import GroupCard
        all_groups = load_all_groups_data()
        for group_name, sights_list in all_groups.items():
            card = GroupCard(group_name, sights_list, self)
            card.edit_requested.connect(self.on_edit_group_clicked)
            card.delete_requested.connect(self.on_delete_group_clicked)
            card.expanded_toggled.connect(self.on_group_expanded_toggled)
            
            item = QListWidgetItem(target_list)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            from PyQt6.QtCore import QSize
            item.setSizeHint(QSize(target_list.width(), 75)) 
            target_list.addItem(item)
            target_list.setItemWidget(item, card)

    def update_gallery_on_group_click(self, active_card):
        if hasattr(self, 'widget_edit_panel') and self.widget_edit_panel.isVisible():
            return
            
        all_lists = self.findChildren(QListWidget)
        for l in all_lists:
            if l.objectName() not in ["repo_list", "active_list", "left_list_widget", "right_list_widget", "repo_preview_list", "active_preview_list", "edit_preview_list"]:
                for i in range(l.count()):
                    item = l.item(i)
                    card = l.itemWidget(item)
                    if card and card != active_card and hasattr(card, 'list_widget'):
                        card.list_widget.blockSignals(True)
                        card.list_widget.clearSelection()
                        card.list_widget.blockSignals(False)
                break
            
    def on_group_expanded_toggled(self, group_name, is_expanded):
        from PyQt6.QtCore import QSize
        for l in self.findChildren(QListWidget):
            if l.objectName() not in ["repo_list", "active_list", "left_list_widget", "right_list_widget", "repo_preview_list", "active_preview_list", "edit_preview_list", "groups_preview_list"]:
                for i in range(l.count()):
                    item = l.item(i)
                    card = l.itemWidget(item)
                    if card and getattr(card, 'group_name', '') == group_name:
                        target_height = 460 if is_expanded else 75
                        item.setSizeHint(QSize(l.width(), target_height))
                        break
                l.doItemsLayout()
                l.update()
                break

    def refresh_activated_ui(self):
        if not hasattr(self, 'active_list'): return
        self.active_list.clear()
        
        game_path = self.input_game_path.text().strip() if hasattr(self, 'input_game_path') else ""
        if not game_path or not os.path.exists(game_path): return
            
        try: active_files_in_game = [f for f in os.listdir(game_path) if f.lower().endswith('.blk')]
        except: active_files_in_game = []
            
        sights_data = getattr(self, 'sights_cache_memory', [])
        for sight in sights_data:
            name = sight["file_name"]
            if name in active_files_in_game:
                sight["is_activated"] = True
                img_marker = "  [🖼️]" if sight.get("has_images", False) else ""
                item = QListWidgetItem(f"🟢 {name}{img_marker}")
                item.setData(Qt.ItemDataRole.UserRole, name)
                self.active_list.addItem(item)
            else:
                sight["is_activated"] = False
    
    def on_repo_selection_changed(self):
        if hasattr(self, 'repo_list') and hasattr(self, 'repo_preview_list'):
            self.render_gallery_waterfall(self.repo_list, self.repo_preview_list)

    def on_active_selection_changed(self):
        if hasattr(self, 'active_list') and hasattr(self, 'active_preview_list'):
            self.render_gallery_waterfall(self.active_list, self.active_preview_list)

    def on_edit_left_selection_changed(self):
        if getattr(self, '_shifter_block', False): return
        if hasattr(self, 'left_list_widget') and self.left_list_widget.selectedItems():
            self._shifter_block = True
            self.right_list_widget.clearSelection()
            self._shifter_block = False
            self.render_gallery_waterfall(self.left_list_widget, self.edit_preview_list)

    def on_edit_right_selection_changed(self):
        if getattr(self, '_shifter_block', False): return
        if hasattr(self, 'right_list_widget') and self.right_list_widget.selectedItems():
            self._shifter_block = True
            self.left_list_widget.clearSelection()
            self._shifter_block = False
            self.render_gallery_waterfall(self.right_list_widget, self.edit_preview_list)


    def render_gallery_waterfall(self, source_list_widget, target_preview_list):
        target_preview_list.clear()
        
        sight_names_to_render = []

        if source_list_widget and hasattr(source_list_widget, 'selectedItems'):
            selected_items = source_list_widget.selectedItems()
            for item in selected_items:
                name = item.data(Qt.ItemDataRole.UserRole)
                if name:
                    sight_names_to_render.append(name)
                    
        if not sight_names_to_render: 
            return
            
        sights_cache = getattr(self, 'sights_cache_memory', [])
        
        for sight_name in sight_names_to_render:
            sight_data = next((s for s in sights_cache if s["file_name"] == sight_name), None)
            if not sight_data: continue
            
            sight_box = QFrame()
            sight_box.setStyleSheet("QFrame { background-color: #1A1A1A; border: 1px solid #2D2D2D; border-radius: 6px; }")
            
            box_layout = QVBoxLayout(sight_box)
            box_layout.setContentsMargins(10, 15, 10, 15)
            box_layout.setSpacing(12)
            
            title_lbl = QLabel(f"📄 {sight_data['file_name']}")
            title_lbl.setStyleSheet("font-weight: bold; color: #007ACC; font-size: 11px; border: none; background: transparent;")
            box_layout.addWidget(title_lbl)
            
            has_images = False
            has_images = False
            if sight_data.get("has_images", False):
                sight_name_no_ext = os.path.splitext(sight_name)[0].strip()
                images_dir = os.path.join("data", "SightsImages", sight_name_no_ext)
                
                if os.path.exists(images_dir) and os.path.isdir(images_dir):
                    valid_exts = ('.png', '.jpg', '.jpeg')
                    img_files = [f for f in os.listdir(images_dir) if f.lower().endswith(valid_exts)]
                    img_files.sort()
                    for f in img_files:
                        img_path = os.path.join(images_dir, f)
                        img_label = QLabel()
                        img_label.setStyleSheet("background: transparent; border: none; border-radius: 4px;")
                        pixmap = QPixmap(img_path)
                        if pixmap.isNull(): continue
                        
                        target_width = 260
                        scaled = pixmap.scaledToWidth(target_width, Qt.TransformationMode.SmoothTransformation)
                        img_label.setPixmap(scaled)
                        img_label.setFixedSize(target_width, scaled.height())
                        box_layout.addWidget(img_label)
                        has_images = True
            if not has_images:
                no_img = QLabel("No preview images for this sight.")
                no_img.setStyleSheet("color: #555555; font-style: italic; border: none; background: transparent;")
                box_layout.addWidget(no_img)
            
            
            sight_box.setFixedWidth(280)
            sight_box.adjustSize()
            
            container_widget = QWidget()
            container_layout = QHBoxLayout(container_widget)
            container_layout.setContentsMargins(0, 10, 0, 10)
            container_layout.setSpacing(0)
            
            container_layout.addWidget(sight_box, alignment=Qt.AlignmentFlag.AlignTop)
            container_layout.addStretch()
            
            container_widget.adjustSize()
            
            gallery_item = QListWidgetItem(target_preview_list)
            gallery_item.setSizeHint(container_widget.sizeHint())
            gallery_item.setFlags(gallery_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            
            target_preview_list.addItem(gallery_item)
            target_preview_list.setItemWidget(gallery_item, container_widget)


    def select_all_sights(self):
        if hasattr(self, 'repo_list'): self.repo_list.selectAll()

    def clear_sights_selection(self):
        if hasattr(self, 'repo_list'): self.repo_list.clearSelection()

    def filter_repository(self):
        if not hasattr(self, 'repo_list'): return
        search_text = self.input_search.text().lower().strip() if hasattr(self, 'input_search') else ""
        hide_grouped = self.check_hide_grouped.isChecked() if hasattr(self, 'check_hide_grouped') else False
        
        sights_data = getattr(self, 'sights_cache_memory', [])
        for i in range(self.repo_list.count()):
            item = self.repo_list.item(i)
            sight_name = item.data(Qt.ItemDataRole.UserRole)
            sight = next((s for s in sights_data if s["file_name"] == sight_name), {"in_group": False})
            matches_search = search_text in sight_name.lower()
            passes_group_filter = not (hide_grouped and sight["in_group"])
            item.setHidden(not (matches_search and passes_group_filter))

    def filter_groups_by_global_search(self):
        search_text = self.input_search_in_groups.text().lower().strip() if hasattr(self, 'input_search_in_groups') else ""
        
        all_lists = self.findChildren(QListWidget)
        target_list = None
        for l in all_lists:
            if l.objectName() not in ["repo_list", "active_list", "left_list_widget", "right_list_widget", "repo_preview_list", "active_preview_list", "edit_preview_list", "groups_preview_list"]:
                target_list = l
                break
                
        if not target_list: return

        from src.models.groups import load_all_groups_data
        all_groups_data = load_all_groups_data()

        for i in range(target_list.count()):
            item = target_list.item(i)
            card = target_list.itemWidget(item)
            
            if card and hasattr(card, 'group_name'):
                g_name = card.group_name
                sights_in_group = all_groups_data.get(g_name, [])
                
                if not search_text:
                    item.setHidden(False)
                    if hasattr(card, 'list_widget'):
                        for row in range(card.list_widget.count()):
                            card.list_widget.item(row).setHidden(False)
                    continue
                
                group_matches = any(search_text in sight_file.lower() for sight_file in sights_in_group)
                item.setHidden(not group_matches)
                
                item.setHidden(not group_matches)
                
                if group_matches and hasattr(card, 'list_widget'):
                    for row in range(card.list_widget.count()):
                        inner_item = card.list_widget.item(row)
                        inner_sight_name = inner_item.data(Qt.ItemDataRole.UserRole)
                        if inner_sight_name:
                            inner_item.setHidden(search_text not in inner_sight_name.lower())
                            
        target_list.doItemsLayout()
        target_list.update()

    def activate_selected_sights(self):
        if not hasattr(self, 'repo_list'): return
        selected_items = self.repo_list.selectedItems()
        if not selected_items: return
        game_path = self.input_game_path.text().strip() if hasattr(self, 'input_game_path') else ""
        if not game_path:
            QMessageBox.critical(self, "Error", "Set valid game directory first!")
            return
        from src.models.game_sync import create_sight_symlink
        sights_cache = getattr(self, 'sights_cache_memory', [])
        for item in selected_items:
            sight_name = item.data(Qt.ItemDataRole.UserRole)
            sight = next((s for s in sights_cache if s["file_name"] == sight_name), None)
            if sight and not sight["is_activated"]:
                success, msg = create_sight_symlink(sight["file_name"], sight["full_path"], game_path)
                print(msg)
                if success: sight["is_activated"] = True
        self.refresh_all_apps_data()

    def deactivate_selected_sights(self):
        if not hasattr(self, 'active_list'): return
        selected_items = self.active_list.selectedItems()
        if not selected_items:
            print("Менеджер: Не выбраны прицелы для деактивации.")
            return
            
        game_path = self.input_game_path.text().strip() if hasattr(self, 'input_game_path') else ""
        if not game_path or not os.path.exists(game_path): 
            QMessageBox.critical(self, "Error", "Set valid game directory first in Settings tab!")
            return
        
        from src.models.game_sync import remove_sight_link_from_game
        sights_cache = getattr(self, 'sights_cache_memory', [])
        updated = False
        
        for item in selected_items:
            sight_name = item.data(Qt.ItemDataRole.UserRole)
            if not sight_name: continue
            
            if remove_sight_link_from_game(sight_name, game_path):
                print(f"Стерта символьная ссылка из игры: {sight_name}")
                
                sight = next((s for s in sights_cache if s["file_name"] == sight_name), None)
                if sight:
                    sight["is_activated"] = False
                updated = True
                
        if updated:
            self.refresh_all_apps_data()
            if hasattr(self, 'active_preview_list'):
                self.active_preview_list.clear()

    def delete_selected_sights(self):
        if not hasattr(self, 'repo_list'): return
        selected_items = self.repo_list.selectedItems()
        if not selected_items: return
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Delete")
        msg_box.setText(f"Delete selected sights ({len(selected_items)} pcs)?")
        msg_box.setIcon(QMessageBox.Icon.Warning)
        delete_btn = msg_box.addButton("Delete", QMessageBox.ButtonRole.AcceptRole)
        cancel_btn = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        msg_box.exec()
        if msg_box.clickedButton() == delete_btn:
            sights_cache = getattr(self, 'sights_cache_memory', [])
            for item in selected_items:
                sight_name = item.data(Qt.ItemDataRole.UserRole)
                sight = next((s for s in sights_cache if s["file_name"] == sight_name), None)
                if sight and os.path.exists(sight["full_path"]):
                    try: os.remove(sight["full_path"])
                    except: pass
            self.refresh_all_apps_data()

    def on_create_group_clicked(self):
        text, ok = QInputDialog.getText(self, "Create New Group", "Enter new group name:")
        if ok and text:
            success, message = create_new_group(text.strip())
            if success: self.refresh_all_apps_data()

    def on_edit_group_clicked(self, group_name):
        self.current_editing_group = group_name
        print(f"Встроенное редактирование группы: {group_name}")
        if hasattr(self, 'widget_edit_panel'): self.widget_edit_panel.show()
        self.refresh_edit_dialog_ui()

    def on_delete_group_clicked(self, group_name):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Delete Group")
        msg_box.setText(f"Delete group '{group_name}'?")
        msg_box.setIcon(QMessageBox.Icon.Warning)
        delete_btn = msg_box.addButton("Delete Group", QMessageBox.ButtonRole.AcceptRole)
        cancel_btn = msg_box.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)
        msg_box.exec()
        if msg_box.clickedButton() == delete_btn:
            group_file_path = os.path.join("GroupsConfig", f"{group_name}.json")
            if os.path.exists(group_file_path):
                try: os.remove(group_file_path)
                except: pass
            if hasattr(self, 'widget_edit_panel'): self.widget_edit_panel.hide()
            self.refresh_all_apps_data()
    


    def refresh_edit_dialog_ui(self):
        if not hasattr(self, 'current_editing_group') or not hasattr(self, 'left_list_widget') or not hasattr(self, 'right_list_widget'): return
        self.left_list_widget.clear()
        self.right_list_widget.clear()
        
        if not getattr(self, '_edit_signals_connected', False):
            self.left_list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
            self.right_list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
            self.left_list_widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            self.right_list_widget.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
            
            self.left_list_widget.itemSelectionChanged.connect(self.on_edit_left_selection_changed)
            self.right_list_widget.itemSelectionChanged.connect(self.on_edit_right_selection_changed)
            
            if hasattr(self, 'input_edit_search_left'): self.input_edit_search_left.textChanged.connect(self.filter_edit_lists)
            if hasattr(self, 'input_edit_search_right'): self.input_edit_search_right.textChanged.connect(self.filter_edit_lists)
            if hasattr(self, 'check_hide_other_grouped'): self.check_hide_other_grouped.stateChanged.connect(self.refresh_edit_dialog_ui)
            if hasattr(self, 'btn_transfer_to_group'): self.btn_transfer_to_group.clicked.connect(self.transfer_to_group)
            if hasattr(self, 'btn_transfer_from_group'): self.btn_transfer_from_group.clicked.connect(self.transfer_from_group)
            
            if hasattr(self, 'btn_edit_close'): 
                self.btn_edit_close.clicked.connect(lambda: self.widget_edit_panel.hide())
            if hasattr(self, 'btn_rename_group_title'): 
                self.btn_rename_group_title.clicked.connect(self.on_rename_group_clicked_inline)
                
            self._edit_signals_connected = True

        from src.models.storage import get_all_sights
        from src.models.groups import load_all_groups_data
        all_sights = get_all_sights()
        all_groups_data = load_all_groups_data()
        current_group_sights = all_groups_data.get(self.current_editing_group, [])
        hide_other_grouped = self.check_hide_other_grouped.isChecked() if hasattr(self, 'check_hide_other_grouped') else False

        for sight in all_sights:
            name = sight["file_name"]
            img_marker = "  [🖼️]" if sight.get("has_images", False) else ""
            if name in current_group_sights:
                item = QListWidgetItem(f"📄  {name}{img_marker}")
                item.setData(Qt.ItemDataRole.UserRole, name)
                self.right_list_widget.addItem(item)
            else:
                if hide_other_grouped and sight["in_group"]: continue
                item = QListWidgetItem(f"📄  {name}{img_marker}")
                item.setData(Qt.ItemDataRole.UserRole, name)
                self.left_list_widget.addItem(item)
                
        if self.right_list_widget.count() == 0:
            item = QListWidgetItem("No sights in this group yet.")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.right_list_widget.addItem(item)
        self.filter_edit_lists()

    def filter_edit_lists(self):
        search_left = self.input_edit_search_left.text().lower().strip() if hasattr(self, 'input_edit_search_left') else ""
        if hasattr(self, 'left_list_widget') and self.left_list_widget:
            for i in range(self.left_list_widget.count()):
                item = self.left_list_widget.item(i)
                sn = item.data(Qt.ItemDataRole.UserRole)
                if sn: item.setHidden(search_left not in sn.lower())

        search_right = self.input_edit_search_right.text().lower().strip() if hasattr(self, 'input_edit_search_right') else ""
        if hasattr(self, 'right_list_widget') and self.right_list_widget:
            for i in range(self.right_list_widget.count()):
                item = self.right_list_widget.item(i)
                sn = item.data(Qt.ItemDataRole.UserRole)
                if sn: item.setHidden(search_right not in sn.lower())

    def transfer_to_group(self):
        if not hasattr(self, 'left_list_widget'): return
        selected_sights = [item.data(Qt.ItemDataRole.UserRole) for item in self.left_list_widget.selectedItems() if item.data(Qt.ItemDataRole.UserRole)]
        if not selected_sights: return
        from src.models.groups import load_all_groups_data, save_single_group_config
        config = load_all_groups_data()
        current_sights = config.get(self.current_editing_group, [])
        current_sights.extend(selected_sights)
        save_single_group_config(self.current_editing_group, list(set(current_sights)))
        
        self.refresh_all_apps_data()

    def transfer_from_group(self):
        if not hasattr(self, 'right_list_widget'): return
        selected_sights = [item.data(Qt.ItemDataRole.UserRole) for item in self.right_list_widget.selectedItems() if item.data(Qt.ItemDataRole.UserRole)]
        if not selected_sights: return
        from src.models.groups import load_all_groups_data, save_single_group_config
        config = load_all_groups_data()
        current_sights = config.get(self.current_editing_group, [])
        for name in selected_sights:
            if name in current_sights: current_sights.remove(name)
        save_single_group_config(self.current_editing_group, current_sights)
        
        self.refresh_all_apps_data()

    def on_rename_group_clicked_inline(self):
        if not hasattr(self, 'current_editing_group'): return
        text, ok = QInputDialog.getText(self, "Rename Group", "Enter new name:", text=self.current_editing_group)
        if ok and text and text.strip() != self.current_editing_group:
            from src.models.groups import rename_group_file
            success, message = rename_group_file(self.current_editing_group, text.strip())
            if success:
                self.current_editing_group = text.strip()
                self.refresh_all_apps_data()

    def on_rebuild_selected_previews_clicked(self):
        if not hasattr(self, 'repo_list'): return
        
        selected_items = self.repo_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Внимание", "Выделите хотя бы один прицел в списке для регенерации картинок!")
            return
            
        selected_sight_names = [item.data(Qt.ItemDataRole.UserRole) for item in selected_items if item.data(Qt.ItemDataRole.UserRole)]
        
        from src.views.generator_dialog import GeneratorDialog
        
        dialog = GeneratorDialog(self, target_sight_names=selected_sight_names)
        dialog.exec()
        
        self.on_repo_selection_changed()