"""Campus Customs API.

For now this serves the product catalogue, per-size stock, and product images
from data/campus_customs.db. It will grow into the agent backend later.
"""

import json
import logging
import secrets
import sqlite3

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, field_validator

from agent import ChatDeps, MissingAPIKey, run_chat
from audit import append_entry, extract_tool_calls
from auth import hash_password, verify_password
from db import DATA_DIR, SIZE_ORDER, get_db, row_to_card
from models import (
    ChatHistoryMessage,
    ChatHistoryResponse,
    ChatRequest,
    ChatResponse,
    ProductCard,
)

# In-memory session store: token -> user id. Fine for this assignment; a real
# deployment would use signed cookies or a persistent session table.
SESSIONS: dict[str, int] = {}

app = FastAPI(title="Campus Customs API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Image paths in the catalogue are relative to data/ (e.g. "products/x.jpg").
# We serve white-background copies (built at startup) so the grid is clean on white;
# falls back to the originals if that can't be built.
from images import serve_dir  # noqa: E402

app.mount("/images/products", StaticFiles(directory=serve_dir()), name="product-images")


class SizeStock(BaseModel):
    size: str
    quantity: int


class Product(BaseModel):
    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str]
    search_tags: list[str]
    image_url: str
    price: float
    total_stock: int = 0  # summed across sizes; drives the card stock badge
    in_stock: bool = True


class ProductDetail(Product):
    sizes: list[SizeStock]


class SignupRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

    @field_validator("first_name", "last_name")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("This field is required.")
        return v.strip()

    @field_validator("password")
    @classmethod
    def strong_enough(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class PublicUser(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str


class AuthResponse(BaseModel):
    token: str
    user: PublicUser


def row_to_product(row: sqlite3.Row, total_stock: int = 0) -> Product:
    return Product(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        description=row["description"],
        colors=json.loads(row["colors"]),
        search_tags=json.loads(row["search_tags"]),
        image_url=f"/images/{row['image_file_path']}",
        price=row["price"],
        total_stock=total_stock,
        in_stock=total_stock > 0,
    )


def public_user(row: sqlite3.Row) -> PublicUser:
    # Fall back to splitting `name` for any legacy row missing first/last.
    first = row["first_name"]
    last = row["last_name"]
    if not first and not last and row["name"]:
        parts = row["name"].split(" ", 1)
        first = parts[0]
        last = parts[1] if len(parts) > 1 else ""
    return PublicUser(id=row["id"], first_name=first or "", last_name=last or "", email=row["email"])


def optional_user(authorization: str | None = Header(default=None)) -> PublicUser | None:
    """Return the signed-in user if a valid token is present, else None (guest)."""
    token = ""
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:]
    user_id = SESSIONS.get(token)
    if user_id is None:
        return None
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return public_user(row) if row is not None else None


def current_user(authorization: str | None = Header(default=None)) -> PublicUser:
    user = optional_user(authorization)
    if user is None:
        raise HTTPException(status_code=401, detail="Not signed in.")
    return user


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/auth/signup", response_model=AuthResponse, status_code=201)
def signup(req: SignupRequest) -> AuthResponse:
    email = req.email.lower()
    with get_db() as conn:
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing is not None:
            raise HTTPException(status_code=409, detail="An account with this email already exists.")
        cur = conn.execute(
            """INSERT INTO users (name, email, password_hash, first_name, last_name)
               VALUES (?, ?, ?, ?, ?)""",
            (
                f"{req.first_name} {req.last_name}",
                email,
                hash_password(req.password),
                req.first_name,
                req.last_name,
            ),
        )
        conn.commit()
        row = conn.execute("SELECT * FROM users WHERE id = ?", (cur.lastrowid,)).fetchone()

    user = public_user(row)
    token = secrets.token_urlsafe(32)
    SESSIONS[token] = user.id
    return AuthResponse(token=token, user=user)


@app.post("/api/auth/login", response_model=AuthResponse)
def login(req: LoginRequest) -> AuthResponse:
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (req.email.lower(),)).fetchone()
    # Verify even when the user is missing is unnecessary here; a generic message
    # avoids revealing which emails are registered.
    if row is None or not verify_password(req.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")

    user = public_user(row)
    token = secrets.token_urlsafe(32)
    SESSIONS[token] = user.id
    return AuthResponse(token=token, user=user)


@app.post("/api/auth/logout", status_code=204)
def logout(authorization: str | None = Header(default=None)) -> None:
    if authorization and authorization.lower().startswith("bearer "):
        SESSIONS.pop(authorization[7:], None)


@app.get("/api/auth/me", response_model=PublicUser)
def me(user: PublicUser = Depends(current_user)) -> PublicUser:
    return user


@app.get("/api/products", response_model=list[Product])
def list_products() -> list[Product]:
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
        totals = {
            r["product_id"]: r["total"]
            for r in conn.execute(
                "SELECT product_id, SUM(quantity) AS total FROM inventory GROUP BY product_id"
            ).fetchall()
        }
    return [row_to_product(r, totals.get(r["product_id"], 0)) for r in rows]


@app.get("/api/products/{product_id}", response_model=ProductDetail)
def get_product(product_id: str) -> ProductDetail:
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Product not found")
        stock = conn.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)
        ).fetchall()

    sizes = sorted(
        (SizeStock(size=s["size"], quantity=s["quantity"]) for s in stock),
        key=lambda s: SIZE_ORDER.index(s.size) if s.size in SIZE_ORDER else len(SIZE_ORDER),
    )
    total_stock = sum(s.quantity for s in sizes)
    return ProductDetail(**row_to_product(row, total_stock).model_dump(), sizes=sizes)


