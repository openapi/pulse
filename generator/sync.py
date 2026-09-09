#!/usr/bin/env python3
"""
Sync the rotation pools in content/current.yml with their sources of truth.

    python3 generator/sync.py [--dry-run]

    developers   ← public members of the Openapi organization
                   https://github.com/orgs/openapi/people
    contributors ← the self-declared registry
                   https://github.com/openapi/contributors

Membership belongs upstream; the *running order* belongs here. So this merges
rather than overwrites: nicknames already in a pool keep their position, new
ones are appended to the tail — entering the rotation behind everyone already
queued instead of jumping the line — and nicknames that disappeared upstream
are dropped.

Anyone listed under `exclude` in content/current.yml is filtered out of both
pools regardless of what the sources say.

Run it before generator/rotate.py. It never picks who is featured: that is
still whoever sits at the head of the list.
"""

import json
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "current.yml"

ORG = "openapi"
MEMBERS_API = f"https://api.github.com/orgs/{ORG}/members?per_page=100"
CONTRIBUTORS_README = (
    f"https://raw.githubusercontent.com/{ORG}/contributors/main/README.md"
)

ITEM = re.compile(r"^\s*-\s+\S")
COMMENT_BLOCK = re.compile(r"<!--.*?-->", re.DOTALL)
AVATAR_LINK = re.compile(r"https://github\.com/([A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)\.png")


def fetch(url, accept="application/vnd.github+json"):
    request = Request(url, headers={
        "User-Agent": "openapi-pulse-card",
        "Accept": accept,
    })
    try:
        with urlopen(request, timeout=15) as response:
            return response.read().decode("utf-8")
    except (URLError, HTTPError, OSError) as error:
        sys.exit(f"cannot reach {url}: {error}")


def fetch_developers():
    """Public members of the organization, in the order GitHub returns them."""
    payload = json.loads(fetch(MEMBERS_API))
    if isinstance(payload, dict):
        sys.exit(f"GitHub API: {payload.get('message', 'unexpected response')}")
    return [user["login"] for user in payload]


def fetch_contributors():
    """Nicknames declared in the openapi/contributors README table.

    Avatars in that table are linked as https://github.com/<user>.png, which
    makes them the most reliable thing to key on. HTML comments are stripped
    first so the "how to add yourself" row template is not picked up.
    """
    readme = COMMENT_BLOCK.sub("", fetch(CONTRIBUTORS_README, accept="text/plain"))
    seen = []
    for nickname in AVATAR_LINK.findall(readme):
        if nickname not in seen:
            seen.append(nickname)
    return seen


def read_pool(lines, key, required=True):
    """Return (start index, item indices, current nicknames) for a list block."""
    try:
        start = next(i for i, line in enumerate(lines)
                     if re.match(rf"^{key}:\s*$", line))
    except StopIteration:
        if not required:
            return None, [], []
        sys.exit(f"content/current.yml: no top-level `{key}:` list found")

    indices = []
    i = start + 1
    while i < len(lines) and ITEM.match(lines[i]):
        indices.append(i)
        i += 1
    return start, indices, [lines[j].split("-", 1)[1].strip() for j in indices]


def merge(current, upstream):
    """Keep the established order, append newcomers, drop who left."""
    upstream_set = set(upstream)
    kept = [n for n in current if n in upstream_set]
    added = [n for n in upstream if n not in set(current)]
    removed = [n for n in current if n not in upstream_set]
    return kept + added, added, removed


def apply_pool(lines, key, nicknames):
    start, indices, _ = read_pool(lines, key)
    block = [f"  - {n}" for n in nicknames]
    if indices:
        lines[indices[0]:indices[-1] + 1] = block
    else:
        lines[start + 1:start + 1] = block


def main():
    dry_run = "--dry-run" in sys.argv
    lines = CONTENT.read_text(encoding="utf-8").splitlines()

    sources = {
        "developers": (fetch_developers, "organization members"),
        "contributors": (fetch_contributors, "contributors registry"),
    }

    _, _, excluded = read_pool(lines, "exclude", required=False)
    if excluded:
        print("excluded: " + ", ".join(f"@{n}" for n in excluded))

    changed = False
    for key, (fetcher, description) in sources.items():
        upstream = [n for n in fetcher() if n not in excluded]
        _, _, current = read_pool(lines, key)
        merged, added, removed = merge(current, upstream)

        print(f"{key}: {len(merged)} from the {description}")
        for nickname in added:
            print(f"  + @{nickname} (queued at the end of the rotation)")
        for nickname in removed:
            print(f"  - @{nickname} (no longer listed upstream)")
        if not added and not removed:
            print("  already in sync")

        if merged != current:
            changed = True
            apply_pool(lines, key, merged)

    if dry_run:
        print("\n--dry-run: content/current.yml left untouched")
        return
    if not changed:
        print("\nnothing to write")
        return

    CONTENT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nupdated {CONTENT.relative_to(ROOT)} — "
          f"run generator/build.py to regenerate the card")


if __name__ == "__main__":
    main()
