# Campus Customs — Usability Improvements (Problem 9)

Four improvements: two on the front end and two in the agent/backend. The front-end work
takes visual and UX cues from [acmecups.nz](https://acmecups.nz/) (clean card grid, color names
under product titles, clear stock badges, generous whitespace, a filter/sort toolbar) while
keeping the Yale palette — navy blue, grey, and white.

## Front-end

### 1. Acme-style product cards: color names + stock badge + hover
**What I added.** Each product card now lists its color options under the name (e.g.
"Heather Gray · White · Red · Navy Blue"), shows a stock badge in the top-left of the image
("Sold out" when nothing is left, "Only a few left" when total stock is low), and gently zooms
the photo on hover. Implemented in `frontend/src/components/ProductCard.tsx`; the stock numbers
come from the API (`total_stock` added to `/api/products` and `/api/products/{id}`).

**Why it helps.** Shoppers can see the colors and whether something is running low without
opening each product, which is exactly the at-a-glance scanning Acme's grid is good at. The
"Only a few left" badge also nudges purchases (scarcity) and sets honest expectations, which
reduces disappointed clicks for the business.

### 2. Filter & sort toolbar on the Products page
**What I added.** A toolbar above the grid (`frontend/src/pages/Products.tsx`) with a price-range
filter (Under $40 / $60 / $80), a color filter built from the catalogue's real colors, a sort
control (Featured, Price low→high, high→low), and an "In stock only" toggle, alongside the
existing search and collection chips. It shows a live result count and a friendly empty state.

**Why it helps.** It mirrors Acme's price and color collections so shoppers can narrow 100+
products to the few they care about — "navy crewnecks under $60 that are in stock" — in a couple
of clicks. Faster discovery means more shoppers reach a product they'll actually buy.

## Agent / backend

### 3. Output validation: drop products the agent made up
**What I added.** A PydanticAI output validator on the agent (`drop_unknown_products` in
`backend/agent.py`) checks every `product_id` the agent returns against the real catalogue and
removes any that aren't real before the reply leaves the server. The catalogue-backed id set
comes from `db.valid_product_ids()`.

**Why it helps.** The page can only ever render cards for products that exist, so a model slip
can't produce a broken or fake product card in front of a customer. It makes the assistant more
accurate and safer with no downside when the agent behaves.

### 4. In-memory catalogue cache: faster and cheaper lookups
**What I added.** The catalogue (descriptions, prices, colors) is loaded once and kept in memory
with a short TTL (`get_catalogue` / `get_catalogue_map` in `backend/db.py`). The agent's tools
(`search_products`, `get_product_details`, `check_size_stock`) read product info from this cache
instead of querying SQLite on every message; stock is still read live so availability stays
accurate.

**Why it helps.** A single chat turn can trigger several product lookups. Serving them from
memory removes repeated database reads (measured ~0.001 ms cached vs ~0.5 ms per DB load) and
cuts latency, so replies come back faster and the backend does less work per message — cheaper
to run at scale.
