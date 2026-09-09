# Openapi Pulse Card

The idea is to introduce a small, shared editorial card into every repository
in the `@openapi` organization, placed near the top of the README, so that
traffic flows from the individual repositories towards the community and the
Discussions.

The card should work as a kind of **weekly news ticker for the Openapi
ecosystem**, showing a few selected editorial items curated in `pulse`, such as:

* API of the Week
* Developer / Contributor of the Week
* a relevant Discussion
* an insight from the community
* a challenge or call to action

The goal is not to turn the README into a newsletter, but to create a
recognizable visual element, identical across every repository, that
communicates that behind the individual libraries there is an active community.

## Architectural principle

The content has to be centralized.

Committing to every README in the organization once a week just to update the
editorial content is not worth it. Each repository should instead contain the
reference to the Pulse Card once and only once.

For example:

```markdown
[![Openapi Pulse](https://openapi.github.io/pulse/ticker.svg)](https://github.com/openapi/discussions)
```

From that point on, every weekly change happens exclusively inside
`openapi/pulse`.

The conceptual architecture:

```text
openapi/pulse
    │
    ├── content/current.yml
    ├── generator
    └── public/ticker.svg
             │
             ├──────────────► repo-python / README
             ├──────────────► repo-php / README
             ├──────────────► repo-rust / README
             ├──────────────► repo-js / README
             └──────────────► every other repository
```

## What goes on the card

The card should be small, readable and visually editorial — not something that
looks like a CI badge.

Roughly:

```text
╭──────────────────────────────────────────────────────────────────────╮
│ 💓 OPENAPI PULSE · WEEK 37                                          │
│                                                                      │
│ 🔌 API OF THE WEEK     👨‍💻 DEVELOPER       💬 COMMUNITY              │
│ Open-Meteo             @foobar              Do agents need SDKs?     │
│                                                                      │
│                         JOIN THE COMMUNITY →                         │
╰──────────────────────────────────────────────────────────────────────╯
```

Indicative dimensions: around 800–900 px wide and 80–120 px tall.

Small enough not to steal space from the project, but recognizable enough to
become a recurring element of the Openapi identity.

## Placement in the README

The ideal position is right after the title/logo and the main badges:

```markdown
# Openapi Python Client

[build badges]

[PULSE CARD]

A fully-featured Python API client...
```

It can even sit above the badges, if it should carry more editorial weight.

## A single CTA

The card should not try to hold too many links.

An SVG embedded in a README works better when the entire image is clickable
towards a single destination.

The ideal destination is the main discussion of the week, or the homepage of
the organization Discussions:

```text
README
   ↓
Pulse Card
   ↓
Weekly Discussion
   ↓
reaction / vote / comment
   ↓
community
```

So the card can show several items, but it must have one single CTA, such as:

```text
JOIN THE COMMUNITY →
```

## Relationship with Pulse

`pulse` should be the editorial engine.

The repository could contain something along these lines:

```text
openapi/pulse
│
├── content/
│   └── current.yml
│
├── generator/
│
├── public/
│   ├── ticker.svg
│   └── ticker-dark.svg
│
└── .github/workflows/
    └── publish-pulse.yml
```

A possible `current.yml`:

```yaml
week: 37

api_of_week:
  name: Open-Meteo
  url: https://...

developer:
  github: foobar

discussion:
  title: Do AI agents still need SDKs?
  url: https://github.com/orgs/openapi/discussions/...

cta:
  text: Join the community
```

A GitHub Action can regenerate the SVGs automatically every week.

## Light and dark mode

The best approach is to produce two versions:

```text
ticker.svg
ticker-dark.svg
```

and embed them in the README through `<picture>`:

```html
<p align="center">
  <a href="https://github.com/openapi/discussions">
    <picture>
      <source
        media="(prefers-color-scheme: dark)"
        srcset="https://openapi.github.io/pulse/ticker-dark.svg">
      <source
        media="(prefers-color-scheme: light)"
        srcset="https://openapi.github.io/pulse/ticker.svg">
      <img
        alt="Openapi Pulse"
        src="https://openapi.github.io/pulse/ticker.svg">
    </picture>
  </a>
</p>
```

This lets the card sit well in both the light and the dark GitHub themes.

## Hosting

A simple solution, coherent with the project, is GitHub Pages:

```text
https://openapi.github.io/pulse/ticker.svg
```

Alternatively a dedicated endpoint could be exposed:

```text
https://pulse.openapi.com/ticker.svg
```

The advantage of an endpoint is more control over caching and distribution.

## Cache

Images in GitHub READMEs can be served through caching/proxy systems.

Since the Pulse Card changes weekly this is not a critical problem, but the
infrastructure should still be designed with updates in mind.

Possible strategies:

1. A fixed URL:

```text
/ticker.svg
```

with appropriate cache headers.

2. A versioned URL:

```text
/pulse-2026-w37.svg
```

but in that case the READMEs would need to be changed periodically.

That is why it is preferable to keep a stable URL and update the content
centrally.

## What to avoid

I would not use Shields.io as the main solution.

Badges like:

```text
API of the week | Open-Meteo
Developer       | @foobar
```

are technically simple but look like CI indicators, and lose the editorial
character of the project.

Shields is perfect for:

```text
build | passing
coverage | 92%
version | 3.2
```

The Pulse Card instead has to communicate:

```text
this week in the Openapi community...
```

So it needs a visual identity of its own.

## Strategic role

The Pulse Card is not just decoration.

SDK repositories normally have very transactional behaviour:

```text
developer
   ↓
README
   ↓
install
   ↓
use API
   ↓
leave
```

The card introduces a new path:

```text
developer
   ↓
README
   ↓
Pulse Card
   ↓
Discussions
   ↓
vote / comment / show project
   ↓
community
   ↓
contributor
```

Every repository therefore becomes an acquisition point towards the community.

The more repositories exist in the organization, the larger the distribution
surface of the Pulse becomes.

## Editorial feedback loop

Over time the community itself should feed the Pulse Card.

For example:

```text
Discussion
   ↓
a user shows a project
   ↓
Project / Developer of the Week
   ↓
Pulse Card
   ↓
visibility across every repository
   ↓
new users enter the Discussion
```

Which creates a cycle:

```text
Publish
   ↓
Discuss
   ↓
Participate
   ↓
Curate
   ↓
Publish
```

## Naming

The component can have a recognizable name and become part of the branding of
the organization:

**Openapi Pulse Card**

or:

**Openapi Pulse Ticker**

`Pulse` remains the editorial engine, while the Pulse Card is the component
distributed across the READMEs.

## Final goal

Every Openapi repository should implicitly communicate two things:

```text
this library is maintained

and

this library belongs to a living community
```

The Pulse Card is the bridge between the technical repositories and
`openapi/discussions`.

The goal is therefore to turn every repository in the organization into a
network of entry points towards a single community space, without generating
weekly editorial commits in each repo, and keeping all the content under the
central control of `openapi/pulse`.
