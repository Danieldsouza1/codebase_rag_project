# src/database.py — query logger using SQLite

import sqlite3
from datetime import datetime

DB_PATH = "data/query_log.db"

def log_query(query, mode, answer):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            query TEXT,
            mode TEXT,
            answer TEXT
        )
    """)
    conn.execute(
        "INSERT INTO logs VALUES (NULL, ?, ?, ?, ?)",
        (datetime.now().isoformat(), query, mode, answer)
    )
    conn.commit()
    conn.close()

def fetch_recent_logs(n=10):
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            "SELECT timestamp, mode, query FROM logs ORDER BY id DESC LIMIT ?", (n,)
        ).fetchall()
        conn.close()
        return rows
    except Exception:
        return []