def cards_from_ids(product_ids: list[str]) -> list[ProductCard]:
    """Turn the product_ids the agent chose into full cards, preserving its order."""
    if not product_ids:
        return []
    placeholders = ",".join("?" for _ in product_ids)
    with get_db() as conn:
        rows = conn.execute(
            f"SELECT * FROM catalogue WHERE product_id IN ({placeholders})", product_ids
        ).fetchall()
    by_id = {r["product_id"]: r for r in rows}
    return [row_to_card(by_id[pid]) for pid in product_ids if pid in by_id]


def build_page_context(current_product_id: str | None) -> str | None:
    """Describe the product the shopper is viewing, so 'this'/'it' resolves to it."""
    if not current_product_id:
        return None
    with get_db() as conn:
        row = conn.execute(
            "SELECT product_id, name, garment_type, colors, price FROM catalogue WHERE product_id = ?",
            (current_product_id,),
        ).fetchone()
    if row is None:
        return None
    colors = ", ".join(json.loads(row["colors"]))
    return (
        f'- {row["name"]} (product_id: {row["product_id"]}), a {row["garment_type"]}, '
        f'${row["price"]:.2f}. Available colors: {colors}.'
    )


def load_history_rows(user_id: int, limit: int = 20) -> list[sqlite3.Row]:
    """Most recent chat rows for a user, oldest-first."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT role, content, products_json FROM chat_messages "
            "WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    return list(reversed(rows))


def agent_message_history(rows: list[sqlite3.Row]):
    """Rebuild prior turns as PydanticAI messages so the agent remembers the thread."""
    from pydantic_ai.messages import (
        ModelRequest,
        ModelResponse,
        TextPart,
        UserPromptPart,
    )

    history = []
    for row in rows:
        if row["role"] == "user":
            history.append(ModelRequest(parts=[UserPromptPart(content=row["content"])]))
        elif row["role"] == "assistant":
            history.append(ModelResponse(parts=[TextPart(content=row["content"])]))
    return history or None


def save_message(user_id: int, role: str, content: str, cards: list[ProductCard]) -> None:
    products_json = json.dumps([c.model_dump() for c in cards]) if cards else None
    with get_db() as conn:
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, ?, ?, ?)",
            (user_id, role, content, products_json),
        )
        conn.commit()


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, user: PublicUser | None = Depends(optional_user)) -> ChatResponse:
    message = req.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="Message cannot be empty.")

    # Who is chatting + what page they're on.
    deps = ChatDeps(
        shopper_name=user.first_name if user else None,
        shopper_email=user.email if user else None,
        current_product=build_page_context(req.current_product_id),
    )
    # Only logged-in users have saved history to remember.
    history = agent_message_history(load_history_rows(user.id)) if user else None

    try:
        result = await run_chat(message, deps=deps, message_history=history)
    except MissingAPIKey as exc:
        # Configuration problem the operator can fix; safe to report.
        append_entry(message, [], "error:missing_api_key", user.id if user else None)
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception:  # noqa: BLE001 - surface a friendly message, never raw model errors
        logging.getLogger("campus_customs").exception("Agent chat failed")
        append_entry(message, [], "error:agent_failed", user.id if user else None)
        raise HTTPException(
            status_code=502, detail="The assistant is unavailable right now. Please try again."
        )

    reply = result.output
    cards = cards_from_ids(reply.product_ids)

    # Append this turn to the audit trail (never wiped between runs).
    append_entry(
        message,
        extract_tool_calls(result.all_messages()),
        "completed",
        user.id if user else None,
    )

    # Persist the turn for signed-in shoppers so it reloads next time.
    if user:
        save_message(user.id, "user", message, [])
        save_message(user.id, "assistant", reply.reply, cards)

    return ChatResponse(reply=reply.reply, products=cards)


@app.get("/api/chat/history", response_model=ChatHistoryResponse)
def chat_history(user: PublicUser = Depends(current_user)) -> ChatHistoryResponse:
    """Replay a signed-in shopper's saved conversation into the chat window."""
    messages = []
    for row in load_history_rows(user.id, limit=100):
        cards = []
        if row["products_json"]:
            cards = [ProductCard(**c) for c in json.loads(row["products_json"])]
        messages.append(
            ChatHistoryMessage(role=row["role"], content=row["content"], products=cards)
        )
    return ChatHistoryResponse(messages=messages)
