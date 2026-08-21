---
name: ai-agent-builder
version: 2.0.0
author: Mirko Bechini
description: "Guida completa alla creazione di agenti AI conversazionali con personalità, memoria persistente e interfaccia Telegram. Copre architettura LangGraph, system prompt design, tool registry, database SQLite/PostgreSQL, e deploy locale. Attivare quando si deve costruire un agente AI da zero o aggiungere funzionalità a un agente esistente."
argument-hint: "[agent-name] [--telegram] [--db sqlite|postgres]"
user-invocable: true
applyTo: "**"
---

# AI Agent Builder

## Quick Start

Crea un agente in 3 comandi:

```bash
# 1. Scaffold del progetto
python scripts/scaffold.py my-agent --telegram --db sqlite

# 2. Installa dipendenze
cd my-agent
pip install -r requirements.txt

# 3. Configura .env e avvia
cp .env.example .env
# Modifica .env con le tue chiavi
python main.py
```

## When to Use

Attiva questa skill quando:

- Devi **costruire un agente AI conversazionale da zero** con personalità e memoria
- Vuoi aggiungere **strumenti (tools)** che l'agente può chiamare autonomamente
- Devi **collegare un bot Telegram** a un agente LangGraph
- L'agente **non risponde**, **si ripete**, o **perde il contesto** della conversazione
- Devi **salvare/recuperare dati** (profilo utente, misure corporee, check-in, sessioni)
- Vuoi **debuggare** perché l'agente si comporta come un programma invece che come un agente

## Output

Questa skill produce:

1. **Architettura completa** — LangGraph + LLM (OpenRouter) + DB + Telegram
2. **System prompt** — Regole per personalità, formato risposta, strumenti, ortografia
3. **Tool registry** — Definizione e implementazione degli strumenti che l'agente può chiamare
4. **Servizi** — Business logic per salvare/recuperare dati (profilo, misure, check-in, sessioni)
5. **Bot Telegram** — Handler per messaggi e comandi con typing indicator e retry
6. **Memoria persistente** — Caricamento e salvataggio della cronologia conversazione

## Architettura di Riferimento

```
progetto/
├── agent/
│   ├── graph.py              ← State machine LangGraph (nodi, archi, loop)
│   ├── memory.py             ← Caricamento/salvataggio cronologia DB
│   ├── prompts/
│   │   └── persona.py        ← System prompt con personalità
│   └── tools/
│       └── registry.py       ← Definizioni e implementazioni tool
├── bot/
│   ├── config.py             ← Variabili d'ambiente (token, webhook)
│   ├── handlers/
│   │   ├── command_handler.py  ← /start, /help, ecc.
│   │   └── message_handler.py  ← Messaggi liberi → agente
│   └── middleware/
│       └── auth.py           ← Whitelist user ID
├── db/
│   ├── database.py           ← Engine SQLAlchemy + session
│   └── models/               ← Modelli ORM
├── services/                 ← Business logic
├── tests/                    ← Test con SQLite :memory:
├── main.py                   ← Entry point bot Telegram
├── cli.py                    ← Entry point CLI (opzionale)
├── .env.example              ← Template variabili d'ambiente
├── alembic.ini               ← Config migrazioni DB
└── requirements.txt
```

## Prerequisiti

### Required

