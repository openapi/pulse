#!/usr/bin/env python3
"""
Read the Openapi blog and turn its cards into queue entries.

    https://openapi.com/blog

The blog is the one place where the Openapi ecosystem already publishes
editorial content, and Discussions is where the community reads. Every edition
of the Pulse relays the top of each queue built here into its own category:

    blog category "News"          → discussions category "Announcements"
    blog category "API Insights"  → discussions category "API Engineering"

The relay is deliberately an *extract*: title, cover, the blog's own summary
and a link back. The article stays where it was written; Discussions gets the
pointer and the conversation.

There is no feed — no RSS, no JSON, the pages are server-rendered — so the
listing markup is what there is to read. Each card carries its category in a
`badge` span, the article link in the `card-title` heading, the date in a
`text-serif` strong and the summary in `card-text`. If that structure ever
changes the parse yields nothing and the caller stops loudly rather than
quietly emptying a queue.
"""

import html
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BLOG = "https://openapi.com/blog"

# Blog category → the queue it feeds in content/blog.yml. Everything the blog
# publishes under any other category (Webinar, Awards, CSR, …) is left alone:
# the Pulse relays what is either an announcement or engineering material.
BADGES = {
    "News": "news",
    "API Insights": "insights",
}

# How many listing pages to read. The queues drain faster than the blog fills
# them, so one page would be enough; two keeps a little slack for a burst of
# posts between two editions.
PAGES = 2

BADGE = re.compile(r'<span class="badge[^"]*">\s*(.*?)\s*</span>')
TITLE = re.compile(
    r'<h2 class="card-title[^"]*">\s*<a href="([^"]+)"[^>]*>(.*?)</a>', re.DOTALL)
DATE = re.compile(r'<strong class="text-serif">\s*(.*?)\s*</strong>', re.DOTALL)
EXCERPT = re.compile(
    r'<p class="card-text">\s*(?:<a[^>]*>)?(.*?)(?:</a>)?\s*</p>', re.DOTALL)
IMAGE = re.compile(r'<img src="([^"]+)"')
TAG = re.compile(r"<[^>]+>")


def fetch(url):
    request = Request(url, headers={
        "User-Agent": "openapi-pulse",
        "Accept": "text/html",
    })
    try:
        with urlopen(request, timeout=30) as response:
            return response.read().decode("utf-8", errors="replace")
    except (URLError, HTTPError, OSError) as error:
        sys.exit(f"cannot reach {url}: {error}")


def text(raw):
    """Card fields carry markup and entities; queue entries carry one line."""
    return " ".join(html.unescape(TAG.sub("", raw)).split())


def parse(page):
    """Every card on one listing page, in the order the blog lists them."""
    posts = []
    for badge in BADGE.finditer(page):
        # The card is everything from its category badge up to the next one;
        # the cover sits just above the badge, so it is looked for backwards.
        card = page[badge.end():badge.end() + 4000]
        title = TITLE.search(card)
        if not title:
            continue
        url, heading = title.group(1), text(title.group(2))
        if not heading:
            continue
        date = DATE.search(card)
        excerpt = EXCERPT.search(card)
        image = IMAGE.findall(page[max(0, badge.start() - 2000):badge.start()])
        posts.append({
            "badge": text(badge.group(1)),
            "slug": url.rstrip("/").rsplit("/", 1)[-1],
            "title": heading,
            "date": text(date.group(1)) if date else "",
            "url": url if url.startswith("http") else "https://openapi.com" + url,
            "image": image[-1] if image else "",
            "excerpt": text(excerpt.group(1)) if excerpt else "",
        })
    return posts


def fetch_posts(pages=PAGES):
    """The blog, newest first, deduplicated across pages.

    Only the categories in BADGES come back, each tagged with the queue it
    belongs to. Pagination is `?page=N`, page 1 being the bare /blog.
    """
    posts, seen = [], set()
    for number in range(1, pages + 1):
        url = BLOG if number == 1 else f"{BLOG}?page={number}"
        found = parse(fetch(url))
        if not found:
            sys.exit(
                f"no blog cards found at {url} — the listing markup may have "
                f"changed; check the selectors in generator/blog.py")
        for post in found:
            queue = BADGES.get(post["badge"])
            if queue is None or post["slug"] in seen:
                continue
            seen.add(post["slug"])
            posts.append(dict(post, queue=queue))
    return posts


def entry_lines(post):
    """A post as the lines of one queue item.

    The queue files are edited as text, never reserialised, so a record is
    written the way the rest of content/ writes one: `- ` then one `key: value`
    per line, values plain and single-line. Blog titles routinely contain a
    colon; the pool reader splits on the first one, so that survives.
    """
    return [
        f"  - slug: {post['slug']}",
        f"    date: {post['date']}",
        f"    title: {post['title']}",
        f"    url: {post['url']}",
        f"    image: {post['image']}",
        f"    excerpt: {post['excerpt']}",
    ]


FIELDS = ("slug", "date", "title", "url", "image", "excerpt")


if __name__ == "__main__":
    for post in fetch_posts():
        print(f"[{post['queue']:>8}] {post['date']}  {post['title']}")
