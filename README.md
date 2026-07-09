# Daily Diet Agent

An AI agent built with the Anthropic API that manages meal tracking through natural language conversation. Instead of calling REST endpoints directly, the agent uses **tool use** to reason about user requests, decide which action to take, and execute real HTTP calls against a Flask API.

This project was built to explore how LLM-powered agents can act as a natural language interface on top of an existing backend — a pattern increasingly used in production AI systems.

## How it works

1. The user sends a message in plain language (e.g. *"Log that I had chicken and rice for lunch at 12:30, it was on my diet"*)
2. Claude decides whether a tool call is needed and which one fits the request
3. The agent executes a real HTTP request (`GET`/`POST`/`PUT`/`DELETE`) against the [`daily-diet-api`](https://github.com/bexteee/daily-diet-api)
4. The result is sent back to Claude, which formats a natural language response
5. The conversation continues in a loop, keeping full context across turns

User (terminal) → Claude (tool selection) → execute_tool() → daily-diet-api (Flask) → SQLite
↑__________________________________________________|
tool_result feeds back into the conversation

## Features

- **Conversational REPL** — persistent terminal chat, not a single-shot script
- **5 tools mapped to REST endpoints**: create, read (single), read (all), update, and delete meals
- **Real HTTP integration** — no mocked logic; every tool call hits a live Flask API
- **Structured error handling** — HTTP status codes are checked and surfaced back to Claude, so it can explain failures (e.g. missing fields) instead of crashing
- **Context-aware** — the agent remembers prior turns, so follow-up requests referencing earlier results work correctly

## Tech Stack

- Python 3.11
- [Anthropic SDK](https://github.com/anthropics/anthropic-sdk-python) (Claude, tool use)
- `requests` for HTTP calls
- `python-dotenv` for environment configuration

## Project Structure

daily-diet-agent/
├── agent.py          # main loop: conversation + tool use + execution
├── requirements.txt
├── .env.example
└── .gitignore

## Setup

This agent requires [`daily-diet-api`](https://github.com/bexteee/daily-diet-api) running locally.

```bash
# 1. Clone this repo
git clone https://github.com/bexteee/daily-diet-agent.git
cd daily-diet-agent

# 2. Create a virtual environment and install dependencies
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# add your ANTHROPIC_API_KEY and DIET_API_BASE_URL in .env

# 4. Make sure daily-diet-api is running in a separate terminal
# 5. Run the agent
python agent.py
```

## Example Usage

Você: Registra que eu almocei arroz com frango às 12:30 hoje, tava na dieta
Claude: Refeição registrada com sucesso! 🎉
Você: Lista minhas refeições
Claude: Aqui está sua lista de refeições:

Almoço (ID: 5) — Arroz com frango — Dentro da dieta ✅
...

Você: sair

## Notes on the API's data format

The underlying API uses a non-standard datetime format (`YYYY-DD-MM HH:MM:SS`, day before month) and represents diet compliance as the strings `"yes"`/`"no"` rather than a native boolean. These quirks are documented in each tool's `input_schema` description so Claude handles them correctly without additional prompting.

## What I learned

- Designing JSON Schemas (`input_schema`) that accurately constrain and describe an LLM's tool inputs
- Structuring an agent loop that separates "one turn" logic from "the whole conversation"
- Handling the boundary between an LLM-facing tool layer and a real backend API (status codes, error propagation, path vs. body parameters)

## Related Project

- [`daily-diet-api`](https://github.com/bexteee/daily-diet-api) — the Flask + SQLAlchemy backend this agent operates on