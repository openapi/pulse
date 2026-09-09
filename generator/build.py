#!/usr/bin/env python3
"""
Openapi Pulse Card generator.

Reads content/current.yml and writes public/ticker.svg (light) and
public/ticker-dark.svg (dark).

    python3 generator/build.py

Avatars are downloaded from https://github.com/<nickname>.png and embedded in
the SVG as data URIs. This is not an optimisation: GitHub serves README images
through a caching proxy that renders them in restricted mode, where an SVG
cannot pull in any external resource. Anything the card shows has to be inside
the file. Downloads are cached in generator/.cache/ between runs, and a
nickname that cannot be fetched falls back to an initial-letter monogram, so
the build never breaks on a typo or an offline machine.

PyYAML is used when available; otherwise a minimal parser handles the small
subset of YAML that content/current.yml uses.
"""

import base64
import sys
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pools import item_key, read_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "current.yml"
APIS = ROOT / "content" / "apis.yml"
PUBLIC = ROOT / "public"
CACHE = Path(__file__).resolve().parent / ".cache"

WIDTH = 880
HEIGHT = 148

# Four editorial tracks: x origin, usable width, and the x of the hairline
# separator that closes each one. Widths are sized to the longest label each
# column carries, so nothing has to be truncated in the common case.
TRACKS = (
    {"x": 24, "width": 140, "sep": 177},
    {"x": 190, "width": 205, "sep": 408},
    {"x": 421, "width": 195, "sep": 629},
    {"x": 642, "width": 214, "sep": None},
)

# Breathing room kept between the end of a value and the next separator.
TRACK_PADDING = 10

LABEL_Y = 76
VALUE_Y = 103
AVATAR_SIZE = 26
AVATAR_CY = 97

# Values are fitted to their track: the type shrinks from PREFERRED_SIZE down
# to MIN_SIZE to make a long value fit, and only what still overflows at the
# smallest size is clipped with an ellipsis. Real GitHub handles run long
# (@FrancescoRicchiutiOpenapi is 25 characters), so a fixed budget would either
# truncate half the organization or force every column to be sized for the
# worst case.
PREFERRED_SIZE = 14
MIN_SIZE = 10

# Approximate advance widths, in em, for the system sans-serif at weight 600.
# Good enough to fit text into a fixed track without measuring a real font.
_WIDE = set("mMWw@")
_NARROW = set("iljItf.,;:'!|[]()")
_CHAR_EM = {c: 0.86 for c in _WIDE}
_CHAR_EM.update({c: 0.30 for c in _NARROW})
_CHAR_EM.update({c: 0.40 for c in "-_ "})


def text_width(text, size, spacing=0):
    """Estimated rendered width of a string, in user units."""
    em = 0.0
    for char in str(text):
        if char in _CHAR_EM:
            em += _CHAR_EM[char]
        elif char.isupper():
            em += 0.68
        elif char.isdigit():
            em += 0.57
        else:
            em += 0.55
    return em * size + spacing * max(len(str(text)) - 1, 0)


def fit(text, budget):
    """Largest size at which `text` fits `budget`, plus the text to draw."""
    text = str(text)
    size = PREFERRED_SIZE
    while size > MIN_SIZE and text_width(text, size) > budget:
        size -= 0.5
    if text_width(text, size) <= budget:
        return text, size
    # Still too wide at the smallest size: clip until it fits.
    while len(text) > 1 and text_width(text[:-1] + "…", size) > budget:
        text = text[:-1]
    return text.rstrip() + "…", size

THEMES = {
    "light": {
        "file": "ticker.svg",
        "bg": "#ffffff",
        "bg_alt": "#f6f8fa",
        "border": "#d8dee4",
        "text": "#1f2328",
        "muted": "#59636e",
        "faint": "#e4e8ed",
        "accent": "#563e7d",
        "cta_bg": "#1f2328",
        "cta_text": "#ffffff",
    },
    "dark": {
        "file": "ticker-dark.svg",
        "bg": "#0d1117",
        "bg_alt": "#111823",
        "border": "#2c3440",
        "text": "#e6edf3",
        "muted": "#9198a1",
        "faint": "#212a35",
        "accent": "#9c7ecc",
        "cta_bg": "#e6edf3",
        "cta_text": "#0d1117",
    },
}

