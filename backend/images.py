"""Normalize product photos to white backgrounds.

Many of the provided product images sit on a solid black background. For a clean,
Acme-style grid we want every product on white. On startup we generate white-background
copies into a cache dir (regenerated from the original images, which are not committed),
and the API serves those. If anything fails we fall back to the originals.
"""

import statistics
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
SRC_DIR = DATA_DIR / "products"
CACHE_DIR = DATA_DIR / ".products_white"  # gitignored, rebuilt at runtime

_WHITE = (255, 255, 255)


def _bg_is_dark(im) -> bool:
    w, h = im.size
    corners = [im.getpixel((1, 1)), im.getpixel((w - 2, 1)),
               im.getpixel((1, h - 2)), im.getpixel((w - 2, h - 2))]
    brightness = statistics.mean(statistics.mean(c[:3]) for c in corners)
    return brightness < 60


_SENTINEL = (254, 0, 254)  # a color that never appears in a garment photo


def _whiten(src: Path, dst: Path) -> None:
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter

    im = Image.open(src).convert("RGB")
    if not _bg_is_dark(im):
        im.save(dst, "JPEG", quality=90)
        return

    w, h = im.size
    # Step 1: flood-fill the black backdrop with a sentinel color, seeding from points
    # all along the border. We use a *conservative* threshold so the fill only consumes
    # the near-black backdrop and never bleeds through a dark channel into the navy
    # garment (which would carve white holes, e.g. between crossed arms).
    step = 3
    seeds = []
    for x in range(0, w, step):
        seeds += [(x, 0), (x, h - 1)]
    for y in range(0, h, step):
        seeds += [(0, y), (w - 1, y)]
    for x, y in seeds:
        if max(im.getpixel((x, y))) < 30:
            # Ultra-conservative: only pure-black backdrop is consumed, so the fill can
            # never climb into the (bluish, less-black) navy garment and carve holes.
            ImageDraw.floodfill(im, (x, y), _SENTINEL, thresh=12)

    arr = np.asarray(im)
    bg = (arr[..., 0] == 254) & (arr[..., 1] == 0) & (arr[..., 2] == 254)

    # Step 2: de-fringe. The conservative fill leaves a thin, jagged dark halo of
    # anti-aliased pixels at the garment edge. Grow the background by a few pixels and
    # whiten any *dark* pixels in that band, so the rough fringe disappears while the
    # garment interior (and any white logo) is untouched. Interior shadows that aren't
    # next to the background stay navy — no white holes.
    grown = np.asarray(Image.fromarray((bg * 255).astype("uint8")).filter(ImageFilter.MaxFilter(7)))
    fringe = (grown > 0) & (~bg) & (arr.max(axis=2) < 120)

    out = arr.copy()
    out[bg | fringe] = _WHITE
    result = Image.fromarray(out, "RGB")
    # A touch of smoothing only along the new edge keeps it from looking pixelated.
    result = result.filter(ImageFilter.SMOOTH)
    result.save(dst, "JPEG", quality=92)


def serve_dir() -> Path:
    """Return the directory of product images the API should serve (white-bg if built)."""
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        originals = sorted(SRC_DIR.glob("*.jpg"))
        for src in originals:
            dst = CACHE_DIR / src.name
            if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
                _whiten(src, dst)
        # Only use the cache if it covers every product image.
        if originals and all((CACHE_DIR / s.name).exists() for s in originals):
            return CACHE_DIR
    except Exception:  # noqa: BLE001 - any failure: fall back to the originals
        pass
    return SRC_DIR
