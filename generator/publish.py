#!/usr/bin/env python3
"""
Publish the current Pulse edition as a post in GitHub Discussions.

    python3 generator/publish.py [--dry-run] [--force] [--rev SHA]

Renders templates/discussion.md with the content of content/current.yml and
opens a discussion in the category configured under `discussions:` there.

Two things GitHub does not let a script do, both worked around here:

  * **Categories cannot be created through the API.** There is no
    createDiscussionCategory mutation and no REST endpoint. The category has to
    be made once by hand; this script looks it up by name and stops with
    instructions if it is missing, rather than quietly posting somewhere else.

  * **Discussions cannot be pinned through the API.** Repository.pinnedDiscussions
    is readable, but no mutation writes it. So instead of pinning each new
    edition, one permanent discussion is pinned by hand and its number recorded
    as `discussions.index`; this script rewrites that post's body every run, so
    the pinned entry always points at the latest edition.

The card images are linked at the commit that produced them, not at `main`, so
an old edition keeps showing the card it was published with instead of silently
updating to today's.

Every edition also relays the Openapi blog: the article at the top of each
queue in content/blog.yml is posted as a short extract linking back to the full
piece — News into Announcements, API Insights into API Engineering. That relay
happens once per article, so what goes out is retired here rather than by
rotate.py: a failed relay leaves the entry at the top of its queue to be
retried on the next edition.
"""

import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import featured, featured_api, featured_topic, load_content  # noqa: E402
from blog import BADGES, FIELDS as BLOG_FIELDS  # noqa: E402
from pools import item_key, read_block, replace_block  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "templates" / "discussion.md"
RELAY_TEMPLATE = ROOT / "templates" / "blog-relay.md"
BLOG = ROOT / "content" / "blog.yml"

# queue → the blog category it comes from, for the credit line on the post.
BADGE_NAMES = {queue: badge for badge, queue in BADGES.items()}
GRAPHQL = "https://api.github.com/graphql"
RAW = "https://raw.githubusercontent.com/openapi/pulse"

TOKEN_VARS = ("PULSE_DISCUSSIONS_TOKEN", "GH_TOKEN", "GITHUB_TOKEN")


# --------------------------------------------------------------------------
# GitHub
# --------------------------------------------------------------------------

def token():
    import os
    for name in TOKEN_VARS:
        value = os.environ.get(name)
        if value:
            return value
    sys.exit(
        "no token found. Set one of: " + ", ".join(TOKEN_VARS) + "\n"
        "It needs write access to the discussions repository, which is a "
        "different repository from this one — so a workflow's built-in "
        "GITHUB_TOKEN is not enough."
    )


def graphql(query, variables=None):
    payload = json.dumps({"query": query, "variables": variables or {}}).encode()
    request = Request(GRAPHQL, data=payload, headers={
        "Authorization": f"Bearer {token()}",
        "User-Agent": "openapi-pulse",
        "Content-Type": "application/json",
    })
    try:
        with urlopen(request, timeout=30) as response:
            result = json.loads(response.read())
    except HTTPError as error:
        sys.exit(f"GitHub API {error.code}: {error.read().decode()[:400]}")
    except (URLError, OSError) as error:
        sys.exit(f"cannot reach the GitHub API: {error}")

    if "errors" in result:
        messages = "; ".join(e.get("message", "?") for e in result["errors"])
        sys.exit(f"GitHub API: {messages}")
    return result["data"]


REPO_QUERY = """
query($owner: String!, $name: String!) {
  repository(owner: $owner, name: $name) {
    id
    discussionCategories(first: 50) { nodes { id name } }
  }
}
"""

EXISTING_QUERY = """
query($owner: String!, $name: String!, $category: ID!) {
  repository(owner: $owner, name: $name) {
    discussions(first: 25, categoryId: $category,
                orderBy: {field: CREATED_AT, direction: DESC}) {
      nodes { number title url }
    }
  }
}
"""

DISCUSSION_QUERY = """
query($owner: String!, $name: String!, $number: Int!) {
  repository(owner: $owner, name: $name) {
    discussion(number: $number) { id title url }
  }
}
"""

CREATE_MUTATION = """
mutation($repo: ID!, $category: ID!, $title: String!, $body: String!) {
  createDiscussion(input: {repositoryId: $repo, categoryId: $category,
                           title: $title, body: $body}) {
    discussion { number url }
  }
}
"""