FONT = ("-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,"
        "Arial,'Liberation Sans',sans-serif")


# --------------------------------------------------------------------------
# content
# --------------------------------------------------------------------------

def load_content():
    """Parse content/current.yml into a plain dict."""
    raw = CONTENT.read_text(encoding="utf-8")
    try:
        import yaml
    except ImportError:
        return _mini_yaml(raw)
    return yaml.safe_load(raw)


def _mini_yaml(raw):
    """Fallback parser: nested maps plus lists of plain scalars."""
    data = {}
    stack = [(-1, data)]
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        body = line.strip()

        if body.startswith("- "):
            container = next(c for i, c in reversed(stack) if i < indent)
            container.append(_scalar(body[2:]))
            continue

        while stack and stack[-1][0] >= indent:
            stack.pop()
        container = stack[-1][1]

        key, _, value = body.partition(":")
        key, value = key.strip(), value.strip()
        if value == "":
            child = [] if key in ("developers", "contributors", "exclude") else {}
            container[key] = child
            stack.append((indent, child))
        else:
            container[key] = _scalar(value)
    return data


def _scalar(value):
    value = value.strip()
    if value[:1] in "\"'" and value[:1] == value[-1:]:
        value = value[1:-1]
    if value == "null":
        return None
    if value.isdigit():
        return int(value)
    return value


# --------------------------------------------------------------------------
# avatars
# --------------------------------------------------------------------------

