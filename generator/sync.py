#!/usr/bin/env python3
"""
Sync the rotation queues with their sources of truth.

    python3 generator/sync.py [--dry-run]

    developers   ← public members of the Openapi organization
                   https://github.com/orgs/openapi/people
    contributors ← the self-declared registry
                   https://github.com/openapi/contributors
    apis         ← the public API library
                   https://console.openapi.com/apis

Membership belongs upstream; the *running order* belongs here. So this merges
rather than overwrites: entries already in a queue keep their position, new
ones are appended to the bottom — queueing behind everything already waiting
instead of jumping the line — and entries that disappeared upstream are
dropped.

Anyone listed under `exclude` in content/current.yml is filtered out of the
people queues regardless of what the sources say.

This never decides what goes out next: that is whatever sits at the top of each
queue, which is yours to reorder by hand.
"""

import html
import json
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pools import item_key, read_block, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CURRENT = ROOT / "content" / "current.yml"
APIS = ROOT / "content" / "apis.yml"

ORG = "openapi"
MEMBERS_API = f"https://api.github.com/orgs/{ORG}/members?per_page=100"
CONTRIBUTORS_README = (
    f"https://raw.githubusercontent.com/{ORG}/contributors/main/README.md"
)
API_LIBRARY = "https://console.openapi.com/apis"

COMMENT_BLOCK = re.compile(r"<!--.*?-->", re.DOTALL)
AVATAR_LINK = re.compile(
    r"https://github\.com/([A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)\.png")
API_BOX = re.compile(
    r'<div id="([A-Za-z0-9_-]+)"\s+class="[^"]*\bapiBox\b[^"]*"'
    r'.*?<h4[^>]*>\s*(.*?)\s*</h4>',
    re.DOTALL)


def fetch(url, accept="application/vnd.github+json"):
    request = Request(url, headers={
        "User-Agent": "openapi-pulse",
        "Accept": accept,
    })
    try:
        with urlopen(request, timeout=20) as response:
            return response.read().decode("utf-8", errors="replace")
    except (URLError, HTTPError, OSError) as error:
        sys.exit(f"cannot reach {url}: {error}")


# --------------------------------------------------------------------------
# sources
# --------------------------------------------------------------------------

def fetch_developers():
    """Public members of the organization, in the order GitHub returns them."""
    payload = json.loads(fetch(MEMBERS_API))
    if isinstance(payload, dict):
        sys.exit(f"GitHub API: {payload.get('message', 'unexpected response')}")
    return [(user["login"], [f"  - {user['login']}"]) for user in payload]


def fetch_contributors():
    """Handles declared in the openapi/contributors README table.

    Avatars in that table are linked as https://github.com/<user>.png, which
    makes them the most reliable thing to key on. HTML comments are stripped
    first so the "how to add yourself" row template is not picked up.
    """
    readme = COMMENT_BLOCK.sub("", fetch(CONTRIBUTORS_README, accept="text/plain"))
    seen = []
    for handle in AVATAR_LINK.findall(readme):
        if handle not in seen:
            seen.append(handle)
    return [(handle, [f"  - {handle}"]) for handle in seen]


def fetch_apis():
    """The API library, scraped from the console.

    The page is server-rendered, one `apiBox` div per API carrying the slug as
    its id and the display name in the heading. There is no public JSON feed
    for this list, so the markup is what there is to read.
    """
    page = fetch(API_LIBRARY, accept="text/html")
    found = []
    for slug, name in API_BOX.findall(page):
        found.append((slug, [
            f"  - slug: {slug}",
            f"    name: {html.unescape(name).strip()}",
            f"    url: {API_LIBRARY}/{slug}/info",
        ]))
    if not found:
        sys.exit(f"no APIs found at {API_LIBRARY} — the page markup may have "
                 f"changed; check the apiBox selector in fetch_apis()")
    return found


# --------------------------------------------------------------------------

def merge(current_keys, upstream):
    """Keep the established order, append newcomers, drop what left."""
    upstream_map = dict(upstream)
    kept = [k for k in current_keys if k in upstream_map]
    added = [k for k, _ in upstream if k not in set(current_keys)]
    removed = [k for k in current_keys if k not in upstream_map]
    return kept + added, added, removed


def sync_pool(path, lines, key, field, fetcher, description, exclude=()):
    upstream = [(k, v) for k, v in fetcher() if k not in exclude]
    start, end, items = read_block(lines, key)
    by_key = {item_key(item, field): item for item in items}
    current_keys = [item_key(item, field) for item in items]

    order, added, removed = merge(current_keys, upstream)
    upstream_map = dict(upstream)

    print(f"{key}: {len(order)} from the {description} ({path.name})")
    for entry in added:
        print(f"  + {entry} (queued at the bottom)")
    for entry in removed:
        print(f"  - {entry} (no longer listed upstream)")
    if not added and not removed:
        print("  already in sync")

    if order == current_keys:
        return False
    replace_block(lines, start, end,
                  [by_key.get(k) or upstream_map[k] for k in order])
    return True


def main():
    dry_run = "--dry-run" in sys.argv

    current_lines = CURRENT.read_text(encoding="utf-8").splitlines()
    api_lines = APIS.read_text(encoding="utf-8").splitlines()

    _, _, excluded_items = read_block(current_lines, "exclude", required=False)
    excluded = [item_key(item) for item in excluded_items]
    if excluded:
        print("excluded: " + ", ".join(f"@{n}" for n in excluded))

    changed_current = False
    for key, fetcher, description in (
        ("developers", fetch_developers, "organization members"),
        ("contributors", fetch_contributors, "contributors registry"),
    ):
        changed_current |= sync_pool(CURRENT, current_lines, key, None,
                                     fetcher, description, exclude=excluded)

    changed_apis = sync_pool(APIS, api_lines, "apis", "slug",
                             fetch_apis, "API library")

    if dry_run:
        print("\n--dry-run: nothing written")
        return

    wrote = []
    if changed_current:
        CURRENT.write_text("\n".join(current_lines) + "\n", encoding="utf-8")
        wrote.append(CURRENT.relative_to(ROOT))
    if changed_apis:
        APIS.write_text("\n".join(api_lines) + "\n", encoding="utf-8")
        wrote.append(APIS.relative_to(ROOT))

    print("\n" + (f"updated {', '.join(str(p) for p in wrote)}"
                  if wrote else "nothing to write"))


if __name__ == "__main__":
    main()
