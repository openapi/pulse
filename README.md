# Openapi Pulse

> **The heartbeat of the Openapi open-source ecosystem.**

<p align="center">
  <a href="https://github.com/orgs/openapi/discussions">
    <picture>
      <source media="(prefers-color-scheme: dark)"
              srcset="https://raw.githubusercontent.com/openapi/pulse/main/public/ticker-dark.svg">
      <source media="(prefers-color-scheme: light)"
              srcset="https://raw.githubusercontent.com/openapi/pulse/main/public/ticker.svg">
      <img alt="OpenAPI Pulse — this week in the OpenAPI community"
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
never need an editorial commit again — the weekly update happens only here.

```text
content/current.yml          ← the only file edited each week
        │
generator/sync.py            ← pulls the people from GitHub
generator/rotate.py          ← advances the week, rotates the people
generator/build.py           ← renders both themes, embeds the avatars
        │
public/ticker.svg
public/ticker-dark.svg
        │
        ├──────────────► openapi/<repo-python> / README
        ├──────────────► openapi/<repo-php>    / README
        ├──────────────► openapi/<repo-js>     / README
        └──────────────► every other repository
```

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
      <img alt="OpenAPI Pulse"
           src="https://raw.githubusercontent.com/openapi/pulse/main/public/ticker.svg">
    </picture>
  </a>
</p>
```

The `<picture>` element gives the card a light and a dark variant so it sits
naturally in both GitHub themes. The whole image is one link, with one
destination — the card carries several stories but never competes with itself.

### The people, and how they rotate

The two people on the card are not hand-picked each week. They come from the
places where the ecosystem already records who is involved:

```text
https://github.com/orgs/openapi/people      → developers
https://github.com/openapi/contributors     → contributors
```

`sync.py` reads both and merges them into the pools in `current.yml`:

```bash
python3 generator/sync.py            # align the pools with the sources
python3 generator/sync.py --dry-run  # preview the changes
```

Membership belongs upstream; the **running order** belongs here. So the sync
merges rather than overwrites — people already in a pool keep their position,
newcomers are appended to the tail so they queue behind everyone already
waiting instead of jumping the line, and anyone no longer listed upstream is
dropped.

The card always features the **head** of each list. Rotating moves each head to
the tail, so the next name steps forward and nobody repeats until the whole
pool has had a turn:

```bash
python3 generator/rotate.py            # bump the week, rotate, regenerate
python3 generator/rotate.py --dry-run  # preview who is up next
```

```text
week 37 → 38
  developers: @AlbertoVenanzoniAltravia → @cipriani1194
  contributors: @Deadpool2000 → @Seraphim200001
```

The order stays plain text and hand-editable: to feature someone sooner, move
them to the top. `rotate.py` edits the file line by line, so comments and
hand-ordering survive. After week 52 it rolls over into week 1 of the next
year.

Anyone under `exclude` is filtered out of both pools no matter what the sources
say. The card exists to give visibility to the people who work on and with
Openapi, not to the person publishing it, so the author of the system stays
out of his own rotation:

```yaml
exclude:
  - francescobianco
```

The full cycle, once a week:

```bash
python3 generator/sync.py     # who is in
python3 generator/rotate.py   # whose turn it is (regenerates the SVGs)
```

To change the other tracks — the API, the discussion, the CTA — edit
`current.yml` and run the generator on its own:

```bash
$EDITOR content/current.yml
python3 generator/build.py
```

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
  disabled under `prefers-reduced-motion`.
* Values are **fitted** to their track: the type shrinks from 14px down to 10px
  to make a long value fit, and only what still overflows at the smallest size
  is clipped. Real handles run long — `@FrancescoRicchiutiOpenapi` is 25
  characters — so a fixed budget would either truncate half the organization or
  force every column to be sized for the worst case.

### Still to refine

* Final palette and accent — the red is a placeholder for the OpenAPI brand.
* Wordmark/logo instead of the plain `OPENAPI PULSE` type.
* Hosting: `raw.githubusercontent.com` works today; GitHub Pages
  (`openapi.github.io/pulse/ticker.svg`) or a dedicated endpoint would give
  proper control over cache headers.
* A `publish-pulse.yml` workflow to run `sync.py` + `rotate.py` and commit the
  SVGs weekly.
* The contributors pool is currently two people, so it cycles every two weeks.
  It widens on its own as `openapi/contributors` grows.

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
