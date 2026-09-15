#!/usr/bin/env python3
"""
Advance the queues by one edition.

    python3 generator/rotate.py [--dry-run]

Moves the top entry of every queue —
developers, contributors, apis, topics — to the bottom, so the next one comes up and
nobody repeats until the whole queue has had a turn.

Run this *after* publishing, not before. The top of each queue is what goes out
**next**, which is what makes curating it a single gesture: move an entry to the
top and it is on the next card. That only holds if rotation happens once the
current edition is already out.

For the same reason this does not regenerate the SVGs. The card in public/ has
to keep showing the edition that was published until the next one is built.

The blog queues in content/blog.yml are not touched here at all: they do not
rotate. An article is relayed once, so publish.py retires what it actually
posted — see the blog relay in the README.

The files are edited line by line rather than reserialised, so comments and
hand-chosen ordering survive.
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pools import item_key, read_block, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
CURRENT = ROOT / "content" / "current.yml"
APIS = ROOT / "content" / "apis.yml"
TOPICS = ROOT / "content" / "topics.yml"
def rotate(lines, key, field=None):
    """Move the top entry of a queue to the bottom."""
    start, end, items = read_block(lines, key)
    if len(items) < 2:
        print(f"  {key}: fewer than two entries, nothing to rotate")
        return False

    outgoing, incoming = item_key(items[0], field), item_key(items[1], field)
    replace_block(lines, start, end, items[1:] + [items[0]])
    print(f"  {key}: {outgoing} → {incoming}")
    return True


def main():
    dry_run = "--dry-run" in sys.argv

    current_lines = CURRENT.read_text(encoding="utf-8").splitlines()
    api_lines = APIS.read_text(encoding="utf-8").splitlines()
    topic_lines = TOPICS.read_text(encoding="utf-8").splitlines()

    rotate(current_lines, "developers")
    rotate(current_lines, "contributors")
    rotate(api_lines, "apis", field="slug")
    rotate(topic_lines, "topics", field="short")

    if dry_run:
        print("\n--dry-run: nothing written")
        return

    CURRENT.write_text("\n".join(current_lines) + "\n", encoding="utf-8")
    APIS.write_text("\n".join(api_lines) + "\n", encoding="utf-8")
    TOPICS.write_text("\n".join(topic_lines) + "\n", encoding="utf-8")
    print("\nupdated the queues in content/ — "
          "run generator/build.py at the start of the next edition")


if __name__ == "__main__":
    main()
