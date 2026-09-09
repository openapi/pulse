#!/usr/bin/env python3
"""
Text-level editing of the ordered pools in content/*.yml.

The pools are queues a human curates: the entry at the top is the one going out
next. Both sync.py and rotate.py rewrite them, and both have to leave the
comments, the spacing and the hand-chosen order of everything they did not
touch exactly as they found it — so the files are edited as lines rather than
parsed and re-serialised.

An item is its `- ` line plus any following lines indented deeper, which lets a
pool hold either bare handles or multi-line records:

    developers:
      - octocat

    apis:
      - slug: geocoding
        name: Geocoding
"""

import re
import sys

BULLET = re.compile(r"^(\s*)-\s+(.*)$")


def indent_of(line):
    return len(line) - len(line.lstrip())


def read_block(lines, key, required=True):
    """Locate a top-level list and split it into items.

    Returns (start, end, items) where `lines[start:end]` is the item block and
    `items` is a list of line-lists. For a missing optional key, returns
    (None, None, []).
    """
    try:
        header = next(i for i, line in enumerate(lines)
                      if re.match(rf"^{re.escape(key)}:\s*$", line))
    except StopIteration:
        if required:
            sys.exit(f"no top-level `{key}:` list found")
        return None, None, []

    items = []
    i = header + 1
    while i < len(lines):
        match = BULLET.match(lines[i])
        if not match:
            break
        bullet_indent = indent_of(lines[i])
        item = [lines[i]]
        i += 1
        # Continuation lines belong to the item while they stay indented deeper
        # than its bullet and are not a new bullet at the same level.
        while i < len(lines) and lines[i].strip() and not BULLET.match(lines[i]) \
                and indent_of(lines[i]) > bullet_indent:
            item.append(lines[i])
            i += 1
        items.append(item)

    return header + 1, i, items


def item_key(item, field=None):
    """The identity of an item: its scalar value, or one of its fields."""
    first = BULLET.match(item[0]).group(2).strip()
    if field is None:
        return first.split("#", 1)[0].strip()

    for line in item:
        text = BULLET.match(line).group(2) if BULLET.match(line) else line
        name, sep, value = text.partition(":")
        if sep and name.strip() == field:
            return value.strip().strip("\"'")
    return first


def replace_block(lines, start, end, items):
    """Swap the item block for a new ordering, flattened back to lines."""
    flat = [line for item in items for line in item]
    lines[start:end] = flat
    return len(flat) - (end - start)
