# Campus Customs — Design (Problem 10)

Restyled the whole site into a clean, editorial storefront inspired by
[acmecups.nz](https://acmecups.nz/), keeping the Yale palette (navy, grey, white).

## What I changed

- **Sharp and minimal.** Removed all rounded corners (square 90° everywhere), dropped the soft
  shadows and the tinted/light-blue section backgrounds. Structure now comes from thin 1px
  lines and generous whitespace on white — like Acme's bordered grid.
- **Two fonts only.** **Archivo** (bold grotesque) for headings, nav, product names, prices,
  and buttons; **Inter** for body text. Nothing else.
- **Full-screen campus hero.** The landing page is a single edge-to-edge photo of Yale's Old
  Campus (Durfee Hall, CC0 from Wikimedia Commons — no attribution required) filling the whole
  viewport, with the nav overlaid in white on top of it. Minimal copy: just "Campus Customs" and
  one line, with a single Shop button over a subtle gradient.
- **Very little text.** Trimmed copy across the site to only what's necessary — the hero, the
  collection boxes (category name only), and page headers are pared down; the announcement bar
  and marketing blurbs were removed.
- **Acme-style product cards on white.** A bordered cell with the product centered on a clean
  white background, the name in bold UPPERCASE, a small grey subtitle line (the color options),
  and a full-width bottom bar with "View" on the left and the price right-aligned. Cards sit in a
  tight grid separated by thin divider lines. Because ~70% of the provided product photos ship on
  solid black backgrounds, the backend normalizes every product image to white at startup
  (flood-filling the background) so the grid is uniformly clean — see `backend/images.py`.
- **Stock badges** are small square tags on the card image.
- **Left-aligned hero with scroll motion.** The hero headline, line, and button are left-aligned
  over a left-weighted gradient. As you scroll past the first screen, the hero text drifts down
  and fades out while the photo parallaxes slightly — an Acme-style reveal into the content below.
- **Accurate subtitles, no misleading colors.** Each card shows the garment type (e.g. "Pullover
  Hoodie") under the name. The database's `colors` field describes the *design's* color scheme
  (the Harvard tee lists "red" for its graphic), not the variants Campus Customs actually sells,
  and there's one photo per product — so color swatches would misrepresent what's for sale. They
  were removed; `colors` is still used behind the scenes for the chatbot's search.
- **Tightened hierarchy + motion.** Uppercase section titles with underlines, consistent
  letter-spacing, and restrained hover motion (a gentle image zoom on cards, button
  invert). The Shop filter/sort controls sit inline with no box around them.
- **Liquid-glass chatbot.** The chat is a deliberate soft counterpoint to the sharp grid: a
  frosted translucent white panel (backdrop blur) with rounded corners, pill-shaped bubbles and
  input, rounded product cards, and a frosted toggle — sleek and all-white, with the navy used
  only as a quiet accent.
- **Minimal nav and footer.** Uppercase Archivo nav links with a thin underline for the active
  page; a clean white footer with a single hairline rule.

## Why it should help customers stick around and buy

- The campus hero sets an immediate, premium Yale mood, so the site feels like a real brand
  storefront rather than a demo — building trust to buy.
- The uncluttered grid and bold product names make it easy to scan 100+ items quickly and keep
  attention on the products, which shortens the path to a purchase.
- Color options and clear price/stock on every card (plus "Only a few left") help shoppers
  decide faster and nudge action.
- One consistent type system and tidy spacing make the whole site feel polished and
  trustworthy, which keeps people browsing longer.