- **Python** 3.11+ — Linguaggio runtime
- **OpenRouter API key** — Accesso ai modelli LLM (https://openrouter.ai/keys)
- **Telegram Bot Token** — Da @BotFather su Telegram
- **SQLite** — Database locale (built-in in Python)

### Installazione

```bash
pip install langgraph langchain-core openai sqlalchemy python-telegram-bot alembic python-dotenv
```

### Variabili d'ambiente (.env)

```
TELEGRAM_BOT_TOKEN=il_tuo_token
TELEGRAM_WEBHOOK_URL=  # Vuoto per polling locale
ALLOWED_USER_ID=il_tuo_telegram_id
OPENROUTER_API_KEY=sk-or-v1-...
DEFAULT_MODEL=google/gemini-2.5-flash
DATABASE_URL=sqlite:///./agent.db
```

## Procedure

### Step 1: Progettare il System Prompt

Il system prompt è il cuore della personalità dell'agente. Deve contenere:

1. **Identità** — Chi è l'agente, cosa ha fatto, cosa sa fare
2. **Personalità** — Tono, stile, atteggiamento (diretto, burbero, motivazionale, ecc.)
3. **Regole di comportamento** — Cosa fare/non fare in situazioni specifiche
4. **Conoscenze** — Cosa l'agente sa (anatomia, nutrizione, programmazione, ecc.)
5. **Strumenti a disposizione** — Lista aggiornata di ciò che può chiamare
6. **Formato risposta** — Come deve rispondere (italiano, accenti, formattazione)
7. **Regole anti-ripetizione** — Istruzioni per non ripetere concetti già detti

**Regola critica**: La lista degli strumenti nel system prompt DEVE corrispondere ESATTAMENTE ai tool definiti nel registry. Se c'è disallineamento, l'agente chiamerà tool inesistenti e otterrà errori.

**Template generico:**

```python
AGENT_SYSTEM_PROMPT = """Sei {NOME_AGENTE}, {DESCRIZIONE_BREVE}.

## Personalità
- {TRATTO_1}
- {TRATTO_2}
- {TRATTO_3}

## Regole di comportamento
1. {REGOLA_1}
2. {REGOLA_2}
3. {REGOLA_3}

## Conoscenze
- {CONOSCENZA_1}
- {CONOSCENZA_2}

## Strumenti a disposizione
- {tool_name(param)}: {descrizione}
- {tool_name(param)}: {descrizione}

## Formato risposta
{ISTRUZIONI_FORMATO}

## Regola importante: non ripeterti
Quando riprendi un discorso interrotto, NON ripetere concetti già detti in precedenza.
Vai dritto al punto.
"""
```

### Step 2: Implementare il Tool Registry

Il registry ha due parti: **definizioni** (in formato OpenAI function calling) e **implementazioni** (funzioni Python reali).

**Struttura tool definition:**

```python
{
    "type": "function",
    "function": {
        "name": "save_measurement",
        "description": "Salva le misure corporee dell'allievo",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {"type": "integer", "description": "ID utente Telegram"},
                "weight_kg": {"type": "number", "description": "Peso in kg"},
            },
            "required": ["user_id"],
        },
    },
}
```

**Struttura implementazione:**

```python
TOOL_IMPLEMENTATIONS: dict[str, callable] = {
    "save_measurement": lambda user_id, **kwargs: save_measurement(user_id, **kwargs),
    "get_profile": lambda user_id: get_profile(user_id),
}
```

**Errori comuni:**

- `"name"` nel tool non corrisponde alla chiave in `TOOL_IMPLEMENTATIONS` → l'agente chiama un tool che non esiste
- Parametri richiesti (`required`) non passati all'implementazione → crash
- System prompt elenca tool che non sono nel registry → l'agente prova a chiamarli e fallisce

### Step 3: Costruire il Grafo LangGraph

Il grafo definisce il flusso: carica memoria → chiama LLM → esegue tool → salva → fine.

```python
from langgraph.graph import END, StateGraph

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
```

**Nodi chiave:**

- `load_memory_node` — Carica la cronologia dal DB e la passa all'LLM
- `call_llm` — Chiama OpenRouter con messaggi + tool definitions
- `execute_tools_node` — Esegue i tool chiamati dall'LLM e restituisce i risultati
- `save_memory_node` — Salva la conversazione nel DB

### Step 4: Gestire la Memoria

La memoria deve:

1. **Salvare ogni turno** (user + assistant) nel DB
2. **Caricare gli ultimi N turni** all'inizio di ogni conversazione
3. **Non ripetere** i messaggi vecchi all'LLM (usa un limite ragionevole)

```python
MAX_HISTORY_TURNS = 20  # Ultimi N turni da caricare

def load_memory(user_id: int) -> list[dict]:
    session = SessionLocal()
    try:
        stmt = select(ConversationMemory).where(
            ConversationMemory.user_id == user_id
        ).order_by(ConversationMemory.created_at.desc()).limit(MAX_HISTORY_TURNS)
        rows = session.execute(stmt).scalars().all()
        rows.reverse()
        return [{"role": r.role, "content": r.content} for r in rows]
    finally:
        session.close()
```

**⚠️ Lezione appresa**: Se copi messaggi da una vecchia chat (es. CLI → Telegram), fallo in ordine cronologico e con i timestamp corretti. Altrimenti l'agente si confonde e ripete concetti.

### Step 5: Collegare Telegram

Il bot Telegram deve:

1. **Mostrare il typing indicator** (`...`) mentre l'agente pensa — e mantenerlo attivo finché non arriva la risposta
2. **Riprova automaticamente** se l'agente crasha (errore API, timeout)
3. **Inviare con parse_mode='Markdown'** per formattazione grassetto/corsivo
4. **Fallback a testo normale** se il markdown è invalido

```python
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Auth check
    if not await auth_middleware(update, context):
        return

    user_text = update.message.text.strip()
    user_id = update.effective_user.id

    # Typing indicator infinito
    async def keep_typing():
        while True:
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id, action=ChatAction.TYPING)
            await asyncio.sleep(4)

    typing_task = asyncio.create_task(keep_typing())

    # Retry infinito
    response = None
    while response is None:
        try:
            response = await asyncio.to_thread(run_agent, user_id, user_text)
        except Exception:
            await asyncio.sleep(2)

    typing_task.cancel()

    # Markdown con fallback
    try:
        await update.message.reply_text(response, parse_mode='Markdown')
    except Exception:
        await update.message.reply_text(response)
```

### Step 6: Implementare i Servizi

Ogni tool deve avere un servizio corrispondente. Pattern standard:

```python
def save_measurement(user_id: int, weight_kg: float = None, **kwargs) -> dict:
    session = SessionLocal()
    try:
        stmt = select(UserProfile).where(UserProfile.telegram_id == user_id)
        profile = session.execute(stmt).scalar_one_or_none()
        if profile is None:
            raise ValueError("User not found")

        record = BodyMeasurement(user_id=profile.id, measurement_date=date.today(), weight_kg=weight_kg, **kwargs)
        session.add(record)
        session.commit()
        return {"id": record.id, "date": record.measurement_date.isoformat()}
    finally:
        session.close()
```

**Pattern obbligatorio**: `try/finally` con `session.close()` per evitare connessioni aperte.

### Step 7: Testare

Usa SQLite `:memory:` per i test. Monkeypatch `SessionLocal` per iniettare la sessione di test.

```python
@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    s = TestSession()
    yield s
    s.close()

def test_save_measurement(self, session, monkeypatch):
    monkeypatch.setattr("services.tracking_service.SessionLocal", lambda: session)
    result = save_measurement(user_id=1, weight_kg=75.0)
    assert result["id"] is not None
```

## Errori Comuni e Soluzioni

| Problema                               | Causa                                      | Soluzione                                                     |
| -------------------------------------- | ------------------------------------------ | ------------------------------------------------------------- |
| L'agente si ripete                     | Troppi messaggi vecchi caricati            | Ridurre `MAX_HISTORY_TURNS` o compattare la cronologia        |
| L'agente non risponde                  | Errore API OpenRouter o crash              | Aggiungere retry loop + typing indicator infinito             |
| I grassetti non si vedono              | `parse_mode` non impostato                 | Usare `parse_mode='Markdown'` con fallback                    |
| Tool non trovato                       | Nome nel system prompt ≠ nome nel registry | Sincronizzare le due liste                                    |
| "table already exists"                 | DB già popolato senza stamp Alembic        | Usare `alembic stamp head` se le tabelle esistono già         |
| `/start` sovrascrive il nome           | Forzatura dello step "name"                | Controllare lo step reale prima di processare                 |
| Accenti mancanti (e vs è)              | Il modello non è istruito                  | Aggiungere regola ortografica nel system prompt               |
| Conversazione persa tra CLI e Telegram | user_id diverso                            | Copiare i messaggi con lo stesso user_id di Telegram          |
| L'agente sembra un programma           | Gate onboarding che blocca i messaggi      | Rimuovere il gate — ogni messaggio va direttamente all'agente |
| Typing indicator scompare              | Inviato una sola volta                     | Inviare ogni 4 secondi finché l'agente non risponde           |

## Script di Supporto

### `scripts/scaffold.py`

Genera la struttura completa del progetto per un nuovo agente.

```bash
python scripts/scaffold.py nome-agente [--telegram] [--db sqlite|postgres]
```

Crea:

- Struttura directory completa
- `agent/prompts/persona.py` con template system prompt
- `agent/graph.py` con grafo LangGraph base
- `agent/tools/registry.py` con tool definitions vuote
- `agent/memory.py` con load/save memoria
- `bot/` handlers (se `--telegram`)
- `db/database.py` + modelli base
- `main.py` / `cli.py`
- `.env.example`, `requirements.txt`, `alembic.ini`

### `scripts/compact_history.py`

Compatta la cronologia di un utente in un unico riassunto quando supera N turni.

```bash
python scripts/compact_history.py <user_id> [--max-turns N] [--db DATABASE_URL]
```

### `scripts/migrate_user.py`

Copia la cronologia da un user_id a un altro (utile per migrare da CLI a Telegram).

```bash
python scripts/migrate_user.py <source_id> <target_id> [--db DATABASE_URL]
```

## Riferimenti

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [python-telegram-bot Documentation](https://python-telegram-bot.org/)
- [OpenRouter API Reference](https://openrouter.ai/docs)
- [SQLAlchemy ORM Guide](https://docs.sqlalchemy.org/en/latest/orm/)

### `scripts/compact_history.py`

Compatta la cronologia di un utente in un unico riassunto quando supera N turni.

### `scripts/migrate_user.py`

Copia la cronologia da un user_id a un altro (utile per migrare da CLI a Telegram).

## Riferimenti

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [python-telegram-bot Documentation](https://python-telegram-bot.org/)
- [OpenRouter API Reference](https://openrouter.ai/docs)
- [SQLAlchemy ORM Guide](https://docs.sqlalchemy.org/en/latest/orm/)
