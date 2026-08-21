"""Migrate conversation history from one user_id to another.

Usage:
    python scripts/migrate_user.py <source_id> <target_id> [--db DATABASE_URL]

Useful when moving from CLI mode (user_id=1) to Telegram mode (your Telegram ID).
"""
import argparse

from sqlalchemy import create_engine, text

DEFAULT_DB = "sqlite:///./agent.db"


def migrate_user(source_id: int, target_id: int, db_url: str = DEFAULT_DB) -> None:
    """Copy all conversation history from source_id to target_id."""
    engine = create_engine(db_url)

    with engine.connect() as conn:
        # Check source exists
        source_count = conn.execute(
            text("SELECT COUNT(*) FROM conversation_memory WHERE user_id = :uid"),
            {"uid": source_id},
        ).scalar()

        if source_count == 0:
            print(f"❌ Nessun messaggio trovato per user_id={source_id}")
            return

        # Check if target already has messages
        target_count = conn.execute(
            text("SELECT COUNT(*) FROM conversation_memory WHERE user_id = :uid"),
            {"uid": target_id},
        ).scalar()

        if target_count > 0:
            print(f"⚠️  user_id={target_id} ha già {target_count} messaggi.")
            confirm = input("Aggiungere comunque? (s/N): ")
            if confirm.lower() != "s":
                print("Annullato.")
                return

        # Copy messages
        rows = conn.execute(
            text(
                "SELECT role, content, created_at FROM conversation_memory "
                "WHERE user_id = :uid ORDER BY id ASC"
            ),
            {"uid": source_id},
        ).fetchall()

        for role, content, created_at in rows:
            conn.execute(
                text(
                    "INSERT INTO conversation_memory (user_id, role, content, created_at) "
                    "VALUES (:uid, :role, :content, :ts)"
                ),
                {"uid": target_id, "role": role, "content": content, "ts": created_at},
            )

        conn.commit()
        print(f"✅ Migrati {len(rows)} messaggi da user_id={source_id} a user_id={target_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate conversation history between users")
    parser.add_argument("source_id", type=int, help="Source user ID")
    parser.add_argument("target_id", type=int, help="Target user ID")
    parser.add_argument("--db", default=DEFAULT_DB, help="Database URL")
    args = parser.parse_args()
    migrate_user(args.source_id, args.target_id, args.db)