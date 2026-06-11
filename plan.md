# Sole Syntax AI Customer Support Agent — Build Plan

## Directory Structure
```
ai-cs-agent-langgraph/
├── pyproject.toml
├── .env                    # GEMINI_API_KEY
├── .env.example
├── .gitignore
├── app.py                  # Chainlit entry point
├── agent/
│   ├── graph.py            # LangGraph state machine
│   ├── state.py            # TypedDict state
│   └── prompts.py          # System prompt
├── tools/
│   ├── crm_tools.py        # lookup_customer, get_order_details
│   ├── policy_tools.py     # check_refund_eligibility
│   └── refund_tools.py     # process_refund, deny_refund, escalate
├── data/
│   ├── seed_db.py          # Creates + seeds sole_syntax.db
│   ├── sole_syntax.db      # SQLite CRM (15 customers, orders)
│   └── refund_policy.md    # Sole Syntax strict policy doc
└── public/
    └── voice.js            # Web Speech API (STT + TTS, free)
```

## Stack
| Layer | Tech |
|---|---|
| LLM | Gemini 2.0 Flash (free, 1500 req/day) |
| Agent | LangGraph ReAct loop |
| UI | Chainlit (chat + reasoning steps + voice) |
| DB | SQLite via SQLAlchemy |
| Voice | Browser Web Speech API — zero cost, zero setup |

## LangGraph Agent
- **State**: `messages`, `customer_info`, `order_details`, `refund_decision`, `reasoning_log`
- **Nodes**: `agent` (Gemini reasons) → `tools` (execute) → loops back or `END`
- **Tools**:
  - `lookup_customer(email)` — CRM search
  - `get_order_details(order_id)` — fetch order
  - `check_refund_eligibility(order_id)` — validates against policy
  - `process_refund(order_id, reason)` — approve
  - `deny_refund(order_id, reason)` — deny with explanation
  - `escalate_to_human(reason)` — edge cases

## CRM Mock Data (15 customers)
Scenarios pre-seeded for demo:
- Customer A: valid refund (within 30 days, unworn) → **approves**
- Customer B: worn shoes, 45 days old → **denies** (policy violation)
- Customer C: missing receipt → **denies**
- Others: mix of loyalty tiers, order statuses, edge cases

## Refund Policy (Sole Syntax)
- 30-day return window from delivery
- Shoes must be unworn, in original box
- Receipt/order ID required
- Sale items: final sale, no returns
- Defective items: up to 90 days
- Loyalty Gold members: extended 45-day window

## UI (Chainlit)
- **Chat panel**: customer types (or speaks) → agent responds with decision
- **Reasoning steps**: Chainlit `cl.Step` shows each tool call + result live
- **Voice**: microphone button via `public/voice.js` using `webkitSpeechRecognition` (STT) + `speechSynthesis` (TTS) — no API key needed
- **Admin view**: all tool calls + reasoning visible as collapsible steps in the same chat

## Demo Flow
1. Standard refund → agent approves, shows tool call trace
2. Policy violation → agent denies firmly with specific reason
3. Voice mode → speak a request, agent responds via TTS

## Setup Commands (in order)
```bash
uv init
uv add langgraph langchain-google-genai langchain-core chainlit sqlalchemy python-dotenv pydantic
uv run python data/seed_db.py   # seed database
chainlit run app.py              # launch
```

## Build Order
1. `data/refund_policy.md` + `data/seed_db.py` → generate `sole_syntax.db`
2. `agent/state.py` → TypedDict state definition
3. `agent/prompts.py` → system prompt
4. `tools/` → all 5 tools wired to SQLite
5. `agent/graph.py` → LangGraph ReAct graph
6. `app.py` → Chainlit app with streaming + cl.Step reasoning display
7. `public/voice.js` → Web Speech API integration
