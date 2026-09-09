# Openapi Pulse

> **The heartbeat of the Openapi open-source ecosystem.**

<p align="center">
  <a href="https://github.com/orgs/openapi/discussions">
    <picture>
      <source media="(prefers-color-scheme: dark)"
              srcset="https://raw.githubusercontent.com/openapi/pulse/main/public/ticker-dark.svg">
      <source media="(prefers-color-scheme: light)"
              srcset="https://raw.githubusercontent.com/openapi/pulse/main/public/ticker.svg">
      <img alt="Openapi Pulse — this week in the Openapi community"
           src="https://raw.githubusercontent.com/openapi/pulse/main/public/ticker.svg">
    </picture>
  </a>
</p>

**Pulse** is the coordination and automation hub behind the continuous activity of the Openapi GitHub ecosystem.

Open-source ecosystems grow through consistency.

Repositories need to be maintained, releases need to happen, projects need to be highlighted, examples need to be published, contributors need attention, and the overall ecosystem needs a visible and predictable rhythm.

Pulse exists to coordinate that rhythm from a single place.

## What Pulse does

Pulse orchestrates recurring activities across the Openapi GitHub organization.

It can coordinate things such as:

* Repository of the Week
* scheduled releases
* recurring repository maintenance
* ecosystem announcements
* release notes
* developer content
* contributor initiatives
* repository rotation and promotion
* recurring GitHub issues
* cross-repository workflows
* ecosystem metrics
* periodic reports
* experiments and campaigns

The goal is not simply to automate tasks.

The goal is to make sure that the Openapi open-source ecosystem **never stops moving**.

## The Pulse concept

Pulse introduces a regular heartbeat into the organization.

Each cycle can select one or more repositories and trigger coordinated activities around them.

For example:

```text
                    OPENAPI PULSE
                         │
              ┌──────────┼──────────┐
              │          │          │
           Weekly     Monthly     Events
            Pulse      Pulse       Pulse
              │
              ↓
       Select Repository
              │
       ┌──────┼────────┐
       ↓      ↓        ↓
    Release  Improve  Promote
       │      │        │
       └──────┼────────┘
              ↓
          Measure
              │
              ↓
        Next Pulse
```

Pulse turns isolated maintenance activities into a continuous process.

## The Pulse Card

The **Pulse Card** is the component the Pulse engine distributes: a single SVG,
embedded once near the top of every repository README in the organization, that
acts as a weekly news ticker for the ecosystem and routes readers to a single
call to action — the Discussions.

The card above is live. This is the prototype currently in `public/`.

It carries four tracks: the **API of the week**, the **Developer of the week**
and the **Contributor of the week** — both with their GitHub avatar — and the
**Community discussion** worth joining.

### How it works

The content lives in exactly one place. Repositories embed a stable URL and
never need an editorial commit again — the update happens only here.

```text
content/current.yml          ← the edition number, the CTA, the people queues
content/apis.yml             ← the API queue
content/topics.yml           ← the discussion queue
content/blog.yml             ← the blog relay queues
        │
generator/sync.py            ← refreshes the queues from their sources
generator/build.py           ← renders both themes, embeds the avatars
generator/publish.py         ← posts the edition to Discussions
generator/rotate.py          ← advances the queues for the next edition
        │
public/ticker.svg
public/ticker-dark.svg
        │
        ├──────────────► openapi/<repo-python> / README
        ├──────────────► openapi/<repo-php>    / README
        ├──────────────► openapi/<repo-js>     / README
        └──────────────► every other repository
```

`.github/workflows/pulse.yml` runs the whole cycle on a schedule and commits
the result back. **Daily for now**, deliberately — the cadence is short so the
loop can be watched working day after day before it is trusted with a weekly
rhythm. Switching to weekly is one line in the cron.

### Embedding it in a repository

Place this right after the title and the main badges:

