import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any
from config import DB_PATH


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS interactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        perspectives_json TEXT NOT NULL,
        synthesis TEXT,
        standard_response TEXT,
        created_at TEXT NOT NULL
    )
    """
    )
    c.execute(
        """
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        interaction_id INTEGER,
        tradition_identify TEXT,
        accuracy INTEGER,
        usefulness INTEGER,
        prefer_single TEXT,
        comments TEXT,
        created_at TEXT,
        FOREIGN KEY(interaction_id) REFERENCES interactions(id)
    )
    """
    )
    conn.commit()
    conn.close()


def save_interaction(question: str, perspectives: Dict[str, str], synthesis: Optional[str], standard_response: Optional[str]) -> int:
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute(
        "INSERT INTO interactions (question, perspectives_json, synthesis, standard_response, created_at) VALUES (?, ?, ?, ?, ?)",
        (question, json.dumps(perspectives, ensure_ascii=False), synthesis, standard_response, now),
    )
    interaction_id = c.lastrowid
    conn.commit()
    conn.close()
    return interaction_id


def save_feedback(interaction_id: int, feedback: Dict[str, Any]):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute(
        "INSERT INTO feedback (interaction_id, tradition_identify, accuracy, usefulness, prefer_single, comments, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            interaction_id,
            feedback.get("tradition_identify"),
            feedback.get("accuracy"),
            feedback.get("usefulness"),
            feedback.get("prefer_single"),
            feedback.get("comments"),
            now,
        ),
    )
    conn.commit()
    conn.close()


def fetch_interactions(limit: int = 50):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, question, perspectives_json, synthesis, standard_response, created_at FROM interactions ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    results = []
    for r in rows:
        results.append({
            "id": r[0],
            "question": r[1],
            "perspectives": json.loads(r[2]),
            "synthesis": r[3],
            "standard_response": r[4],
            "created_at": r[5],
        })
    return results
