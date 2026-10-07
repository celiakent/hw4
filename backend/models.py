"""Pydantic / PydanticAI structured types shared by the agent and the API."""

from pydantic import BaseModel, Field


class ProductCard(BaseModel):
    """A product the agent decided to surface on the page."""

    product_id: str
    name: str
    garment_type: str
    price: float
    image_url: str
    description: str


class SizeStock(BaseModel):
    size: str
    quantity: int


class AgentReply(BaseModel):
    """Structured output the agent returns for every turn."""

    reply: str = Field(description="The assistant's message to show in the chat window.")
    product_ids: list[str] = Field(
        default_factory=list,
        description="product_id values of items to show as cards next to the chat. "
        "Only include products you confirmed exist via a tool.",
    )


# ---- Tool result types (what the agent's tools return) ----

class ProductSearchResult(BaseModel):
    """One candidate from a product search — enough to decide and show a card."""

    product_id: str
    name: str
    garment_type: str
    price: float
    colors: list[str]
    short_description: str


class SizeAvailability(BaseModel):
    """Stock for a single size of a product."""

    size: str
    quantity: int
    in_stock: bool


class ProductDetails(BaseModel):
    """Full lookup for one product: description, price, and per-size stock."""

    product_id: str
    name: str
    garment_type: str
    description: str
    price: float
    colors: list[str]
    sizes: list[SizeAvailability]
    total_in_stock: int


class SizeStockResult(BaseModel):
    """Answer to 'is this product in stock in size X?'"""

    product_id: str
    name: str
    size: str
    quantity: int
    in_stock: bool
    available_sizes: list[str]


class ChatRequest(BaseModel):
    message: str
    # product_id of the page the shopper is currently viewing, if any. Lets the
    # agent resolve "do you have this in pink?" to the right item.
    current_product_id: str | None = None


class ChatResponse(BaseModel):
    """What the website's chat widget receives."""

    reply: str
    products: list[ProductCard] = Field(default_factory=list)


class ChatHistoryMessage(BaseModel):
    """One stored message, replayed into the chat window on return."""

    role: str  # "user" or "assistant"
    content: str
    products: list[ProductCard] = Field(default_factory=list)


class ChatHistoryResponse(BaseModel):
    messages: list[ChatHistoryMessage] = Field(default_factory=list)
