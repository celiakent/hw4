"""Tools the Campus Customs agent can call to read the product database.

These are the only way the agent learns real descriptions, prices, and stock, so it
can answer honestly instead of guessing. The typed return shapes live in models.py.
"""

import json

from db import get_catalogue, get_catalogue_map, get_db, sorted_sizes
from models import (
    ProductDetails,
    ProductSearchResult,
    SizeAvailability,
    SizeStockResult,
)


def _colors_tags(row: dict) -> tuple[list[str], list[str]]:
    return json.loads(row["colors"]), json.loads(row["search_tags"])


def search_products(query: str, limit: int = 8) -> list[ProductSearchResult]:
    """Find catalogue items matching a shopper's words.

    Matches the query terms (case-insensitive) against name, garment type, colors,
    description, and search tags. Returns a short ranked list of candidates. Use this
    first to find the right product(s), then call get_product_details for exact price
    and per-size stock. Reads the in-memory catalogue cache, not the database.
    """
    terms = [t for t in query.lower().split() if t]
    rows = get_catalogue()

    scored: list[tuple[int, ProductSearchResult]] = []
    for row in rows:
        colors, tags = _colors_tags(row)
        haystack = " ".join(
            [row["name"], row["garment_type"], row["description"], " ".join(colors), " ".join(tags)]
        ).lower()
        score = sum(1 for t in terms if t in haystack)
        if terms and score == 0:
            continue
        scored.append(
            (
                score,
                ProductSearchResult(
                    product_id=row["product_id"],
                    name=row["name"],
                    garment_type=row["garment_type"],
                    price=row["price"],
                    colors=colors,
                    short_description=row["description"][:140],
                ),
            )
        )

    scored.sort(key=lambda s: s[0], reverse=True)
    return [r for _, r in scored[:limit]]


def get_product_details(product_id: str) -> ProductDetails | None:
    """Get the full description, exact price, colors, and per-size stock for one product.

    Call this before quoting a price or describing a product, and whenever a shopper
    asks about overall availability. Returns None if the product_id does not exist.
    Product info comes from the catalogue cache; stock is read live.
    """
    row = get_catalogue_map().get(product_id)
    if row is None:
        return None
    with get_db() as conn:
        stock = conn.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)
        ).fetchall()

    colors, _ = _colors_tags(row)
    sizes = [
        SizeAvailability(size=s.size, quantity=s.quantity, in_stock=s.quantity > 0)
        for s in sorted_sizes(stock)
    ]
    return ProductDetails(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        description=row["description"],
        price=row["price"],
        colors=colors,
        sizes=sizes,
        total_in_stock=sum(s.quantity for s in sizes),
    )


def check_size_stock(product_id: str, size: str) -> SizeStockResult | None:
    """Check how many of one product are in stock in a specific size.

    Use this for direct questions like "do you have the Mom hoodie in M?". `size` is
    matched case-insensitively (XS, S, M, L, XL, XXL). Returns None if the product does
    not exist; if the product exists but the size is unknown, quantity is 0 and
    available_sizes lists the sizes that do have stock.
    """
    want = size.strip().upper()
    row = get_catalogue_map().get(product_id)
    if row is None:
        return None
    with get_db() as conn:
        stock = conn.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)
        ).fetchall()

    sizes = sorted_sizes(stock)
    match = next((s for s in sizes if s.size.upper() == want), None)
    quantity = match.quantity if match else 0
    return SizeStockResult(
        product_id=row["product_id"],
        name=row["name"],
        size=want,
        quantity=quantity,
        in_stock=quantity > 0,
        available_sizes=[s.size for s in sizes if s.quantity > 0],
    )