UPDATE_MUTATION = """
mutation($id: ID!, $body: String!) {
  updateDiscussion(input: {discussionId: $id, body: $body}) {
    discussion { number url }
  }
}
"""


def resolve_category(owner, name, wanted, required=True):
    """The repository id and the id of the category named `wanted`.

    With `required=False` a missing category comes back as None instead of
    stopping the run: the blog relay is an extra, and one missing category
    there must not take the edition itself down with it.
    """
    data = graphql(REPO_QUERY, {"owner": owner, "name": name})["repository"]
    if data is None:
        sys.exit(f"repository {owner}/{name} not found, or the token cannot see it")

    categories = data["discussionCategories"]["nodes"]
    for category in categories:
        if category["name"].lower() == wanted.lower():
            return data["id"], category["id"]

    available = ", ".join(c["name"] for c in categories)
    if not required:
        print(f'  ! no discussion category named "{wanted}" in {owner}/{name} '
              f"— create it at https://github.com/{owner}/{name}/discussions/"
              f"categories and it goes out with the next edition")
        print(f"    existing categories: {available}")
        return data["id"], None
    sys.exit(
        f'no discussion category named "{wanted}" in {owner}/{name}.\n'
        f"Existing categories: {available}\n"
        "Categories cannot be created through the GitHub API. Create it once at\n"
        f"  https://github.com/{owner}/{name}/discussions/categories"
    )


# --------------------------------------------------------------------------
# post body
# --------------------------------------------------------------------------

def full_stop(text):
    """The library writes its pitches as labels, half of them without a stop."""
    text = str(text).strip()
    return text + "." if text and text[-1] not in ".!?:" else text


def sentence_case(text):
    """"JOIN THE COMMUNITY" reads as shouting in prose; the card can shout."""
    text = str(text).strip()
    return text[:1].upper() + text[1:].lower()


def head_revision():
    """The commit the card images should be linked at."""
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT,
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "main"


def category_url(owner, name, category):
    slug = "-".join(str(category).lower().split())
    return f"https://github.com/{owner}/{name}/discussions/categories/{slug}"


def from_the_blog(data):
    """The two blog articles this edition relays, as a section of the post.

    The edition links the articles themselves rather than the posts that relay
    them: those are created after this body is rendered, and the blog is where
    the piece actually lives. The card says nothing about any of this — it has
    four tracks and they belong to the community, not to the blog.

    A queue that has run dry simply drops its line, and if both are empty the
    whole section disappears.
    """
    settings = data.get("blog", {}) or {}
    mapping = settings.get("relay", {}) or {}
    owner, _, name = (data.get("discussions", {}) or {}).get(
        "repo", "openapi/discussions").partition("/")

    lines = []
    for queue, category in mapping.items():
        waiting = blog_queue(queue)
        if not waiting:
            continue
        article = waiting[0]
        lines.append(
            f"**[{article['title']}]({article['url']})** — from "
            f"*{BADGE_NAMES.get(queue, queue)}* on the "
            f"[Openapi blog](https://openapi.com/blog), relayed in full to "
            f"[{category}]({category_url(owner, name, category)}).")

    if not lines:
        return ""
    return "### 📰 From the blog\n\n" + "\n\n".join(lines) + "\n"


def render(data, revision):
    developer = featured(data, "developers")
    contributor = featured(data, "contributors")
    api = featured_api()
    topic = featured_topic()
    cta = data.get("cta", {}) or {}

    values = {
        "week": data.get("week", ""),
        "year": data.get("year", ""),
        "date": date.today().isoformat(),
        "api_name": api.get("name", ""),
        "api_url": api.get("url", ""),
        "api_about": full_stop(api.get("about", "")),
        "developer": developer,
        "contributor": contributor,
        "discussion_title": topic.get("title", ""),
        "discussion_url": topic.get("url", ""),
        "from_the_blog": from_the_blog(data),
        "cta_text": sentence_case(cta.get("text", "JOIN THE COMMUNITY")),
        "cta_url": cta.get("url", ""),
        "card_light": f"{RAW}/{revision}/public/ticker.svg",
        "card_dark": f"{RAW}/{revision}/public/ticker-dark.svg",
    }

    body = TEMPLATE.read_text(encoding="utf-8")
    for key, value in values.items():
        body = body.replace("{{" + key + "}}", str(value))
    # A field the source left empty — an API with no pitch, a drained blog
    # queue — leaves a hole where its paragraph was. Close it rather than
    # publishing the gap.
    return re.sub(r"\n{3,}", "\n\n", body)


