"""
Consistency cache for perspective generation.

Ensures that the same community-topic pairs receive identical framing
across different users asking similar questions.

Cache key: hash(community, topic_category, query_normalized)
"""

import hashlib
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Optional

from config import DB_PATH


def _normalize_query(query: str) -> str:
    """Normalize a query for cache key generation."""
    # Lowercase, remove extra whitespace, remove punctuation
    normalized = query.lower().strip()
    normalized = " ".join(normalized.split())
    return normalized


def _generate_cache_key(community: str, topic_category: str, query: str) -> str:
    """Generate a cache key for a community-topic-query combination."""
    normalized_query = _normalize_query(query)
    key_string = f"{community}|{topic_category}|{normalized_query}"
    return hashlib.sha256(key_string.encode()).hexdigest()[:32]


def init_cache_table():
    """Initialize the perspective cache table."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
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
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_cache_key ON perspective_cache(cache_key)
    """)
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_community_topic ON perspective_cache(community, topic_category)
    """)
    conn.commit()
    conn.close()


def get_cached_perspective(
    community: str,
    topic_category: str,
    query: str
) -> Optional[str]:
    """
    Retrieve a cached perspective if available and not expired.

    Args:
        community: Community ID
        topic_category: Topic category from controversy detection
        query: The user's query

    Returns:
        Cached perspective text or None if not found/expired
    """
    cache_key = _generate_cache_key(community, topic_category, query)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT perspective_text, expires_at, id
        FROM perspective_cache
        WHERE cache_key = ?
    """, (cache_key,))
    row = c.fetchone()

    if row:
        perspective_text, expires_at, row_id = row
        # Check if expired
        if datetime.fromisoformat(expires_at) > datetime.utcnow():
            # Update hit count
            c.execute("""
                UPDATE perspective_cache
                SET hit_count = hit_count + 1
                WHERE id = ?
            """, (row_id,))
            conn.commit()
            conn.close()
            return perspective_text

    conn.close()
    return None


def store_cached_perspective(
    community: str,
    topic_category: str,
    query: str,
    perspective_text: str,
    ttl_days: int = 30
):
    """
    Store a perspective in the cache.

    Args:
        community: Community ID
        topic_category: Topic category from controversy detection
        query: The user's query
        perspective_text: Generated perspective to cache
        ttl_days: Time-to-live in days (default 30)
    """
    cache_key = _generate_cache_key(community, topic_category, query)
    normalized_query = _normalize_query(query)
    now = datetime.utcnow()
    expires_at = now + timedelta(days=ttl_days)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Upsert: insert or replace if exists
    c.execute("""
        INSERT INTO perspective_cache
            (cache_key, community, topic_category, query_normalized,
             perspective_text, created_at, expires_at, hit_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0)
        ON CONFLICT(cache_key) DO UPDATE SET
            perspective_text = excluded.perspective_text,
            created_at = excluded.created_at,
            expires_at = excluded.expires_at
    """, (
        cache_key, community, topic_category, normalized_query,
        perspective_text, now.isoformat(), expires_at.isoformat()
    ))
    conn.commit()
    conn.close()


def clear_expired_cache():
    """Remove expired entries from the cache."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        DELETE FROM perspective_cache
        WHERE expires_at < ?
    """, (datetime.utcnow().isoformat(),))
    deleted = c.rowcount
    conn.commit()
    conn.close()
    return deleted


def get_cache_stats() -> dict:
    """Get cache statistics."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM perspective_cache")
    total_entries = c.fetchone()[0]

    c.execute("SELECT SUM(hit_count) FROM perspective_cache")
    total_hits = c.fetchone()[0] or 0

    c.execute("""
        SELECT community, COUNT(*) as count
        FROM perspective_cache
        GROUP BY community
        ORDER BY count DESC
        LIMIT 10
    """)
    top_communities = c.fetchall()

    conn.close()

    return {
        "total_entries": total_entries,
        "total_hits": total_hits,
        "top_communities": top_communities,
    }