def avatar_data_uri(nickname):
    """Return a base64 PNG data URI for a GitHub user, or None if unavailable."""
    if not nickname:
        return None
    CACHE.mkdir(exist_ok=True)
    cached = CACHE / f"{nickname}.png"

    if not cached.exists():
        url = f"https://github.com/{nickname}.png?size=96"
        try:
            request = Request(url, headers={"User-Agent": "openapi-pulse-card"})
            with urlopen(request, timeout=10) as response:
                payload = response.read()
        except (URLError, HTTPError, OSError) as error:
            print(f"  ! avatar for @{nickname} unavailable ({error}); "
                  f"using monogram", file=sys.stderr)
            return None
        cached.write_bytes(payload)

    encoded = base64.b64encode(cached.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


# --------------------------------------------------------------------------
# svg helpers
# --------------------------------------------------------------------------

def clip(text, limit):
    text = str(text)
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def text_el(x, y, content, fill, size, weight=400, spacing=0, anchor="start"):
    attrs = [f'x="{x}"', f'y="{y}"', f'fill="{fill}"',
             f'font-size="{size}"', f'font-weight="{weight}"']
    if spacing:
        attrs.append(f'letter-spacing="{spacing}"')
    if anchor != "start":
        attrs.append(f'text-anchor="{anchor}"')
    return f'<text {" ".join(attrs)}>{escape(str(content))}</text>'


def label_el(track, text, theme):
    return text_el(track["x"], LABEL_Y, clip(text, 26).upper(),
                   theme["muted"], 9, 700, spacing=1.2)


def person_el(track, nickname, avatar, theme, index):
    """Avatar disc plus @handle, laid out from the track's x origin."""
    x = track["x"]
    radius = AVATAR_SIZE / 2
    top = AVATAR_CY - radius
    parts = [
        f'<clipPath id="avatar-{index}">'
        f'<circle cx="{x + radius}" cy="{AVATAR_CY}" r="{radius}"/>'
        f'</clipPath>'
    ]

    if avatar:
        parts.append(
            f'<image x="{x}" y="{top}" width="{AVATAR_SIZE}" height="{AVATAR_SIZE}" '
            f'clip-path="url(#avatar-{index})" preserveAspectRatio="xMidYMid slice" '
            f'href="{avatar}" xlink:href="{avatar}"/>'
        )
    else:
        # Monogram fallback: keeps the layout intact when the avatar is missing.
        parts.append(
            f'<circle cx="{x + radius}" cy="{AVATAR_CY}" r="{radius}" '
            f'fill="{theme["faint"]}"/>'
        )
        parts.append(
            text_el(x + radius, AVATAR_CY + 4.5, nickname[:1].upper(),
                    theme["muted"], 12, 700, anchor="middle")
        )

    # Hairline ring, so light avatars keep an edge against the card.
    parts.append(
        f'<circle cx="{x + radius}" cy="{AVATAR_CY}" r="{radius - 0.5}" '
        f'fill="none" stroke="{theme["border"]}"/>'
    )
    handle, size = fit(f"@{nickname}",
                       track["width"] - AVATAR_SIZE - 10 - TRACK_PADDING)
    parts.append(
        text_el(x + AVATAR_SIZE + 10, VALUE_Y, handle, theme["text"], size, 600)
    )
    return parts


# --------------------------------------------------------------------------
# card
# --------------------------------------------------------------------------

def build(theme_name, data, avatars):
    t = THEMES[theme_name]
    week = data.get("week", "")
    cta = data.get("cta", {}) or {}
    cta_text = clip(cta.get("text", "JOIN THE COMMUNITY"), 30)
    developer = featured(data, "developers")
    contributor = featured(data, "contributors")

    parts = []

    # --- shell ---------------------------------------------------------
    parts.append(
        f'<defs><clipPath id="card">'
        f'<rect x="1" y="1" width="{WIDTH - 2}" height="{HEIGHT - 2}" rx="9.5"/>'
        f'</clipPath></defs>'
    )
    parts.append(
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="10" '
        f'fill="{t["bg"]}" stroke="{t["border"]}"/>'
    )
    # Header band, subtly tinted so the card reads as editorial, not as a badge.
    parts.append(
        f'<path d="M0.5 10.5A10 10 0 0 1 10.5 0.5H{WIDTH - 10.5}A10 10 0 0 1 {WIDTH - 0.5} 10.5V47.5H0.5Z" '
        f'fill="{t["bg_alt"]}"/>'
    )
    parts.append(
        f'<line x1="0.5" y1="47.5" x2="{WIDTH - 0.5}" y2="47.5" stroke="{t["border"]}"/>'
    )

    # --- heartbeat mark ------------------------------------------------
    parts.append(
        f'<g stroke="{t["accent"]}" stroke-width="2" fill="none" '
        f'stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="M26 24h8l4-9 6 18 4-9h8"/>'
        f'</g>'
    )
    parts.append(
        f'<circle class="ring" cx="56" cy="24" r="3" fill="none" '
        f'stroke="{t["accent"]}" stroke-width="1.5"/>'
    )
    parts.append(f'<circle class="dot" cx="56" cy="24" r="3" fill="{t["accent"]}"/>')

    # --- header text ---------------------------------------------------
    parts.append(text_el(72, 29, "OPENAPI PULSE", t["text"], 13, 700, spacing=1.6))
    parts.append(text_el(210, 29, "·", t["muted"], 13, 700))
    parts.append(text_el(224, 29, f"WEEK {week}", t["muted"], 13, 600, spacing=1.6))

    # --- CTA pill ------------------------------------------------------
    pill_w = 8 * len(cta_text) + 46
    pill_x = WIDTH - 24 - pill_w
    parts.append(
        f'<rect x="{pill_x}" y="12" width="{pill_w}" height="24" rx="12" fill="{t["cta_bg"]}"/>'
    )
    parts.append(
        text_el(pill_x + pill_w / 2, 28, f"{cta_text}  →", t["cta_text"], 11, 700,
                spacing=1.2, anchor="middle")
    )

    # --- editorial tracks ----------------------------------------------
    api = featured_api().get("name", "")
    discussion = (data.get("discussion", {}) or {}).get("title", "")

    parts.append(label_el(TRACKS[0], "API of the week", t))
    api_text, api_size = fit(api, TRACKS[0]["width"] - TRACK_PADDING)
    parts.append(text_el(TRACKS[0]["x"], VALUE_Y, api_text, t["text"], api_size, 600))

    parts.append(label_el(TRACKS[1], "Developer of the week", t))
    parts.extend(person_el(TRACKS[1], developer, avatars.get(developer), t, 0))

    parts.append(label_el(TRACKS[2], "Contributor of the week", t))
    parts.extend(person_el(TRACKS[2], contributor, avatars.get(contributor), t, 1))

    parts.append(label_el(TRACKS[3], "Community discussion", t))
    disc_text, disc_size = fit(discussion, TRACKS[3]["width"] - TRACK_PADDING)
    parts.append(text_el(TRACKS[3]["x"], VALUE_Y, disc_text, t["text"], disc_size, 600))

    for track in TRACKS:
        if track["sep"]:
            parts.append(
                f'<line x1="{track["sep"]}" y1="66" x2="{track["sep"]}" y2="110" '
                f'stroke="{t["faint"]}"/>'
            )

    # --- baseline ECG --------------------------------------------------
    # A flat trace with one beat, sliding slowly left to right along the bottom
    # edge: the card's "still alive" signal.
    beat = "M0 0h96l6-10 5 20 6-10h74"
    parts.append(
        f'<g clip-path="url(#card)">'
        f'<g transform="translate(0 127)">'
        f'<line x1="24" y1="0" x2="{WIDTH - 24}" y2="0" stroke="{t["border"]}" stroke-width="1.5"/>'
        f'<g stroke="{t["accent"]}" stroke-width="2" fill="none" opacity="0.75" '
        f'stroke-linecap="round" stroke-linejoin="round">'
        f'<path class="trace" d="{beat}" transform="translate(24 0)"/>'
        f'</g>'
        f'</g>'
        f'</g>'
    )

    body = "\n  ".join(parts)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'role="img" aria-label="Openapi Pulse — week {week}">\n'
        f'  <title>Openapi Pulse — week {week}</title>\n'
        f'  <style>\n'
        f'    text {{ font-family: {FONT}; }}\n'
        f'    .dot, .ring {{ transform-box: fill-box; transform-origin: center; }}\n'
        f'    .dot {{ animation: beat 1.6s ease-in-out infinite; }}\n'
        f'    .ring {{ animation: halo 1.6s ease-out infinite; }}\n'
        f'    .trace {{ transform: translateX(24px); animation: trace 9s linear infinite; }}\n'
        f'    @keyframes beat {{ 0%, 100% {{ opacity: 1; transform: scale(1); }}'
        f' 45% {{ opacity: 0.55; transform: scale(0.7); }} }}\n'
        f'    @keyframes halo {{ 0% {{ opacity: 0.7; transform: scale(1); }}'
        f' 70%, 100% {{ opacity: 0; transform: scale(2.6); }} }}\n'
        f'    @keyframes trace {{ from {{ transform: translateX(24px); }}'
        f' to {{ transform: translateX({WIDTH - 211}px); }} }}\n'
        f'    @media (prefers-reduced-motion: reduce) {{\n'
        f'      .dot, .ring, .trace {{ animation: none; }}\n'
        f'      .ring {{ opacity: 0; }}\n'
        f'    }}\n'
        f'  </style>\n'
        f'  {body}\n'
        f'</svg>\n'
    )


def featured(data, key):
    """Who is on stage: always the entry at the top of the queue."""
    people = data.get(key) or []
    return people[0] if people else ""


def featured_api():
    """The API at the top of content/apis.yml.

    Read through the pool helpers rather than a YAML parser: the file is a list
    of records, and this only ever needs the first one.
    """
    lines = APIS.read_text(encoding="utf-8").splitlines()
    _, _, items = read_block(lines, "apis")
    if not items:
        return {}
    return {field: item_key(items[0], field) for field in ("slug", "name", "url")}


def main():
    data = load_content()
    developer = featured(data, "developers")
    contributor = featured(data, "contributors")

    avatars = {}
    for nickname in (developer, contributor):
        if nickname and nickname not in avatars:
            avatars[nickname] = avatar_data_uri(nickname)

    print(f"edition {data.get('week')}: {featured_api().get('name', '?')} (api), "
          f"@{developer} (developer), @{contributor} (contributor)")

    PUBLIC.mkdir(exist_ok=True)
    for name, theme in THEMES.items():
        out = PUBLIC / theme["file"]
        out.write_text(build(name, data, avatars), encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
