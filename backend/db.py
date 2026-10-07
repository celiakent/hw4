"""Shared database access for the Campus Customs backend."""

import json
import sqlite3
import time
from pathlib import Path

from models import ProductCard, SizeStock

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DATA_DIR / "campus_customs.db"

SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# --- Catalogue cache --------------------------------------------------------
# The catalogue (product descriptions, prices, colors) rarely changes, so we
# keep it in memory and refresh it at most once per TTL. The agent's product
# lookups hit this cache instead of re-querying SQLite on every message, which
# makes replies faster and cheaper. Inventory (stock) is always read live.

_CATALOGUE_TTL = 300  # seconds
_catalogue_cache: list[dict] | None = None
_catalogue_cached_at: float = 0.0


def get_catalogue() -> list[dict]:
    """Return all catalogue rows as plain dicts, cached in memory with a TTL."""
    global _catalogue_cache, _catalogue_cached_at
    now = time.time()
    if _catalogue_cache is None or now - _catalogue_cached_at > _CATALOGUE_TTL:
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM catalogue").fetchall()
        _catalogue_cache = [dict(r) for r in rows]
        _catalogue_cached_at = now
    return _catalogue_cache


def get_catalogue_map() -> dict[str, dict]:
    """product_id -> catalogue row (dict), from the cache."""
    return {r["product_id"]: r for r in get_catalogue()}


def valid_product_ids() -> set[str]:
    """The set of real product_ids, used to drop anything the agent made up."""
    return set(get_catalogue_map().keys())


def invalidate_catalogue_cache() -> None:
    global _catalogue_cache
    _catalogue_cache = None


def row_to_card(row: sqlite3.Row) -> ProductCard:
    return ProductCard(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        price=row["price"],
        image_url=f"/images/{row['image_file_path']}",
        description=row["description"],
    )


def sorted_sizes(rows: list[sqlite3.Row]) -> list[SizeStock]:
    return sorted(
        (SizeStock(size=r["size"], quantity=r["quantity"]) for r in rows),
        key=lambda s: SIZE_ORDER.index(s.size) if s.size in SIZE_ORDER else len(SIZE_ORDER),
    )


def colors_and_tags(row: sqlite3.Row) -> tuple[list[str], list[str]]:
    return json.loads(row["colors"]), json.loads(row["search_tags"])
