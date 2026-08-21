# AI Agent Builder — Architecture Reference

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      Telegram Bot                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ /start, /help │  │  Message     │  │  Auth Middleware  │  │
│  │  Command      │  │  Handler     │  │  (whitelist)     │  │
│  │  Handler      │  │              │  │                  │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────────────┘  │
│         │                 │                                  │
└─────────┼─────────────────┼──────────────────────────────────┘
          │                 │
          ▼                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph Agent                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  load_memory  │→│    call_llm   │→│  execute_tools    │  │
│  │  (DB → ctx)  │  │  (OpenRouter) │  │  (tool registry) │  │
│  └──────────────┘  └──────┬───────┘  └────────┬─────────┘  │
│                           │                    │             │
│                           ▼                    │             │
│                    ┌──────────────┐            │             │
│                    │  save_memory  │←───────────┘             │
│                    │  (ctx → DB)  │                          │
│                    └──────────────┘                          │
└─────────────────────────────────────────────────────────────┘
          │                                         │
          ▼                                         ▼
┌──────────────────┐                    ┌──────────────────┐
│   OpenRouter API  │                    │   SQLite/Postgres │
│   (LLM models)    │                    │   (persistence)   │
└──────────────────┘                    └──────────────────┘
```

## Data Flow

1. **User sends message** → Telegram webhook/polling
2. **Auth middleware** → checks whitelist (ALLOWED_USER_ID)
3. **Message handler** → typing indicator ON → calls `run_agent()`
4. **load_memory** → loads last N turns from DB
5. **call_llm** → sends system prompt + history + user message to OpenRouter
6. **LLM responds** → may include tool calls
7. **execute_tools** → runs each tool, returns results to LLM
8. **LLM responds again** (with tool results) → may call more tools
9. **save_memory** → saves user message + assistant response to DB
10. **Message handler** → typing indicator OFF → sends response to Telegram

## Key Files

| File                              | Responsibility                            |
| --------------------------------- | ----------------------------------------- |
| `agent/graph.py`                  | LangGraph state machine, node definitions |
| `agent/memory.py`                 | DB read/write for conversation history    |
| `agent/prompts/persona.py`        | System prompt with personality            |
| `agent/tools/registry.py`         | Tool definitions + implementations        |
| `bot/handlers/message_handler.py` | Telegram message → agent bridge           |
| `bot/handlers/command_handler.py` | /start, /help, /setmodel, etc.            |
| `bot/middleware/auth.py`          | User whitelist check                      |
| `services/*.py`                   | Business logic for each tool              |
| `db/database.py`                  | SQLAlchemy engine + session               |
| `db/models/*.py`                  | ORM models                                |
| `main.py`                         | Entry point                               |
