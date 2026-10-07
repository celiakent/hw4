# Campus Customs

A customer storefront with a helpful shopping chatbot for **Campus Customs — Yale Bulldog Blue**,
built for HW4.

- **Frontend:** React + Vite + TypeScript — a minimal, editorial storefront (browse products,
  filter/sort, single-item pages, create account / log in, and a floating liquid-glass chat).
- **Backend:** Python FastAPI whose brain is a **PydanticAI** agent. The agent answers honestly
  about price and stock from a local SQLite database, and matching products appear on the page.

The agent itself is four files under `backend/`: `prompts/prompt.md` (system prompt + safety
rules), `agent.py` (wiring: model + prompt + tools), `tools.py` (database lookups), and
`models.py` (Pydantic types).

## What's in this repo

```
AI_prompts.md          # the prompts used to build this, by problem
requirements.txt       # Python dependencies
.env.example           # template for the Portkey key (copy to .env)
.gitignore
README.md
frontend/              # Vite React TypeScript app
backend/
  main.py              # FastAPI app — run with uvicorn
  agent.py             # PydanticAI agent wiring
  models.py            # Pydantic models
  tools.py             # agent tools (product/price/stock lookups)
  auth.py  db.py  images.py   # auth, db access, image normalization
  prompts/prompt.md    # system prompt + safety rules
output/                # harness.md, design.md, usability.md, app_check.html,
                       # app_check_images/, audit_trail.json
```

The database and product images are **not** in the repo. Add them locally (see below).

## 1. Add the local data pack

Place the provided data so the folder looks like this (relative to the repo root):

```
data/
  campus_customs.db          # SQLite database
  products/                  # product images referenced by the catalogue
```

If you have `data.zip`, unzip it in the repo root so you get `data/campus_customs.db` and
`data/products/`.

## 2. Add your Portkey API key

The chatbot calls an OpenAI model through the Portkey gateway. Copy the template and add your key:

```bash
cp .env.example .env
```

Then edit `.env` and set `PORTKEY_API_KEY=...` (optionally `AGENT_MODEL`, a Portkey virtual key,
or config). `.env` is gitignored. The backend reads `.env` from the repo root or from `backend/`.

## 3. Run the backend (FastAPI)

From the repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd backend
uvicorn main:app --reload --port 8000
```

The API serves products and images and exposes `POST /api/chat`. On first start it normalizes the
product photos onto white backgrounds (cached under `data/.products_white/`).

## 4. Run the frontend (Vite + React)

In a second terminal, from the repo root:

```bash
cd frontend
npm install
npm run dev
```

Open the printed URL (http://localhost:5173). The dev server proxies `/api` and `/images` to the
backend on port 8000, so start the backend first.

## Notes

- Requires Python 3.10+ (developed on 3.12) and Node 18+.
- A seed test account ships in the database: `test@campuscustoms.yale.edu` / `password`.
- `output/harness.md` documents the full system (data, auth, agent, tools, safety, specs).
