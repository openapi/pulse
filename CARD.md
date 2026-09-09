# OpenAPI Pulse Card

L’idea è introdurre in tutte le repository dell’organizzazione `@openapi` una piccola card editoriale comune, posizionata nella parte alta del README, con lo scopo di portare traffico dalle singole repository verso la community e le Discussions.

La card deve funzionare come una sorta di **news ticker settimanale dell’ecosistema OpenAPI**, mostrando pochi contenuti editoriali selezionati da `pulse`, ad esempio:

* API of the Week
* Developer / Contributor of the Week
* una Discussion rilevante
* un insight dalla community
* una challenge o call to action

L’obiettivo non è trasformare il README in una newsletter, ma creare un elemento visivo riconoscibile e identico su tutte le repository, capace di comunicare che dietro le singole librerie esiste una community attiva.

## Principio architetturale

Il contenuto deve essere centralizzato.

Non conviene fare un commit settimanale su tutti i README dell’organizzazione solo per aggiornare il contenuto editoriale. Ogni repository dovrebbe invece contenere una volta sola il riferimento alla Pulse Card.

Esempio:

```markdown
[![OpenAPI Pulse](https://openapi.github.io/pulse/ticker.svg)](https://github.com/openapi/discussions)
```

Da quel momento in poi tutte le modifiche settimanali avvengono esclusivamente dentro `openapi/pulse`.

Architettura concettuale:

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
             └──────────────► tutte le altre repo
```

## Contenuto della card

La card dovrebbe essere piccola, leggibile e visivamente editoriale, non simile a un badge CI.

Indicativamente:

```text
╭──────────────────────────────────────────────────────────────────────╮
│ 💓 OPENAPI PULSE · WEEK 37                                          │
│                                                                      │
│ 🔌 API OF THE WEEK     👨‍💻 DEVELOPER       💬 COMMUNITY              │
│ Open-Meteo             @foobar              Do agents need SDKs?     │
│                                                                      │
│                         JOIN THE DISCUSSION →                        │
╰──────────────────────────────────────────────────────────────────────╯
```

Dimensioni indicative: circa 800–900 px di larghezza e 80–120 px di altezza.

Deve essere abbastanza piccola da non rubare spazio al progetto, ma abbastanza riconoscibile da diventare un elemento ricorrente dell’identità OpenAPI.

## Posizione nel README

La posizione ideale è subito dopo titolo/logo e badge principali:

```markdown
# OpenAPI Python Client

[build badges]

[PULSE CARD]

A fully-featured Python API client...
```

In alternativa può stare persino sopra i badge, se si vuole darle maggiore peso editoriale.

## Un’unica CTA

La card non deve cercare di contenere troppi link.

Un SVG inserito nel README funziona meglio se l’intera immagine è cliccabile verso una sola destinazione.

La destinazione ideale è la Discussion principale della settimana oppure la homepage delle Organization Discussions:

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

Quindi la card può mostrare più contenuti, ma deve avere una CTA unica come:

```text
JOIN THE CONVERSATION →
```

## Relazione con Pulse

`pulse` deve essere il motore editoriale.

La repository potrebbe contenere qualcosa del genere:

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

Un possibile `current.yml`:

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
  text: Join the conversation
```

Una GitHub Action può rigenerare automaticamente gli SVG ogni settimana.

## Light e dark mode

La soluzione migliore è produrre due versioni:

```text
ticker.svg
ticker-dark.svg
```

e inserirle nel README tramite `<picture>`:

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
        alt="OpenAPI Pulse"
        src="https://openapi.github.io/pulse/ticker.svg">
    </picture>
  </a>
</p>
```

Questo permette alla card di integrarsi bene sia nel tema chiaro sia nel tema scuro di GitHub.

## Hosting

Una soluzione semplice e coerente con il progetto è usare GitHub Pages:

```text
https://openapi.github.io/pulse/ticker.svg
```

In alternativa può essere esposto un endpoint dedicato:

```text
https://pulse.openapi.com/ticker.svg
```

Il vantaggio dell’endpoint è avere maggiore controllo su cache e distribuzione.

## Cache

Le immagini nei README GitHub possono essere servite attraverso sistemi di caching/proxy.

Poiché la Pulse Card cambia settimanalmente, questo non è un problema critico, ma l’infrastruttura dovrebbe comunque essere progettata pensando agli aggiornamenti.

Possibili strategie:

1. URL fisso:

```text
/ticker.svg
```

con opportuni header di cache.

2. URL versionato:

```text
/pulse-2026-w37.svg
```

ma in questo caso sarebbe necessario modificare periodicamente i README.

Per questo è preferibile mantenere un URL stabile e aggiornare centralmente il contenuto.

## Cosa evitare

Non userei Shields.io come soluzione principale.

Badge come:

```text
API of the week | Open-Meteo
Developer       | @foobar
```

sono tecnicamente semplici ma sembrano indicatori CI e perdono il carattere editoriale del progetto.

Shields è perfetto per:

```text
build | passing
coverage | 92%
version | 3.2
```

La Pulse Card invece deve comunicare:

```text
questa settimana nella community OpenAPI...
```

Deve quindi avere una propria identità visuale.

## Ruolo strategico

La Pulse Card non è soltanto decorazione.

Le repository SDK normalmente hanno un comportamento molto transazionale:

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

La card introduce un nuovo percorso:

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

Ogni repository diventa quindi un punto di acquisizione verso la community.

Più repository esistono nell’organizzazione, più cresce la superficie di distribuzione del Pulse.

## Feedback loop editoriale

Nel tempo la community stessa deve alimentare la Pulse Card.

Esempio:

```text
Discussion
   ↓
utente mostra un progetto
   ↓
Project / Developer of the Week
   ↓
Pulse Card
   ↓
visibilità in tutte le repository
   ↓
nuovi utenti entrano nella Discussion
```

Si crea così un ciclo:

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

Il componente può avere un nome riconoscibile e diventare parte del branding dell’organizzazione:

**OpenAPI Pulse Card**

oppure:

**OpenAPI Pulse Ticker**

`Pulse` rimane il motore editoriale, mentre la Pulse Card è il componente distribuito nei README.

## Obiettivo finale

Ogni repository OpenAPI deve comunicare implicitamente due cose:

```text
questa libreria è mantenuta

e

questa libreria appartiene a una community viva
```

La Pulse Card è il ponte tra le repository tecniche e `openapi/discussions`.

L’obiettivo è quindi trasformare tutte le repository dell’organizzazione in una rete di ingressi verso un unico spazio di community, senza generare commit editoriali settimanali su ciascuna repo e mantenendo tutto il contenuto sotto il controllo centrale di `openapi/pulse`.