def index_body(data, edition_url, revision):
    """Body for the permanent pinned discussion: a pointer to the latest one."""
    week = data.get("week", "")
    return (
        f'<p align="center">\n'
        f'  <a href="{edition_url}">\n'
        f"    <picture>\n"
        f'      <source media="(prefers-color-scheme: dark)" '
        f'srcset="{RAW}/{revision}/public/ticker-dark.svg">\n'
        f'      <source media="(prefers-color-scheme: light)" '
        f'srcset="{RAW}/{revision}/public/ticker.svg">\n'
        f'      <img alt="Openapi Pulse" src="{RAW}/{revision}/public/ticker.svg">\n'
        f"    </picture>\n"
        f"  </a>\n"
        f"</p>\n\n"
        f"The Openapi ecosystem publishes an edition of the **Pulse** on a "
        f"regular beat: the API worth a look, the people building and "
        f"contributing, and the discussion worth joining.\n\n"
        f"### 👉 Latest edition: [{title_for(data)}]({edition_url})\n\n"
        f"Every past edition is collected in the "
        f"[Openapi Pulse category]"
        f"(https://github.com/openapi/discussions/discussions/categories/openapi-pulse).\n\n"
        f"<sub>This post is kept up to date automatically by "
        f"[openapi/pulse](https://github.com/openapi/pulse) — currently "
        f"pointing at edition {week}. Do not edit it by hand.</sub>\n"
    )


def title_for(data):
    return f"Openapi Pulse — Edition {data.get('week', '')}"


# --------------------------------------------------------------------------
# the blog relay
# --------------------------------------------------------------------------

def blog_queue(queue):
    """The articles waiting in one queue of content/blog.yml, top first."""
    lines = BLOG.read_text(encoding="utf-8").splitlines()
    _, _, items = read_block(lines, queue, required=False)
    return [{field: item_key(item, field) for field in BLOG_FIELDS}
            for item in items]


def relayed_editions(queue):
    """The editions in which this queue has already sent something out."""
    lines = BLOG.read_text(encoding="utf-8").splitlines()
    _, _, items = read_block(lines, "relayed", required=False)
    return {item_key(item, "edition") for item in items
            if item_key(item, "queue") == queue}


def retire(queue, slug, edition):
    """Move a relayed article out of its queue and into `relayed:`.

    Rotation is what the other queues do — they turn, and everything comes
    round again. An article does not: it is relayed once. So this is a removal,
    and it is done here, by whatever actually posted it, rather than by
    rotate.py — which would retire an article the relay never managed to send.

    The edition is recorded with the slug, which is what makes running this
    script twice in one edition harmless: without it a second run would find
    the *next* article at the top of the queue and cheerfully send that out
    too.
    """
    lines = BLOG.read_text(encoding="utf-8").splitlines()

    start, end, items = read_block(lines, queue, required=False)
    if start is None:
        return
    kept = [item for item in items if item_key(item, "slug") != slug]
    if len(kept) == len(items):
        return
    replace_block(lines, start, end, kept)

    start, end, items = read_block(lines, "relayed", required=False)
    if start is not None:
        replace_block(lines, start, end, items + [[
            f"  - slug: {slug}",
            f"    queue: {queue}",
            f"    edition: {edition}",
        ]])

    BLOG.write_text("\n".join(lines) + "\n", encoding="utf-8")


def render_relay(article, data, badge):
    values = {
        "title": article.get("title", ""),
        "url": article.get("url", ""),
        "date": article.get("date", ""),
        "excerpt": full_stop(article.get("excerpt", "")),
        "badge": badge,
        "week": data.get("week", ""),
    }
    body = RELAY_TEMPLATE.read_text(encoding="utf-8")
    for key, value in values.items():
        body = body.replace("{{" + key + "}}", str(value))
    return body.lstrip("\n")


