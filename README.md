# Sole Syntax AI Customer Support Agent

An AI-powered customer support agent for **Sole Syntax**, a shoe e-commerce brand. The agent handles refund and return requests by dynamically calling tools to validate policy rules, look up customer records, and process or deny refunds — all in real time.

## Features

- **Conversational refund handling** — customers describe their issue in plain language
- **Policy enforcement** — agent strictly applies Sole Syntax's refund policy (return windows, worn items, final sale, defects, loyalty tiers)
- **Live reasoning steps** — every tool call is shown as a collapsible step in the chat UI
- **Voice interface** — speak requests via browser microphone; agent responses read aloud (Web Speech API, no API key required)
- **Terminal reasoning logs** — colorized, structured agent trace printed to terminal during every session

## Tech Stack

| Layer | Technology |
|---|---|
| Agent framework | [LangGraph](https://github.com/langchain-ai/langgraph) (ReAct loop) |
| LLM | [OpenRouter](https://openrouter.ai) — `openai/gpt-oss-120b:free` |
| Chat UI | [Chainlit](https://chainlit.io) |
| Database | SQLite via SQLAlchemy (15 mock customers + orders) |
| Voice | Browser Web Speech API (STT + TTS, zero cost) |
| Terminal logs | [Rich](https://github.com/Textualize/rich) |
| Python env | [uv](https://github.com/astral-sh/uv) |

## Project Structure

```
ai-cs-agent-langgraph/
├── app.py                  # Chainlit entry point
├── agent/
│   ├── graph.py            # LangGraph ReAct graph
│   ├── state.py            # Shared state TypedDict
│   ├── prompts.py          # Agent system prompt
│   └── tracer.py           # Rich terminal reasoning logger
├── tools/
│   ├── crm_tools.py        # lookup_customer, get_order_details
│   ├── policy_tools.py     # check_refund_eligibility
│   └── refund_tools.py     # process_refund, deny_refund, escalate_to_human
├── data/
│   ├── seed_db.py          # Database seed script
│   ├── sole_syntax.db      # SQLite CRM (auto-generated)
│   └── refund_policy.md    # Sole Syntax refund policy document
└── public/
    └── voice.js            # Web Speech API integration
```

## Getting Started

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- An [OpenRouter](https://openrouter.ai) API key (free account)

### Installation

```bash
cd ai-cs-agent-langgraph

# Install dependencies
uv sync

# Seed the database
uv run python data/seed_db.py
```

### Configuration

Create a `.env` file in the project root:

```
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### Run

```bash
chainlit run app.py
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

## Usage

Start a conversation by providing your name and order ID. Example:

> "Hi, I'm Alice Johnson. I'd like to return my order ORD-001."

The agent will look up your account, retrieve the order, check the refund policy, and either approve or deny the request — explaining the exact policy rule that applies.

For voice input, click the **🎤 floating button** (bottom-right). Your spoken request is transcribed and submitted automatically. The agent's response is also read aloud.

## How It Works

1. User message arrives via Chainlit
2. LangGraph routes to the **agent node** — the LLM decides which tool to call
3. **Tools node** executes the tool (SQLite query or policy check)
4. Results flow back to the agent; it reasons again and calls the next tool
5. Once the agent has enough information, it generates a final response
6. The terminal prints a structured reasoning trace for every session

