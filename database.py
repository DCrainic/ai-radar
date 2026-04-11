"""
SQLite persistence layer for AI Radar.
Handles tweets, saved content ideas, and app settings.
"""

import sqlite3
import json
from datetime import datetime, timezone

DB_PATH = "ai_radar.db"


class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS tweets (
                    id          TEXT PRIMARY KEY,
                    author      TEXT NOT NULL,
                    text        TEXT NOT NULL,
                    likes       INTEGER DEFAULT 0,
                    retweets    INTEGER DEFAULT 0,
                    replies     INTEGER DEFAULT 0,
                    posted_at   TEXT NOT NULL,
                    url         TEXT,
                    category    TEXT,
                    trend_score REAL DEFAULT 0,
                    fetched_at  TEXT
                );

                CREATE TABLE IF NOT EXISTS content_ideas (
                    tweet_id TEXT PRIMARY KEY,
                    saved_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS settings (
                    key   TEXT PRIMARY KEY,
                    value TEXT
                );
            """)

    # ── Tweets ────────────────────────────────────────────────────────────

    def upsert_tweets(self, tweets: list[dict]):
        """Insert or replace a list of tweet dicts."""
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT OR REPLACE INTO tweets
                    (id, author, text, likes, retweets, replies,
                     posted_at, url, category, trend_score, fetched_at)
                VALUES
                    (:id, :author, :text, :likes, :retweets, :replies,
                     :posted_at, :url, :category, :trend_score, :fetched_at)
                """,
                [
                    {**t, "trend_score": t.get("trend_score", 0), "fetched_at": now}
                    for t in tweets
                ],
            )

    def get_tweets(
        self,
        hours: int = 24,
        category: str | None = None,
        min_engagement: int = 0,
        account: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        query = """
            SELECT *
            FROM   tweets
            WHERE  datetime(posted_at) >= datetime('now', :window)
              AND  (likes + retweets * 3 + replies * 2) >= :min_eng
        """
        params: dict = {"window": f"-{hours} hours", "min_eng": min_engagement}

        if category and category != "all":
            query += " AND category = :category"
            params["category"] = category

        if account and account != "All":
            query += " AND author = :account"
            params["account"] = account

        query += " ORDER BY trend_score DESC LIMIT :limit"
        params["limit"] = limit

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def get_tweet(self, tweet_id: str) -> dict | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM tweets WHERE id = ?", (tweet_id,)
            ).fetchone()
        return dict(row) if row else None

    def tweet_count(self) -> int:
        with self._connect() as conn:
            return conn.execute("SELECT COUNT(*) FROM tweets").fetchone()[0]

    # ── Trend graph data ──────────────────────────────────────────────────

    def get_hourly_volume(self, hours: int = 24) -> list[dict]:
        """Return tweet counts grouped by hour and category for the trend graph."""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    strftime('%Y-%m-%d %H:00', posted_at) AS hour,
                    category,
                    COUNT(*)                               AS count
                FROM  tweets
                WHERE datetime(posted_at) >= datetime('now', :window)
                GROUP BY hour, category
                ORDER BY hour
                """,
                {"window": f"-{hours} hours"},
            ).fetchall()
        return [dict(r) for r in rows]

    # ── Content ideas ─────────────────────────────────────────────────────

    def save_idea(self, tweet_id: str):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO content_ideas (tweet_id, saved_at) VALUES (?, ?)",
                (tweet_id, datetime.now(timezone.utc).isoformat()),
            )

    def remove_idea(self, tweet_id: str):
        with self._connect() as conn:
            conn.execute(
                "DELETE FROM content_ideas WHERE tweet_id = ?", (tweet_id,)
            )

    def is_idea(self, tweet_id: str) -> bool:
        with self._connect() as conn:
            return bool(
                conn.execute(
                    "SELECT 1 FROM content_ideas WHERE tweet_id = ?", (tweet_id,)
                ).fetchone()
            )

    def get_ideas(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT t.*, ci.saved_at AS idea_saved_at
                FROM   content_ideas ci
                JOIN   tweets t ON t.id = ci.tweet_id
                ORDER  BY ci.saved_at DESC
                """
            ).fetchall()
        return [dict(r) for r in rows]

    # ── Settings ──────────────────────────────────────────────────────────

    def get_setting(self, key: str, default=None):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT value FROM settings WHERE key = ?", (key,)
            ).fetchone()
        if row is None:
            return default
        try:
            return json.loads(row["value"])
        except (json.JSONDecodeError, TypeError):
            return row["value"]

    def set_setting(self, key: str, value):
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, json.dumps(value)),
            )
