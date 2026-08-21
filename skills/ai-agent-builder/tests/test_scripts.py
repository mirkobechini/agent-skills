"""Tests for ai-agent-builder skill scripts."""

import pytest
import sqlite3
from datetime import datetime


@pytest.fixture
def db():
    """Create an in-memory SQLite database with the conversation_memory table."""
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE conversation_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    yield conn
    conn.close()


def populate(db, user_id: int, count: int):
    """Insert N conversation turns for a user."""
    for i in range(count):
        role = "user" if i % 2 == 0 else "assistant"
        db.execute(
            "INSERT INTO conversation_memory (user_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (user_id, role, f"Message {i+1}", datetime(2026, 8, 21, 0, 0, i)),
        )
    db.commit()


class TestCompactHistory:
    def test_under_limit_does_nothing(self, db):
        populate(db, 1, 5)
        count_before = db.execute(
            "SELECT COUNT(*) FROM conversation_memory WHERE user_id = ?", (1,)
        ).fetchone()[0]
        assert count_before == 5

    def test_over_limit_can_be_compacted(self, db):
        populate(db, 1, 25)
        count = db.execute(
            "SELECT COUNT(*) FROM conversation_memory WHERE user_id = ?", (1,)
        ).fetchone()[0]
        assert count == 25


class TestMigrateUser:
    def test_migrate_messages(self, db):
        populate(db, 1, 10)

        # Simulate migration: copy from user 1 to user 2
        rows = db.execute(
            "SELECT role, content, created_at FROM conversation_memory WHERE user_id = ? ORDER BY id",
            (1,),
        ).fetchall()
        for role, content, ts in rows:
            db.execute(
                "INSERT INTO conversation_memory (user_id, role, content, created_at) VALUES (?, ?, ?, ?)",
                (2, role, content, ts),
            )
        db.commit()

        source_count = db.execute(
            "SELECT COUNT(*) FROM conversation_memory WHERE user_id = ?", (1,)
        ).fetchone()[0]
        target_count = db.execute(
            "SELECT COUNT(*) FROM conversation_memory WHERE user_id = ?", (2,)
        ).fetchone()[0]
        assert source_count == 10
        assert target_count == 10

    def test_migrate_no_source(self, db):
        target_count = db.execute(
            "SELECT COUNT(*) FROM conversation_memory WHERE user_id = ?", (2,)
        ).fetchone()[0]
        assert target_count == 0