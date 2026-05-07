import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "archive.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")

def get_connection():
    """Создает и возвращает подключение к базе данных."""
    conn = sqlite3.connect(DB_PATH)
    # Включаем поддержку внешних ключей (Foreign Keys) в SQLite
    conn.execute("PRAGMA foreign_keys = ON;")
    # Данные из запросов будут возвращаться в виде удобных словарей, а не кортежей
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Читает schema.sql и создает таблицы, если их нет."""
    if not os.path.exists(SCHEMA_PATH):
        raise FileNotFoundError(f"Файл схемы не найден по пути: {SCHEMA_PATH}")
        
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        sql_script = f.read()
        
    conn = get_connection()
    try:
        conn.executescript(sql_script)
        conn.commit()
        print("База данных успешно инициализирована!")
    except Exception as e:
        print(f"Ошибка при инициализации БД: {e}")
    finally:
        conn.close()

def save_file_info(file_name: str, file_path: str) -> int:
    """Сохраняет файл в БД и возвращает его id."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Используем INSERT OR IGNORE, чтобы не дублировать файлы при повторном запуске
        cursor.execute(
            "INSERT OR IGNORE INTO files (name, path) VALUES (?, ?)",
            (file_name, file_path)
        )
        conn.commit()
        
        # Получаем id файла (либо только что созданного, либо существующего)
        cursor.execute("SELECT id FROM files WHERE name = ?", (file_name,))
        file_id = cursor.fetchone()["id"]
        return file_id
    finally:
        conn.close()

def save_entities(entities: list[dict]):
    """
    Массово сохраняет сущности (функции/классы) в БД.
    Ожидает список словарей с ключами: file_id, type, name, lineno_start, lineno_end, docstring
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.executemany(
            """
            INSERT INTO code_entities (file_id, type, name, lineno_start, lineno_end, docstring)
            VALUES (:file_id, :type, :name, :lineno_start, :lineno_end, :docstring)
            """,
            entities
        )
        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    print("Запуск инициализации базы данных...")
    init_db()