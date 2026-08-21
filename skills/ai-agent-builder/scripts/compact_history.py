"""Compact conversation history for a user into a single summary message.

Usage:
    python scripts/compact_history.py <user_id> [--max-turns N] [--db DATABASE_URL]

When a user's conversation history exceeds N turns, this script replaces
the oldest messages with a compact summary, keeping only the most recent
turns intact. This prevents the LLM from receiving too much context.
"""
import argparse
from datetime import datetime

from sqlalchemy import create_engine, text

DEFAULT_DB = "sqlite:///./agent.db"


def compact_history(user_id: int, max_turns: int = 20, db_url: str = DEFAULT_DB) -> None:
    """Compact history for a user, keeping only the last max_turns."""
    engine = create_engine(db_url)

    with engine.connect() as conn:
        # Count total turns
        count = conn.execute(
            text("SELECT COUNT(*) FROM conversation_memory WHERE user_id = :uid"),
            {"uid": user_id},
        ).scalar()

        if count <= max_turns:
            print(f"✅ {count} turni, sotto il limite di {max_turns}. Nessuna azione.")
            return

        # Get turns to compact (oldest ones)
        to_compact = count - max_turns
        rows = conn.execute(
            text(
                "SELECT id, role, content FROM conversation_memory "
                "WHERE user_id = :uid ORDER BY id ASC LIMIT :limit"
            ),
            {"uid": user_id, "limit": to_compact},
        ).fetchall()

        # Build summary
        user_msgs = [r for r in rows if r.role == "user"]
        assistant_msgs = [r for r in rows if r.role == "assistant"]

        summary = (
            "[RIASSUNTO DELLA PRECEDENTE CONVERSAZIONE]\n"
            f"L'utente ha inviato {len(user_msgs)} messaggi. "
            f"L'assistente ha risposto {len(assistant_msgs)} volte. "
            "Ecco i punti principali:\n"
        )
        for r in rows:
            preview = r.content[:100].replace("\n", " ")
            summary += f"- [{r.role}]: {preview}...\n"

        # Delete old messages
        conn.execute(
            text(
                "DELETE FROM conversation_memory "
                "WHERE user_id = :uid AND id IN :ids"
            ),
            {"uid": user_id, "ids": tuple(r.id for r in rows)},
        )

        # Insert summary
        conn.execute(
            text(
                "INSERT INTO conversation_memory (user_id, role, content, created_at) "
                "VALUES (:uid, 'user', :content, :ts)"
            ),
            {"uid": user_id, "content": summary, "ts": datetime.now()},
        )

        conn.commit()
        print(f"✅ Compattati {to_compact} turni in 1 riassunto. {max_turns} turni recenti preservati.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compact conversation history")
    parser.add_argument("user_id", type=int, help="Telegram user ID")
    parser.add_argument("--max-turns", type=int, default=20, help="Max turns to keep")
    parser.add_argument("--db", default=DEFAULT_DB, help="Database URL")
    args = parser.parse_args()
    compact_history(args.user_id, args.max_turns, args.db)