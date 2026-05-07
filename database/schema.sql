-- Таблица для хранения информации о файлах
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    path TEXT NOT NULL
);

-- Таблица для хранения классов и функций
CREATE TABLE IF NOT EXISTS code_entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_id INTEGER NOT NULL,
    type TEXT NOT NULL, -- 'function' или 'class'
    name TEXT NOT NULL,
    lineno_start INTEGER NOT NULL,
    lineno_end INTEGER NOT NULL,
    docstring TEXT,
    FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE
);

-- Индекс для быстрого регистронезависимого поиска по имени
CREATE INDEX IF NOT EXISTS idx_entity_name ON code_entities(name);