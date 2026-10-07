"""Campus Customs PydanticAI agent: wiring, model, prompt, and tools.

The model is reached through Portkey's OpenAI-compatible gateway. Configuration
comes from backend/.env (see backend/.env.example).
"""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from db import valid_product_ids
from models import AgentReply
from tools import check_size_stock, get_product_details, search_products


@dataclass
class ChatDeps:
    """Per-conversation context handed to the agent on each turn.

    This is how the agent knows *who* it's talking to and *what page* they're on,
    without the model having to ask. None means "not available" (e.g. a guest, or a
    shopper who isn't on a product page).
    """

    shopper_name: str | None = None
    shopper_email: str | None = None
    # A short, already-looked-up description of the product the shopper is viewing,
    # so "do you have this in pink?" resolves to the right item.
    current_product: str | None = None


class MissingAPIKey(RuntimeError):
    """Raised when no Portkey API key is configured."""


BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent
# Load the Portkey config from .env. We check the repo root first and then
# backend/.env (either location works); override=True so the file wins over any
# stale PORTKEY_* value already in the shell environment.
load_dotenv(ROOT_DIR / ".env", override=True)
load_dotenv(BACKEND_DIR / ".env", override=True)

PROMPT_PATH = BACKEND_DIR / "prompts" / "prompt.md"


def _build_model() -> OpenAIChatModel:
    api_key = os.getenv("PORTKEY_API_KEY")
    if not api_key:
        raise MissingAPIKey(
            "PORTKEY_API_KEY is not set. Copy backend/.env.example to backend/.env "
            "and add your Portkey API key."
        )

    base_url = os.getenv("PORTKEY_BASE_URL", "https://api.portkey.ai/v1")
    model_name = os.getenv("AGENT_MODEL", "gpt-5.6")

    # Portkey routing headers: a virtual key and/or a config id, if provided.
    default_headers = {}
    if os.getenv("PORTKEY_VIRTUAL_KEY"):
        default_headers["x-portkey-virtual-key"] = os.environ["PORTKEY_VIRTUAL_KEY"]
    if os.getenv("PORTKEY_CONFIG"):
        default_headers["x-portkey-config"] = os.environ["PORTKEY_CONFIG"]

    client = AsyncOpenAI(
        base_url=base_url,
        api_key=api_key,
        default_headers=default_headers or None,
    )
    provider = OpenAIProvider(openai_client=client)
    return OpenAIChatModel(model_name, provider=provider)


def _load_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


# Built lazily so importing this module (e.g. in tests) doesn't require a key.
_agent: Agent[ChatDeps, AgentReply] | None = None


def get_agent() -> "Agent[ChatDeps, AgentReply]":
    global _agent
    if _agent is None:
        agent = Agent(
            _build_model(),
            output_type=AgentReply,
            deps_type=ChatDeps,
            instructions=_load_prompt(),
        )
        agent.tool_plain(search_products)
        agent.tool_plain(get_product_details)
        agent.tool_plain(check_size_stock)

        @agent.output_validator
        def drop_unknown_products(reply: AgentReply) -> AgentReply:
            """Safety net: never show a product the agent invented.

            Any product_id that isn't a real catalogue id is removed before the reply
            reaches the website, so the page only ever renders cards for real products.
            """
            valid = valid_product_ids()
            kept = [pid for pid in reply.product_ids if pid in valid]
            if len(kept) != len(reply.product_ids):
                reply.product_ids = kept
            return reply

        @agent.instructions
        def who_and_where(ctx: RunContext[ChatDeps]) -> str:
            """Inject the live customer + page context for this turn."""
            deps = ctx.deps
            lines: list[str] = []
            if deps.shopper_name or deps.shopper_email:
                who = deps.shopper_name or "a signed-in shopper"
                email = f" ({deps.shopper_email})" if deps.shopper_email else ""
                lines.append(
                    f"You are chatting with {who}{email}. You may greet them by first name. "
                    "You still cannot see their password, orders, or payment details."
                )
            else:
                lines.append("You are chatting with a guest who is not signed in.")
            if deps.current_product:
                lines.append(
                    "The shopper is currently viewing this product page, so words like "
                    f'"this", "it", or "this one" refer to it:\n{deps.current_product}'
                )
            return "\n".join(lines)

        _agent = agent
    return _agent


async def run_chat(
    message: str,
    deps: ChatDeps | None = None,
    message_history=None,
):
    """Run one chat turn and return the full run result (has .output and messages)."""
    return await get_agent().run(
        message,
        deps=deps or ChatDeps(),
        message_history=message_history,
    )
