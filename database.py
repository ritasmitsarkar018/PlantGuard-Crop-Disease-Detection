import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

DB_PATH = Path(__file__).parent / "plantguard.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scan_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                filename TEXT NOT NULL,
                predicted_class TEXT NOT NULL,
                crop TEXT NOT NULL,
                disease TEXT NOT NULL,
                confidence REAL NOT NULL,
                severity TEXT NOT NULL,
                top_predictions TEXT NOT NULL,
                notes TEXT DEFAULT ''
            );
        """)
        conn.commit()

def save_scan(
    filename: str,
    predicted_class: str,
    crop: str,
    disease: str,
    confidence: float,
    severity: str,
    top_predictions: List[Dict[str, Any]],
    notes: str = ""
) -> int:
    init_db()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO scan_history (
                timestamp, filename, predicted_class, crop, disease, 
                confidence, severity, top_predictions, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            now_str,
            filename,
            predicted_class,
            crop,
            disease,
            round(confidence, 4),
            severity,
            json.dumps(top_predictions),
            notes
        ))
        conn.commit()
        return cursor.lastrowid

def get_recent_scans(limit: int = 30) -> List[Dict[str, Any]]:
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, timestamp, filename, predicted_class, crop, disease, 
                   confidence, severity, top_predictions, notes
            FROM scan_history
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        result = []
        for row in rows:
            d = dict(row)
            try:
                d["top_predictions"] = json.loads(d["top_predictions"])
            except Exception:
                d["top_predictions"] = []
            result.append(d)
        return result

def get_scan_stats() -> Dict[str, Any]:
    init_db()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as total FROM scan_history")
        total = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT disease, COUNT(*) as count 
            FROM scan_history 
            GROUP BY disease 
            ORDER BY count DESC 
            LIMIT 5
        """)
        common_diseases = [dict(r) for r in cursor.fetchall()]

        cursor.execute("""
            SELECT crop, COUNT(*) as count 
            FROM scan_history 
            GROUP BY crop 
            ORDER BY count DESC 
            LIMIT 5
        """)
        common_crops = [dict(r) for r in cursor.fetchall()]

        return {
            "total_scans": total,
            "top_diseases": common_diseases,
            "top_crops": common_crops
        }

def clear_all_history() -> bool:
    init_db()
    with get_connection() as conn:
        conn.execute("DELETE FROM scan_history")
        conn.commit()
    return True
