import os
import json
import shutil

# Жесткие пути в архитектуре MVC к новой папке data
REPOSITORY_DIR = os.path.join("data", "UserSights")
IMAGES_DIR = os.path.join("data", "SightsImages")
CACHE_FILE = os.path.join("data", "sights_cache.json")

def init_app_folders():
    """Автоматически создает структуру папок пользователя внутри data/ при первом старте"""
    os.makedirs(REPOSITORY_DIR, exist_ok=True)
    os.makedirs(IMAGES_DIR, exist_ok=True)

def rebuild_sights_cache():
    """[BULLETPROOF CACHE] Полная пересборка кэша репозитория с учетом пробелов Windows и групп"""
    if not os.path.exists(REPOSITORY_DIR):
        return

    # Загружаем данные групп для проверки флага in_group
    from src.models.groups import load_all_groups_data
    all_groups_data = load_all_groups_data()
    
    # Собираем все имена прицелов, которые уже состоят в группах
    sights_in_groups = []
    for g_name, g_list in all_groups_data.items():
        sights_in_groups.extend(g_list)

    cache_data = []

    # ЖЕСТКИЙ ЦИКЛ: Имя переменной строго 'sight' во всех внутренних узлах!
    for sight in os.listdir(REPOSITORY_DIR):
        if sight.lower().endswith('.blk'):
            # ФИКС ПРОБЕЛОВ: Отрезаем расширение и намертво чистим пробелы на конце строки
            sight_name_no_ext = os.path.splitext(sight)[0].strip()
            
            # Собираем чистый путь к папке превью
            images_path = os.path.join(IMAGES_DIR, sight_name_no_ext)
            
            has_images = False
            if os.path.exists(images_path) and os.path.isdir(images_path):
                valid_exts = ('.png', '.jpg', '.jpeg')
                try:
                    images_in_dir = [f for f in os.listdir(images_path) if f.lower().endswith(valid_exts)]
                    if images_in_dir:
                        has_images = True
                except:
                    has_images = False

            # ИСПРАВЛЕНО: Проверяем, входит ли наш 'sight' в списки групп кентов
            in_group = sight in sights_in_groups

            # Пакуем в кэш-словарь
            cache_data.append({
                "file_name": sight,
                "full_path": os.path.abspath(os.path.join(REPOSITORY_DIR, sight)),
                "has_images": has_images,
                "in_group": in_group,
                "is_activated": False # Базовый флаг, MainWindow пересчитает его в реальном времени
            })

    # Сохраняем готовый кэш в JSON
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=4)
        print(f"✅ Кэш успешно обновлен! Записано {len(cache_data)} прицелов.")
    except Exception as e:
        print(f"🛑 Критическая ошибка записи файла кэша: {e}")

def get_all_sights(force_refresh=False):
    """
    Супер-быстрое чтение. Если force_refresh=False, мгновенно отдает данные из файла кэша,
    вообще не сканируя папки и не трогая жесткий диск.
    """
    if force_refresh or not os.path.exists(CACHE_FILE):
        return rebuild_sights_cache()
        
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка чтения кэша, пересобираем: {e}")
        return rebuild_sights_cache()

def import_sights_files(parent_window):
    """Открывает диалог выбора файлов .blk и копирует их в SightsRepository"""
    files, _ = QFileDialog.getOpenFileNames(
        parent_window, "Import Custom Sights", "", "War Thunder Sights (*.blk)"
    )
    if files:
        init_app_folders()
        imported_count = 0
        for src_path in files:
            file_name = os.path.basename(src_path)
            dest_path = os.path.join(REPOSITORY_DIR, file_name)
            try:
                shutil.copy2(src_path, dest_path)
                imported_count += 1
            except Exception as e:
                print(f"Error importing {file_name}: {e}")
        
        # После импорта принудительно обновляем кэш
        rebuild_sights_cache()
        return imported_count
    return 0