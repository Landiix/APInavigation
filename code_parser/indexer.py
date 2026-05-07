import sys
import ast
import os

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Добавляем этот путь в список поиска модулей самым первым
if root_path not in sys.path:
    sys.path.insert(0, root_path)
# Импортируем функции из твоего db_manager
from database.db_manager import save_file_info, save_entities, init_db

def index_all_files(directory_path):
    """
    Проходит по всем .py файлам в указанной папке,
    извлекает структуру кода и сохраняет её в БД.
    """
    # Убеждаемся, что база данных и таблицы созданы
    init_db()

    if not os.path.exists(directory_path):
        print(f"Ошибка: Папка {directory_path} не найдена.")
        return

    # Список всех файлов в папке
    files = [f for f in os.listdir(directory_path) if f.endswith(".py")]
    
    if not files:
        print("В папке нет .py файлов для индексации.")
        return

    for filename in files:
        file_path = os.path.join(directory_path, filename)
        
        # 1. Сохраняем файл в таблицу 'files' и получаем его уникальный ID
        file_id = save_file_info(filename, file_path)
        
        # 2. Читаем и парсим код файла через AST
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                tree = ast.parse(f.read())
            except Exception as e:
                print(f"Не удалось спарсить файл {filename}: {e}")
                continue
        
        entities_to_save = []

        # 3. Обходим узлы дерева (верхний уровень)
        for node in tree.body:
            # Если нашли функцию (FunctionDef)
            if isinstance(node, ast.FunctionDef):
                entities_to_save.append({
                    "file_id": file_id,
                    "type": "function",
                    "name": node.name,
                    "lineno_start": node.lineno,
                    # end_lineno доступен в Python 3.8+
                    "lineno_end": getattr(node, "end_lineno", node.lineno),
                    "docstring": ast.get_docstring(node)
                })
            
            # Если нашли класс (ClassDef)
            elif isinstance(node, ast.ClassDef):
                entities_to_save.append({
                    "file_id": file_id,
                    "type": "class",
                    "name": node.name,
                    "lineno_start": node.lineno,
                    "lineno_end": getattr(node, "end_lineno", node.lineno),
                    "docstring": ast.get_docstring(node)
                })
        
        # 4. Сохраняем все найденные функции и классы этого файла в БД одним махом
        if entities_to_save:
            save_entities(entities_to_save)
            print(f"успешно: {filename} ({len(entities_to_save)} объектов)")

if __name__ == "__main__":
    # Запуск индексации твоей папки с данными
    index_all_files("data")