#!/usr/bin/env python3
"""
Advance the Pulse Card by one week.

    python3 generator/rotate.py [--dry-run]

Bumps `week` in content/current.yml and rotates the `developers` and
`contributors` lists: the nickname currently on the card moves to the tail, the
next one takes its place. Everyone gets a turn before anyone repeats, and the
running order stays visible and editable in the file itself — to feature
someone sooner, move them to the top by hand.

The file is edited line by line rather than reserialised, so comments and
formatting survive.
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content" / "current.yml"
LISTS = ("developers", "contributors")
LAST_WEEK_OF_YEAR = 52

ITEM = re.compile(r"^\s*-\s+\S")


def bump_week(lines):
    """Advance `week`, rolling over into the next year after week 52."""
    week = year = None
    for i, line in enumerate(lines):
        match = re.match(r"^week:\s*(\d+)\s*$", line)
        if match:
            week = (i, int(match.group(1)))
        match = re.match(r"^year:\s*(\d+)\s*$", line)
        if match:
            year = (i, int(match.group(1)))

    if week is None:
        sys.exit("content/current.yml: no top-level `week:` key found")

    index, value = week
    new_value = value + 1
    if new_value > LAST_WEEK_OF_YEAR:
        new_value = 1
        if year is not None:
            y_index, y_value = year
            lines[y_index] = f"year: {y_value + 1}"
    lines[index] = f"week: {new_value}"
    return value, new_value


def rotate_list(lines, key):
    """Move the first entry of `key` to the end of its block."""
    try:
        start = next(i for i, line in enumerate(lines)
                     if re.match(rf"^{key}:\s*$", line))
    except StopIteration:
        sys.exit(f"content/current.yml: no top-level `{key}:` list found")

    items = []
    i = start + 1
    while i < len(lines) and ITEM.match(lines[i]):
        items.append(i)
        i += 1

    if len(items) < 2:
        print(f"  {key}: fewer than two entries, nothing to rotate")
        return None, None

    first, rest = lines[items[0]], [lines[j] for j in items[1:]]
    lines[items[0]:items[-1] + 1] = rest + [first]

    outgoing = first.split("-", 1)[1].strip()
    incoming = rest[0].split("-", 1)[1].strip()
    return outgoing, incoming


def main():
    dry_run = "--dry-run" in sys.argv
    lines = CONTENT.read_text(encoding="utf-8").splitlines()

    old_week, new_week = bump_week(lines)
    print(f"week {old_week} → {new_week}")
    for key in LISTS:
        outgoing, incoming = rotate_list(lines, key)
        if incoming:
            print(f"  {key}: @{outgoing} → @{incoming}")

    if dry_run:
        print("\n--dry-run: content/current.yml left untouched")
        return

    CONTENT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nupdated {CONTENT.relative_to(ROOT)}")

    build = Path(__file__).resolve().parent / "build.py"
    subprocess.run([sys.executable, str(build)], check=True)


if __name__ == "__main__":
    main()