```html
<p align="center">
  <a href="https://github.com/orgs/openapi/discussions">
    <picture>
      <source media="(prefers-color-scheme: dark)"
              srcset="https://raw.githubusercontent.com/openapi/pulse/main/public/ticker-dark.svg">
      <source media="(prefers-color-scheme: light)"
              srcset="https://raw.githubusercontent.com/openapi/pulse/main/public/ticker.svg">
      <img alt="Openapi Pulse"
           src="https://raw.githubusercontent.com/openapi/pulse/main/public/ticker.svg">
    </picture>
  </a>
</p>
```

The `<picture>` element gives the card a light and a dark variant so it sits
naturally in both GitHub themes. The whole image is one link, with one
destination — the card carries several stories but never competes with itself.

### The queues

Ordered queues decide what goes out. The first four are what the card shows;
the last two are the blog relay described below. **The entry at the top of
each one is what goes out next**, which makes curating them a single gesture:
move a line to the top and it is on the next card. Publishing moves it to the
bottom, so the queues keep turning on their own once you stop curating them.

| Queue | File | Source |
| --- | --- | --- |
| `developers` | `content/current.yml` | [organization members](https://github.com/orgs/openapi/people) |
| `contributors` | `content/current.yml` | [contributors registry](https://github.com/openapi/contributors) |
| `apis` | `content/apis.yml` | [API library](https://console.openapi.com/apis) |
| `topics` | `content/topics.yml` | [open discussions](https://github.com/openapi/discussions) |
| `news` · `insights` | `content/blog.yml` | [the Openapi blog](https://openapi.com/blog) |

`sync.py` aligns all of them with those sources:

```bash
python3 generator/sync.py            # align the queues
python3 generator/sync.py --dry-run  # preview the changes
```

Membership belongs upstream; the **running order** belongs here. So the sync
merges rather than overwrites — entries already in a queue keep their position,
newcomers are appended to the bottom so they queue behind everything already
waiting instead of jumping the line, and anything no longer listed upstream is
dropped. It never decides what goes out next.

The API library has no public JSON feed, so `sync.py` reads the server-rendered
listing and keys on the `apiBox` markup. If that page is ever restructured the
sync fails loudly rather than writing an empty queue.

The topic queue picks up every open discussion except the Openapi Pulse
editions themselves and the Announcements. Each entry carries a `short` — the
label the card shows, since a track has room for roughly 35 characters and a
real discussion title rarely fits. Without one it falls back to the title, and
the fitter shrinks and clips it.

Anyone under `exclude` is filtered out of the people queues no matter what the
sources say. The card exists to give visibility to the people who work on and
with Openapi, not to the person publishing it, so the author of the system
stays out of his own rotation:

```yaml
exclude:
  - francescobianco
```

### The cycle

```bash
python3 generator/sync.py      # refresh the queues from their sources
python3 generator/build.py     # render the card for the top of each queue
python3 generator/publish.py   # post the edition, and relay the blog
python3 generator/rotate.py    # advance the queues for the next one
```

The order is not arbitrary. The card is built and committed **before** the post
goes out, so the discussion can link the SVG at an immutable commit and keep
showing the card it was published with instead of silently updating to a later
edition. The queues are rotated **after**, which is what keeps the top of each
file meaning "next". And because rotation comes last, a failed publish leaves
the edition intact to be retried rather than silently skipped.

For the same reason `rotate.py` does not regenerate the SVGs: the card in
`public/` has to keep showing the published edition until the next one is
built.

### Publishing to Discussions

`publish.py` renders `templates/discussion.md` and opens one post per edition
in the **Openapi Pulse** category of
[openapi/discussions](https://github.com/openapi/discussions). It then relays
the blog into two further categories — see
[the blog relay](#the-blog-relay).

Two things GitHub does not let a script do, both worked around:

* **Discussion categories cannot be created through the API.** There is no
  `createDiscussionCategory` mutation and no REST endpoint. The category has to
  be created once by hand at
  [discussions/categories](https://github.com/openapi/discussions/discussions/categories).
  `publish.py` looks it up by name and stops with instructions if it is
  missing, rather than quietly posting somewhere else.
* **Discussions cannot be pinned through the API.**
  `Repository.pinnedDiscussions` is readable, but no mutation writes it. So
  instead of pinning every new edition, one permanent discussion is pinned by
  hand — once, forever — and its number recorded as `discussions.index` in
  `current.yml`. `publish.py` rewrites that post's body every edition, so the
  pinned entry always points at the latest one.

The workflow needs a `PULSE_DISCUSSIONS_TOKEN` secret. The discussions live in
`openapi/discussions`, a different repository from this one, and a workflow's
built-in `GITHUB_TOKEN` is scoped to its own repository — so a PAT with write
access to the discussions repository is required.

### The blog relay

The [Openapi blog](https://openapi.com/blog) is where the ecosystem already
publishes editorial content, and Discussions is where the community reads it.
Every edition carries one article from each of two blog categories into a
category of its own:

| On the blog | In [openapi/discussions](https://github.com/openapi/discussions) |
| --- | --- |
| News | Announcements |
| API Insights | API Engineering |

What goes out is an **extract**, never a copy: the blog's own summary and a
link back to the full piece. The article stays where it was written;
Discussions gets the pointer and the conversation. No cover image — a thread
that opens on a full-width marketing image reads as a repost rather than as an
invitation to talk.

The blog has no feed — no RSS, no JSON, the pages are server-rendered — so
`generator/blog.py` reads the listing markup, keying on the category badge and
the card heading. As with the API library, a restructured page yields nothing
and the sync stops loudly rather than emptying a queue.

These two queues behave differently from the other four, and the difference is
the point:

* **They do not rotate.** An article is relayed once. `publish.py` moves what
  it posted into `relayed:` at the bottom of `content/blog.yml`, and `sync.py`
  never puts a relayed slug back.
* **They are not curated.** The blog decides the order — newest first, because
  for news freshness *is* the running order. An article that ages off the front
  of the blog before its turn is dropped; by then it is not news any more.
* **Retirement happens in `publish.py`, not `rotate.py`.** Rotation is for
  queues that turn; this is a removal, and it belongs to whatever actually
  managed to post. A relay that fails leaves its article at the top of the
  queue for the next edition instead of burning it.

The relay is deliberately the softer half of the edition. If a category does
not exist yet, or the blog cannot be reached, the run says so and the edition
itself still goes out — the two are separate events that happen to share a
schedule. Like every other discussion category, **Announcements** and **API
Engineering** have to be created by hand once, at
[discussions/categories](https://github.com/openapi/discussions/discussions/categories).

Both of them are also excluded from the card's topic queue: they hold what this
system writes, and the card spotlights conversations, not broadcasts.

### Design notes

* **880 × 148**, one line of identity and one line of content — small enough
  not to steal space from the project, distinctive enough to be recognized
  across repositories.
* **Editorial, not CI.** No Shields-style key/value pills: a badge says
  `build | passing`, the Pulse Card says *this week in the community*.
* **Avatars are baked in.** GitHub serves README images through a caching proxy
  that renders them in restricted mode, where an SVG cannot load any external
  resource. So `build.py` downloads `https://github.com/<nickname>.png` and
  embeds it as a base64 data URI, clipped to a circle. Downloads are cached in
  `generator/.cache/`; a nickname that cannot be fetched degrades to an
  initial-letter monogram instead of breaking the build.
* **No external assets at all** — system font stack, no web fonts, no scripts.
* The heartbeat mark and the trace along the bottom edge are CSS animations,
  disabled under `prefers-reduced-motion`. They carry the Openapi purple —
  `#563e7d` on light, lightened to `#9c7ecc` on dark, where the brand value
  itself would all but disappear against `#0d1117`.
* Values are **fitted** to their track: the type shrinks from 14px down to 10px
  to make a long value fit, and only what still overflows at the smallest size
  is clipped. Real handles run long — `@FrancescoRicchiutiOpenapi` is 25
  characters — so a fixed budget would either truncate half the organization or
  force every column to be sized for the worst case.

### Still to refine

* Wordmark/logo instead of the plain `OPENAPI PULSE` type.
* Hosting: `raw.githubusercontent.com` works today; GitHub Pages
  (`openapi.github.io/pulse/ticker.svg`) or a dedicated endpoint would give
  proper control over cache headers.
* Move the schedule from daily to weekly once the loop has been watched
  running end to end.
* The contributors queue is currently two people, so it turns over every two
  editions. It widens on its own as `openapi/contributors` grows.
* The `week` counter is a plain increment, not the real ISO week — while the
  cadence is daily the two cannot agree, and it rolls over from 52 to 1.

See [CARD.md](CARD.md) for the full rationale behind the component.

## Repository of the Week

One of the core Pulse mechanisms is the **Repository of the Week**.

Every week, Pulse can select a repository from the Openapi ecosystem and make it the focus of coordinated activity.

A weekly cycle may include:

```text
Monday      Select repository
Tuesday     Maintenance / documentation
Wednesday   Example or developer resource
Thursday    Community / distribution
Friday      Release and promotion
```

The exact process can evolve over time.

The important part is maintaining a predictable rhythm.

## What lives here

Pulse is intended to contain the configuration, workflows and data required to coordinate recurring ecosystem activity.

A possible structure is:

```text
pulse/
│
├── calendar/
│   ├── weekly.yml
│   └── campaigns.yml
│
├── repositories/
│   ├── rotation.yml
│   └── priorities.yml
│
├── campaigns/
│   └── ...
│
├── templates/
│   ├── release.md
│   ├── repository-of-the-week.md
│   └── announcement.md
│
├── metrics/
│   └── ...
│
├── scripts/
│   └── ...
│
└── .github/
    └── workflows/
        ├── weekly-pulse.yml
        ├── release.yml
        ├── metrics.yml
        └── ...
```

The structure is expected to evolve as Pulse grows.

## Centralized automation

Pulse provides a central place for automation that affects multiple Openapi repositories.

Whenever possible, common operations should be implemented as reusable workflows or shared automation rather than duplicated across repositories.

Individual repositories should remain focused on their products.

Pulse should focus on **when, why and how the ecosystem acts as a whole**.

## Pulse cycles

Pulse activities can operate at different frequencies.

### Weekly Pulse

The main operational heartbeat.

Examples:

* select the Repository of the Week
* publish or coordinate a release
* create maintenance tasks
* highlight an example
* trigger developer-facing activity

### Monthly Pulse

A broader ecosystem review.

Examples:

* repository performance
* stars and followers
* contributors
* issues and pull requests
* package downloads
* ecosystem growth
* repositories requiring attention

### Campaign Pulse

Temporary coordinated initiatives.

Examples:

* MCP ecosystem campaign
* SDK improvements
* Hacktoberfest
* documentation month
* new API launch
* developer challenge

Campaigns can temporarily modify the normal Pulse priorities without replacing the underlying weekly rhythm.

## Principles

Pulse follows a few simple principles.

**Consistency over intensity**

Small activity every week is more valuable than occasional bursts of activity.

**Automation over repetition**

If an activity becomes predictable, Pulse should eventually automate it.

**One ecosystem, many repositories**

Repositories are independent projects, but they should behave as parts of the same Openapi developer ecosystem.

**Useful activity over artificial activity**

Pulse should never generate commits, releases or announcements merely to create noise.

Every Pulse should produce something useful for developers, contributors or users.

**Measure and adapt**

Activities should be measurable whenever possible.

What generates adoption should receive more attention. What does not work should be changed or removed.

## The long-term goal

Pulse is not a marketing campaign.

It is permanent infrastructure for maintaining the health, visibility and growth of the Openapi open-source ecosystem.

Over time, more recurring activities should become coordinated or automated through Pulse.

The desired result is simple:

> **Every week, something useful happens in the Openapi ecosystem.**

That is the heartbeat.

That is **Pulse**.
