"""Scaffold a new AI agent project.

Usage:
    python scripts/scaffold.py my-agent [--telegram] [--db sqlite|postgres]

Creates a complete project structure with LangGraph agent, memory, tools,
and optional Telegram bot integration.
"""
import argparse
import os
import shutil


def scaffold(agent_name: str, with_telegram: bool = False, db: str = "sqlite") -> None:
    """Generate a new agent project directory."""
    target = os.path.join(os.getcwd(), agent_name)

    if os.path.exists(target):
        print(f"[ERRORE] Directory '{target}' already exists.")
        return

    # Create directory structure
    dirs = [
        f"{target}/agent/prompts",
        f"{target}/agent/tools",
        f"{target}/db/models",
        f"{target}/services",
        f"{target}/tests",
    ]
    if with_telegram:
        dirs += [f"{target}/bot/handlers", f"{target}/bot/middleware"]

    for d in dirs:
        os.makedirs(d)
        with open(os.path.join(d, "__init__.py"), "w") as f:
            f.write("")

    # ── agent/prompts/persona.py ──
    with open(f"{target}/agent/prompts/persona.py", "w") as f:
        f.write(f'''"""System prompt for {agent_name} agent."""

AGENT_SYSTEM_PROMPT = """Sei {agent_name}, un assistente AI specializzato.

## Personalità
- [TRATTO_1]
- [TRATTO_2]
- [TRATTO_3]

## Regole di comportamento
1. [REGOLA_1]
2. [REGOLA_2]
3. [REGOLA_3]

## Conoscenze
- [CONOSCENZA_1]
- [CONOSCENZA_2]

## Strumenti a disposizione
- [tool_name(param)]: [descrizione]

## Formato risposta
[ISTRUZIONI_FORMATO]

## Regola importante: non ripeterti
Quando riprendi un discorso interrotto, NON ripetere concetti già detti in precedenza.
Vai dritto al punto.
"""
''')

    # ── agent/memory.py ──
    with open(f"{target}/agent/memory.py", "w") as f:
        f.write('''"""Memory layer — read/write conversation history from database."""

from datetime import datetime
from typing import Any

from sqlalchemy import select

from db.database import SessionLocal
from db.models import ConversationMemory

MAX_HISTORY_TURNS = 20


def load_memory(user_id: int) -> list[dict[str, Any]]:
    """Load the last N conversation turns for a user."""
    session = SessionLocal()
    try:
        stmt = (
            select(ConversationMemory)
            .where(ConversationMemory.user_id == user_id)
            .order_by(ConversationMemory.created_at.desc())
            .limit(MAX_HISTORY_TURNS)
        )
        rows = session.execute(stmt).scalars().all()
        rows.reverse()
        return [{"role": r.role, "content": r.content} for r in rows]
    finally:
        session.close()


def save_turn(user_id: int, role: str, content: str) -> None:
    """Save a single conversation turn."""
    session = SessionLocal()
    try:
        record = ConversationMemory(user_id=user_id, role=role, content=content)
        session.add(record)
        session.commit()
    finally:
        session.close()


def trim_history(user_id: int, max_turns: int = MAX_HISTORY_TURNS) -> None:
    """Remove oldest turns if history exceeds max_turns."""
    session = SessionLocal()
    try:
        stmt = (
            select(ConversationMemory)
            .where(ConversationMemory.user_id == user_id)
            .order_by(ConversationMemory.created_at.desc())
        )
        rows = session.execute(stmt).scalars().all()
        if len(rows) > max_turns:
            for record in rows[max_turns:]:
                session.delete(record)
        session.commit()
    finally:
        session.close()
''')

    # ── agent/graph.py ──
    with open(f"{target}/agent/graph.py", "w") as f:
        f.write('''"""LangGraph state machine for the agent."""

import json
import os
from typing import Annotated, Any, Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from agent.memory import load_memory, save_turn, trim_history
from agent.prompts.persona import AGENT_SYSTEM_PROMPT
from agent.tools.registry import TOOL_DEFINITIONS, execute_tool_call


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    user_id: int
    tool_calls: list[dict[str, Any]]


def load_memory_node(state: AgentState) -> dict:
    user_id = state["user_id"]
    history = load_memory(user_id)
    messages = [SystemMessage(content=AGENT_SYSTEM_PROMPT)]
    for h in history:
        if h["role"] == "user":
            messages.append(HumanMessage(content=h["content"]))
        elif h["role"] == "assistant":
            messages.append(AIMessage(content=h["content"]))
    for msg in state["messages"]:
        if isinstance(msg, HumanMessage):
            messages.append(msg)
    return {"messages": messages}


def call_llm(state: AgentState) -> dict:
    from openai import OpenAI

    model = os.getenv("DEFAULT_MODEL", "google/gemini-2.5-flash")
    api_key = os.getenv("OPENROUTER_API_KEY", "")

    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

    openai_messages = []
    for msg in state["messages"]:
        if isinstance(msg, SystemMessage):
            openai_messages.append({"role": "system", "content": msg.content})
        elif isinstance(msg, HumanMessage):
            openai_messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            d = {"role": "assistant", "content": msg.content or ""}
            if msg.tool_calls:
                d["tool_calls"] = msg.tool_calls
            openai_messages.append(d)
        elif isinstance(msg, ToolMessage):
            openai_messages.append({"role": "tool", "content": msg.content, "tool_call_id": msg.tool_call_id})

    response = client.chat.completions.create(
        model=model,
        messages=openai_messages,
        tools=TOOL_DEFINITIONS,
        tool_choice="auto",
    )

    choice = response.choices[0]
    msg = choice.message

    result: dict = {}
    if msg.tool_calls:
        result["tool_calls"] = [
            {"name": tc.function.name, "arguments": tc.function.arguments}
            for tc in msg.tool_calls
        ]
    result["messages"] = [AIMessage(content=msg.content or "", tool_calls=msg.tool_calls)]
    return result


def execute_tools_node(state: AgentState) -> dict:
    results = []
    for tc in state.get("tool_calls", []):
        args = json.loads(tc["arguments"]) if isinstance(tc["arguments"], str) else tc["arguments"]
        output = execute_tool_call(tc["name"], args)
        results.append(ToolMessage(content=json.dumps(output, ensure_ascii=False, default=str), tool_call_id=tc.get("name", "")))
    return {"messages": results, "tool_calls": []}


def save_memory_node(state: AgentState) -> dict:
    user_id = state["user_id"]
    for msg in state["messages"]:
        if isinstance(msg, HumanMessage):
            save_turn(user_id, "user", msg.content)
        elif isinstance(msg, AIMessage) and msg.content:
            save_turn(user_id, "assistant", msg.content)
    trim_history(user_id)
    return {}


def should_continue(state: AgentState) -> Literal["tools", "save"]:
    if state.get("tool_calls"):
        return "tools"
    return "save"


def build_agent() -> StateGraph:
    workflow = StateGraph(AgentState)
    workflow.add_node("load_memory", load_memory_node)
    workflow.add_node("llm", call_llm)
    workflow.add_node("tools", execute_tools_node)
    workflow.add_node("save", save_memory_node)
    workflow.set_entry_point("load_memory")
    workflow.add_edge("load_memory", "llm")
    workflow.add_conditional_edges("llm", should_continue, {"tools": "tools", "save": "save"})
    workflow.add_edge("tools", "llm")
    workflow.add_edge("save", END)
    return workflow.compile()


agent_app = build_agent()


def run_agent(user_id: int, user_message: str) -> str:
    result = agent_app.invoke({
        "messages": [HumanMessage(content=user_message)],
        "user_id": user_id,
        "tool_calls": [],
    })
    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage) and msg.content:
            return msg.content
    return "Non ho capito. Puoi ripetere?"
''')

    # ── agent/tools/registry.py ──
    with open(f"{target}/agent/tools/registry.py", "w") as f:
        f.write('''"""Tool registry — functions the agent can call."""

from typing import Any

TOOL_DEFINITIONS = [
    # Add your tool definitions here following OpenAI function calling format
]

TOOL_IMPLEMENTATIONS: dict[str, callable] = {
    # Map tool names to implementation functions
}


def execute_tool_call(tool_name: str, arguments: dict[str, Any]) -> Any:
    """Execute a tool by name with the given arguments."""
    fn = TOOL_IMPLEMENTATIONS.get(tool_name)
    if fn is None:
        return {"error": f"Tool '{tool_name}' not found"}
    try:
        return fn(**arguments)
    except Exception as e:
        return {"error": str(e)}
''')

    # ── db/database.py ──
    with open(f"{target}/db/database.py", "w") as f:
        f.write(f'''"""Database connection and session management."""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./{agent_name}.db")


class Base(DeclarativeBase):
    pass


engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
''')

    # ── db/models/__init__.py ──
    with open(f"{target}/db/models/__init__.py", "w") as f:
        f.write('''"""Database models."""

from db.models.conversation_memory import ConversationMemory

__all__ = ["ConversationMemory"]
''')

    # ── db/models/conversation_memory.py ──
    with open(f"{target}/db/models/conversation_memory.py", "w") as f:
        f.write('''"""Conversation memory model."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class ConversationMemory(Base):
    __tablename__ = "conversation_memory"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
''')

    # ── main.py ──
    if with_telegram:
        with open(f"{target}/main.py", "w") as f:
            f.write(f'''"""Entry point for Telegram bot."""

import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, MessageHandler, filters

from bot.config import TELEGRAM_BOT_TOKEN
from bot.handlers.message_handler import message_handler

load_dotenv()


def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("[AI] Bot avviato in polling mode...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
''')

        # ── bot/config.py ──
        with open(f"{target}/bot/config.py", "w") as f:
            f.write('''"""Bot configuration from environment variables."""

import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_WEBHOOK_URL = os.getenv("TELEGRAM_WEBHOOK_URL", "")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", "0"))
''')

        # ── bot/middleware/auth.py ──
        with open(f"{target}/bot/middleware/auth.py", "w") as f:
            f.write('''"""Authentication middleware — whitelist check."""

from telegram import Update
from telegram.ext import ContextTypes

from bot.config import ALLOWED_USER_ID


async def auth_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Return True if the user is authorized."""
    user_id = update.effective_user.id
    return user_id == ALLOWED_USER_ID
''')

        # ── bot/handlers/message_handler.py ──
        with open(f"{target}/bot/handlers/message_handler.py", "w") as f:
            f.write('''"""Handle non-command messages by forwarding to the agent."""

import asyncio

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ChatAction

from bot.middleware.auth import auth_middleware
from agent.graph import run_agent


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await auth_middleware(update, context):
        return

    user_text = update.message.text.strip()
    if not user_text:
        return

    user_id = update.effective_user.id

    async def keep_typing():
        while True:
            try:
                await context.bot.send_chat_action(
                    chat_id=update.effective_chat.id, action=ChatAction.TYPING)
                await asyncio.sleep(4)
            except Exception:
                break

    typing_task = asyncio.create_task(keep_typing())

    response = None
    while response is None:
        try:
            response = await asyncio.to_thread(run_agent, user_id, user_text)
        except Exception:
            await asyncio.sleep(2)

    typing_task.cancel()

    try:
        await update.message.reply_text(response, parse_mode='Markdown')
    except Exception:
        await update.message.reply_text(response)
''')

    # ── cli.py ──
    with open(f"{target}/cli.py", "w") as f:
        f.write(f'''"""CLI chat interface for {agent_name}."""

import os

from dotenv import load_dotenv

load_dotenv()

DEFAULT_USER_ID = 1


def run_cli():
    from agent.graph import run_agent

    print()
    print("=" * 50)
    print(f"  [AI]  {agent_name}")
    print("=" * 50)
    print("  /quit    — Esci")
    print("=" * 50)
    print()

    while True:
        try:
            user_input = input("[Tu] Tu > ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not user_input:
            continue
        if user_input.lower() == "/quit":
            break

        response = run_agent(DEFAULT_USER_ID, user_input)
        print(f"[AI] {agent_name} > {{response}}")
        print()


if __name__ == "__main__":
    run_cli()
''')

    # ── .env.example ──
    with open(f"{target}/.env.example", "w") as f:
        f.write(f'''# {agent_name} — Environment Variables

# Telegram (required only if using --telegram)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_WEBHOOK_URL=
ALLOWED_USER_ID=your_telegram_user_id

# OpenRouter
OPENROUTER_API_KEY=sk-or-v1-your-key-here
DEFAULT_MODEL=google/gemini-2.5-flash

# Database
DATABASE_URL=sqlite:///./{agent_name}.db
''')

    # ── requirements.txt ──
    with open(f"{target}/requirements.txt", "w") as f:
        f.write('''langgraph>=0.4.0
langchain-core>=0.3.0
openai>=1.0.0
sqlalchemy>=2.0.0
python-telegram-bot>=21.0
alembic>=1.13.0
python-dotenv>=1.0.0
''')

    # ── tests/test_agent.py ──
    with open(f"{target}/tests/test_agent.py", "w") as f:
        f.write('''"""Basic tests for the agent graph."""

from agent.graph import build_agent


class TestAgentGraph:
    def test_build_agent_returns_compiled_graph(self):
        graph = build_agent()
        assert graph is not None
        assert hasattr(graph, "invoke")
''')

    print(f"[OK] Progetto '{agent_name}' creato in {target}")
    print(f"\nProssimi passi:")
    print(f"  cd {agent_name}")
    print(f"  pip install -r requirements.txt")
    print(f"  cp .env.example .env  # e modifica con le tue chiavi")
    if with_telegram:
        print(f"  python main.py")
    else:
        print(f"  python cli.py")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold a new AI agent project")
    parser.add_argument("agent_name", help="Name of the agent project")
    parser.add_argument("--telegram", action="store_true", help="Include Telegram bot integration")
    parser.add_argument("--db", choices=["sqlite", "postgres"], default="sqlite", help="Database type")
    args = parser.parse_args()
    scaffold(args.agent_name, args.telegram, args.db)