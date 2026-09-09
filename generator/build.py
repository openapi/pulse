#!/usr/bin/env python3
"""
OpenAPI Pulse Card generator.

Reads content/current.yml and writes public/ticker.svg (light) and
public/ticker-dark.svg (dark).

    python3 generator/build.py

No third-party dependencies required: PyYAML is used when available,
otherwise a minimal parser handles the small subset of YAML used by
content/current.yml.
"""

from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "current.yml"
PUBLIC = ROOT / "public"

WIDTH = 880
HEIGHT = 132

# Column geometry: x origin of each of the three editorial columns and the
# x position of the hairline separator that follows it.
COLUMNS_X = (28, 328, 610)
SEPARATORS_X = (306, 588)

# Max characters per column value before ellipsis. Values are rendered in a
# 15px semibold face; these limits keep every column inside its own track.
VALUE_MAX_CHARS = 28
LABEL_MAX_CHARS = 26

THEMES = {
    "light": {
        "file": "ticker.svg",
        "bg": "#ffffff",
        "bg_alt": "#f6f8fa",
        "border": "#d8dee4",
        "text": "#1f2328",
        "muted": "#59636e",
        "faint": "#e4e8ed",
        "accent": "#e5484d",
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
        "accent": "#ff6369",
        "cta_bg": "#e6edf3",
        "cta_text": "#0d1117",
    },
}

FONT = ("-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,"
        "Arial,'Liberation Sans',sans-serif")


def load_content():
    """Parse content/current.yml into a plain dict."""
    raw = CONTENT.read_text(encoding="utf-8")
    try:
        import yaml
    except ImportError:
        return _mini_yaml(raw)
    return yaml.safe_load(raw)


def _mini_yaml(raw):
    """Fallback parser: handles the flat maps + one list of maps we use."""
    data = {}
    stack = [(-1, data)]
    current_item = None
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        body = line.strip()

        if body.startswith("- "):
            parent = next(c for i, c in reversed(stack) if i < indent)
            current_item = {}
            parent.append(current_item) if isinstance(parent, list) else None
            body = body[2:].strip()
            key, _, value = body.partition(":")
            current_item[key.strip()] = _scalar(value.strip())
            continue

        while stack and stack[-1][0] >= indent:
            stack.pop()
        container = stack[-1][1]
        if isinstance(container, list):
            container = current_item

        key, _, value = body.partition(":")
        key, value = key.strip(), value.strip()
        if value == "":
            child = [] if key == "columns" else {}
            container[key] = child
            stack.append((indent, child))
        else:
            container[key] = _scalar(value)
    return data


def _scalar(value):
    value = value.strip()
    if value[:1] in "\"'" and value[:1] == value[-1:]:
        value = value[1:-1]
    if value.isdigit():
        return int(value)
    return value


def clip(text, limit):
    text = str(text)
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def text_el(x, y, content, fill, size, weight=400, spacing=0, anchor="start", opacity=None):
    attrs = [
        f'x="{x}"', f'y="{y}"',
        f'fill="{fill}"',
        f'font-size="{size}"',
        f'font-weight="{weight}"',
    ]
    if spacing:
        attrs.append(f'letter-spacing="{spacing}"')
    if anchor != "start":
        attrs.append(f'text-anchor="{anchor}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    return f'<text {" ".join(attrs)}>{escape(str(content))}</text>'


def build(theme_name, data):
    t = THEMES[theme_name]
    week = data.get("week", "")
    columns = data.get("columns", [])[:3]
    cta = data.get("cta", {}) or {}
    cta_text = clip(cta.get("text", "JOIN THE CONVERSATION"), 30)

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
        text_el(pill_x + pill_w / 2, 28, f"{cta_text}  →", t["cta_text"], 11, 700, spacing=1.2, anchor="middle")
    )

    # --- editorial columns ---------------------------------------------
    for x, column in zip(COLUMNS_X, columns):
        parts.append(
            text_el(x, 74, clip(column.get("label", ""), LABEL_MAX_CHARS).upper(),
                    t["muted"], 9.5, 700, spacing=1.4)
        )
        parts.append(
            text_el(x, 97, clip(column.get("value", ""), VALUE_MAX_CHARS),
                    t["text"], 15, 600)
        )

    for x in SEPARATORS_X:
        parts.append(f'<line x1="{x}" y1="64" x2="{x}" y2="102" stroke="{t["faint"]}"/>')

    # --- baseline ECG --------------------------------------------------
    # A flat trace with one beat, sliding slowly left to right along the
    # bottom edge: the card's "still alive" signal.
    beat = "M0 0h96l6-10 5 20 6-10h74"
    parts.append(
        f'<g clip-path="url(#card)">'
        f'<g transform="translate(0 111)">'
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
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" '
        f'aria-label="OpenAPI Pulse — week {week}">\n'
        f'  <title>OpenAPI Pulse — week {week}</title>\n'
        f'  <style>\n'
        f'    text {{ font-family: {FONT}; }}\n'
        f'    .dot, .ring {{ transform-box: fill-box; transform-origin: center; }}\n'
        f'    .dot {{ animation: beat 1.6s ease-in-out infinite; }}\n'
        f'    .ring {{ animation: halo 1.6s ease-out infinite; }}\n'
        f'    .trace {{ transform: translateX(24px); '
        f'animation: trace 9s linear infinite; }}\n'
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


def main():
    data = load_content()
    PUBLIC.mkdir(exist_ok=True)
    for name, theme in THEMES.items():
        out = PUBLIC / theme["file"]
        out.write_text(build(name, data), encoding="utf-8")
        print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
