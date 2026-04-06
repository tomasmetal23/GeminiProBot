"""
memory.py — Persistent conversation memory using SQLite.
Each user gets their own history and optional custom system prompt.
"""
import sqlite3
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "/app/data/bot_memory.db")

DEFAULT_SYSTEM_PROMPT = os.getenv(
    "DEFAULT_SYSTEM_PROMPT",
    "Eres un asistente inteligente, útil y conciso. Respondes en el mismo idioma que el usuario.",
)
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "20"))


def _get_conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables if they don't exist. Call once at startup."""
    with _get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id  INTEGER NOT NULL,
                role     TEXT    NOT NULL,
                content  TEXT    NOT NULL,
                ts       DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS system_prompts (
                user_id INTEGER PRIMARY KEY,
                prompt  TEXT NOT NULL
            )
            """
        )
        conn.commit()
    logger.info("✅ Database initialized at %s", DB_PATH)


def get_history(user_id: int) -> list[dict]:
    """Return the last MAX_HISTORY messages for a user, oldest first."""
    with _get_conn() as conn:
        rows = conn.execute(
            """
            SELECT role, content FROM (
                SELECT role, content, ts
                FROM messages
                WHERE user_id = ?
                ORDER BY ts DESC
                LIMIT ?
            ) ORDER BY ts ASC
            """,
            (user_id, MAX_HISTORY),
        ).fetchall()
    return [{"role": r["role"], "content": r["content"]} for r in rows]


def add_message(user_id: int, role: str, content: str) -> None:
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
            (user_id, role, content),
        )
        conn.commit()


def clear_history(user_id: int) -> int:
    """Delete all messages for a user. Returns number of deleted rows."""
    with _get_conn() as conn:
        cur = conn.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
        conn.commit()
        return cur.rowcount


def get_system_prompt(user_id: int) -> str:
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT prompt FROM system_prompts WHERE user_id = ?", (user_id,)
        ).fetchone()
    return row["prompt"] if row else DEFAULT_SYSTEM_PROMPT


def set_system_prompt(user_id: int, prompt: str) -> None:
    with _get_conn() as conn:
        conn.execute(
            "INSERT INTO system_prompts (user_id, prompt) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET prompt = excluded.prompt",
            (user_id, prompt),
        )
        conn.commit()


def reset_system_prompt(user_id: int) -> None:
    with _get_conn() as conn:
        conn.execute("DELETE FROM system_prompts WHERE user_id = ?", (user_id,))
        conn.commit()
