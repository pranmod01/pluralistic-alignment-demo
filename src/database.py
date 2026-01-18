"""
Database layer for Pluralistic Alignment Demo v1 MVP.

Tables:
- interactions: Stores user queries and generated perspectives
- feedback: Stores user feedback on interactions
- perspective_cache: Consistency cache (managed by cache.py)
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional

from config import DB_PATH


def init_db():
    """Initialize the database with all required tables."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Interactions table - stores queries and responses
    c.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            question TEXT NOT NULL,
            topic_category TEXT,
            controversy_profile_json TEXT,
            selected_communities_json TEXT,
            perspectives_json TEXT NOT NULL,
            synthesis TEXT,
            standard_response TEXT,
            surfaced_perspectives INTEGER DEFAULT 1,
            created_at TEXT NOT NULL
        )
    """)

    # Feedback table
    c.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interaction_id INTEGER,
            user_community TEXT,
            accuracy_own_community INTEGER,
            accuracy_other_communities INTEGER,
            usefulness INTEGER,
            prefer_multiple_perspectives TEXT,
            missing_perspectives TEXT,
            comments TEXT,
            created_at TEXT,
            FOREIGN KEY(interaction_id) REFERENCES interactions(id)
        )
    """)

    # Perspective cache table
    c.execute("""
        CREATE TABLE IF NOT EXISTS perspective_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cache_key TEXT UNIQUE NOT NULL,
            community TEXT NOT NULL,
            topic_category TEXT NOT NULL,
            query_normalized TEXT NOT NULL,
            perspective_text TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            hit_count INTEGER DEFAULT 0
        )
    """)

    # Create indexes
    c.execute("CREATE INDEX IF NOT EXISTS idx_interactions_user ON interactions(user_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_interactions_topic ON interactions(topic_category)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_cache_key ON perspective_cache(cache_key)")

    conn.commit()
    conn.close()


def save_interaction(
    question: str,
    perspectives: dict[str, str],
    synthesis: Optional[str],
    user_id: Optional[str] = None,
    topic_category: Optional[str] = None,
    controversy_profile: Optional[dict] = None,
    selected_communities: Optional[list[str]] = None,
    standard_response: Optional[str] = None,
    surfaced_perspectives: bool = True
) -> int:
    """Save an interaction to the database."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()

    c.execute("""
        INSERT INTO interactions (
            user_id, question, topic_category, controversy_profile_json,
            selected_communities_json, perspectives_json, synthesis,
            standard_response, surfaced_perspectives, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        question,
        topic_category,
        json.dumps(controversy_profile) if controversy_profile else None,
        json.dumps(selected_communities) if selected_communities else None,
        json.dumps(perspectives, ensure_ascii=False),
        synthesis,
        standard_response,
        1 if surfaced_perspectives else 0,
        now
    ))

    interaction_id = c.lastrowid
    conn.commit()
    conn.close()
    return interaction_id


def save_feedback(interaction_id: int, feedback: dict):
    """Save user feedback for an interaction."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = datetime.utcnow().isoformat()

    c.execute("""
        INSERT INTO feedback (
            interaction_id, user_community, accuracy_own_community,
            accuracy_other_communities, usefulness, prefer_multiple_perspectives,
            missing_perspectives, comments, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        interaction_id,
        feedback.get("user_community"),
        feedback.get("accuracy_own_community"),
        feedback.get("accuracy_other_communities"),
        feedback.get("usefulness"),
        feedback.get("prefer_multiple_perspectives"),
        feedback.get("missing_perspectives"),
        feedback.get("comments"),
        now
    ))

    conn.commit()
    conn.close()


def fetch_interactions(limit: int = 50, user_id: Optional[str] = None) -> list[dict]:
    """Fetch recent interactions, optionally filtered by user."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if user_id:
        c.execute("""
            SELECT id, user_id, question, topic_category, perspectives_json,
                   synthesis, surfaced_perspectives, created_at
            FROM interactions
            WHERE user_id = ?
            ORDER BY id DESC LIMIT ?
        """, (user_id, limit))
    else:
        c.execute("""
            SELECT id, user_id, question, topic_category, perspectives_json,
                   synthesis, surfaced_perspectives, created_at
            FROM interactions
            ORDER BY id DESC LIMIT ?
        """, (limit,))

    rows = c.fetchall()
    conn.close()

    results = []
    for r in rows:
        results.append({
            "id": r[0],
            "user_id": r[1],
            "question": r[2],
            "topic_category": r[3],
            "perspectives": json.loads(r[4]) if r[4] else {},
            "synthesis": r[5],
            "surfaced_perspectives": bool(r[6]),
            "created_at": r[7],
        })
    return results


def get_interaction_by_id(interaction_id: int) -> Optional[dict]:
    """Fetch a single interaction by ID."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        SELECT id, user_id, question, topic_category, controversy_profile_json,
               selected_communities_json, perspectives_json, synthesis,
               standard_response, surfaced_perspectives, created_at
        FROM interactions
        WHERE id = ?
    """, (interaction_id,))

    row = c.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "user_id": row[1],
        "question": row[2],
        "topic_category": row[3],
        "controversy_profile": json.loads(row[4]) if row[4] else None,
        "selected_communities": json.loads(row[5]) if row[5] else None,
        "perspectives": json.loads(row[6]) if row[6] else {},
        "synthesis": row[7],
        "standard_response": row[8],
        "surfaced_perspectives": bool(row[9]),
        "created_at": row[10],
    }
