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

### How it works

The content lives in exactly one place. Repositories embed a stable URL and
never need an editorial commit again — the weekly update happens only here.

```text
content/current.yml          ← the only file edited each week
        │
generator/build.py           ← renders both themes
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

### Updating the card

Edit `content/current.yml`, regenerate, commit:

```bash
$EDITOR content/current.yml
python3 generator/build.py
git commit -am "pulse: week 38"
```

`current.yml` holds the week number, the three editorial columns and the CTA:

```yaml
week: 37

cta:
  text: JOIN THE CONVERSATION
  url: https://github.com/orgs/openapi/discussions

columns:
  - label: API OF THE WEEK
    value: Open-Meteo
  - label: DEVELOPER OF THE WEEK
    value: "@foobar"
  - label: COMMUNITY DISCUSSION
    value: Do agents still need SDKs?
```

Column values are clipped at 28 characters so the three tracks never collide.

### Design notes

* **880 × 132**, one line of identity and one line of content — small enough not
  to steal space from the project, distinctive enough to be recognized across
  repositories.
* **Editorial, not CI.** No Shields-style key/value pills: a badge says
  `build | passing`, the Pulse Card says *this week in the community*.
* **No external assets.** System font stack, no web fonts, no scripts — GitHub
  serves README images through a caching proxy that would drop them.
* The heartbeat mark and the trace along the bottom edge are CSS animations,
  disabled under `prefers-reduced-motion`.

### Still to refine

* Final palette and accent — the red is a placeholder for the OpenAPI brand.
* Wordmark/logo instead of the plain `OPENAPI PULSE` type.
* Hosting: `raw.githubusercontent.com` works today; GitHub Pages
  (`openapi.github.io/pulse/ticker.svg`) or a dedicated endpoint would give
  proper control over cache headers.
* A `publish-pulse.yml` workflow to regenerate and commit the SVGs weekly.

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