def relay_blog(data, owner, name, dry_run=False, force=False):
    """Relay the head of each blog queue into its discussion category.

    One article per queue per edition. Everything here is best-effort: the
    edition itself has already gone out, and a blog that cannot be reached or a
    category that does not exist yet must not turn a published edition into a
    failed run.
    """
    settings = data.get("blog", {}) or {}
    mapping = settings.get("relay", {}) or {}
    if not mapping:
        return

    edition = str(data.get("week", ""))

    print("\nblog relay:")
    for queue, category_name in mapping.items():
        badge = BADGE_NAMES.get(queue, queue)
        if not dry_run and edition in relayed_editions(queue):
            print(f"  {queue}: already relayed in edition {edition} — "
                  f"nothing more goes out until the queues advance")
            continue

        waiting = blog_queue(queue)
        if not waiting:
            print(f"  {queue}: nothing waiting — nothing to relay")
            continue

        article = waiting[0]
        title = article.get("title", "")
        body = render_relay(article, data, badge)

        if dry_run:
            print(f"  {queue} → {category_name}: {title}\n")
            print(body)
            continue

        repo_id, category_id = resolve_category(
            owner, name, category_name, required=False)
        if category_id is None:
            continue

        existing = graphql(EXISTING_QUERY, {
            "owner": owner, "name": name, "category": category_id,
        })["repository"]["discussions"]["nodes"]
        clash = next((d for d in existing if d["title"] == title), None)
        if clash and not force:
            print(f"  {queue}: already relayed as {clash['url']} — retiring it")
            retire(queue, article["slug"], edition)
            continue

        created = graphql(CREATE_MUTATION, {
            "repo": repo_id, "category": category_id,
            "title": title, "body": body,
        })["createDiscussion"]["discussion"]
        print(f"  {queue} → {category_name}: {title}\n"
              f"    {created['url']}")
        retire(queue, article["slug"], edition)


# --------------------------------------------------------------------------

def main():
    dry_run = "--dry-run" in sys.argv
    force = "--force" in sys.argv
    revision = "main"
    if "--rev" in sys.argv:
        revision = sys.argv[sys.argv.index("--rev") + 1]
    elif not dry_run:
        revision = head_revision()

    data = load_content()
    settings = data.get("discussions", {}) or {}
    owner, _, name = settings.get("repo", "openapi/discussions").partition("/")
    category_name = settings.get("category", "Openapi Pulse")

    title = title_for(data)
    body = render(data, revision)

    if dry_run:
        print(f"# {title}\n\ncategory: {category_name} in {owner}/{name}\n")
        print(body)
        relay_blog(data, owner, name, dry_run=True)
        return

    repo_id, category_id = resolve_category(owner, name, category_name)

    existing = graphql(EXISTING_QUERY, {
        "owner": owner, "name": name, "category": category_id,
    })["repository"]["discussions"]["nodes"]
    clash = next((d for d in existing if d["title"] == title), None)
    if clash and not force:
        print(f"edition {data.get('week')} is already published: {clash['url']}")
        print("nothing to post again (pass --force to repost it)")
        # The relay still runs: the edition going out and the blog going out
        # are two separate things, and a rerun after a half-failed edition is
        # exactly when the relay needs its second chance.
        relay_blog(data, owner, name)
        return

    created = graphql(CREATE_MUTATION, {
        "repo": repo_id, "category": category_id, "title": title, "body": body,
    })["createDiscussion"]["discussion"]
    print(f"published {title} → {created['url']}")

    update_index(data, settings, owner, name, created["url"], revision)
    relay_blog(data, owner, name, force=force)


def update_index(data, settings, owner, name, edition_url, revision):
    number = settings.get("index")
    if number in (None, "", "null"):
        print(
            "\nno pinned index configured. GitHub has no API for pinning a "
            "discussion, so to keep one always-visible entry point:\n"
            f"  1. open a discussion in {owner}/{name} (any title, e.g. "
            '"Openapi Pulse")\n'
            "  2. pin it by hand — once, forever\n"
            "  3. put its number in content/current.yml under discussions.index\n"
            "From then on this script rewrites its body at every edition."
        )
        return

    discussion = graphql(DISCUSSION_QUERY, {
        "owner": owner, "name": name, "number": int(number),
    })["repository"]["discussion"]
    if discussion is None:
        sys.exit(f"discussions.index points at #{number}, which does not exist "
                 f"in {owner}/{name}")

    graphql(UPDATE_MUTATION, {
        "id": discussion["id"],
        "body": index_body(data, edition_url, revision),
    })
    print(f"pinned index #{number} now points at this edition: {discussion['url']}")


if __name__ == "__main__":
    main()
