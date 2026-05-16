from fastapi import FastAPI, Query
from database.db_manager import get_connection
import sqlite3

app = FastAPI(title="API Навигации по коду")

@app.get("/")
def root():
    return {
        "message": "Сервис навигации по коду активен",
        "docs": "Перейдите на /docs для тестирования API"
    }

# Хелпер для превращения строк базы в удобные словари
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.get("/api/files")
def list_files():
    """Возвращает список всех проиндексированных файлов."""
    conn = get_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    cursor.execute("SELECT name, path FROM files")
    files = cursor.fetchall()
    conn.close()
    return files

@app.get("/api/search")
def search(q: str = Query(None), type: str = Query("None"), limit: int = Query(None), offset: int = Query(None)):
    """
    Поиск функций и классов. 
    Если запрос пустой или состоит из пробелов — возвращаем пустой список.
    """
    if not q or not q.strip():
        return []

    conn = get_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    # Очищаем запрос от лишних пробелов для более точного поиска
    clean_query = q.strip()
    search_pattern = f"%{clean_query}%"
    
    cursor.execute("""
        SELECT type, name, lineno_start, lineno_end, docstring 
        FROM code_entities 
        WHERE (name LIKE ? OR docstring LIKE ?) AND type LIKE ?
        LIMIT ? OFFSET ?
                   
    """, (search_pattern, search_pattern, type, limit, offset))
    print(type, search_pattern)
    results = cursor.fetchall()
    conn.close()
    return results


@app.get("/api/files/{filename}/structure")
def get_structure(filename: str, type: str = Query(None)):
    """Возвращает все функции и классы конкретного файла."""
    conn = get_connection()
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
   
    cursor.execute("""
        SELECT ce.type, ce.name, ce.lineno_start, ce.lineno_end, ce.docstring
        FROM code_entities ce
        JOIN files f ON ce.file_id = f.id
        WHERE f.name = ? AND ce.type LIKE ?
    """, (filename,type))
    print(type)
    results = cursor.fetchall()
    conn.close()
    return results

@app.get("/api/stats")
def get_stats():
    """Возвращает статистику по проиндексированным файлам."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM files")
    total_files = cursor.fetchone()[0]
    
    cursor.execute("SELECT type, COUNT(*) FROM code_entities GROUP BY type")
    entity_counts = {row[0]: row[1] for row in cursor.fetchall()}
    
    conn.close()
    
    return {
        "total_files": total_files,
        "entity_counts": entity_counts
    }