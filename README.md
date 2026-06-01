# Pocket Universe Generator

**Procedural microcosms from a single seed.**

Give it a word — any word — and it builds a complete fictional world: physics, geography, calendar, pantheon, ecology, language, and culture. All procedural, all interlinked, all deterministic from the seed. No LLMs, no APIs, no external generation.

```
pocket-universe "ember"
# → Durnnaren Copse — A forest world with OVS grammar, loose federation, zero moons
```

## Try it

**Web app** — open `http://localhost:8081` while the servers are running.

**API** — `http://localhost:8080/generate?seed=ember`

## Features

- **Physics** — radius, gravity, day/year length, axial tilt, rings, moons
- **Regions** — named biomes with terrain types and procedurally named cities
- **Calendar** — seasons determined by axial tilt, named months, festivals
- **Pantheon** — 3-5 gods with archetypes, domains, epithets, creation myth
- **Ecology** — signature flora/fauna, full species lists keyed to terrain
- **Language** — 36-word lexicon (no duplicates), configurable grammar (SOV/SVO/VSO/OVS/free), gendered or tonal
- **Culture** — social structure, values, taboos, burial tradition

## Install

```bash
git clone https://github.com/imrightguy/pocket-universe.git
cd pocket-universe
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Usage

```bash
# Generate a world from a seed
pocket-universe rust

# Batch 5 random worlds
pocket-universe --list-seeds

# JSON output
pocket-universe rust --json

# API server
pocket-universe-api
# → Listening on http://0.0.0.0:8080
```

## Web frontend

A Flutter web app lives in `pocket_web/`. To build and serve:

```bash
cd pocket_web
flutter build web
python3 -m http.server 8081 --directory build/web
```

The frontend talks to the API on `localhost:8080`.

## How it works

The seed feeds a deterministic PRNG (SplitMix64). Every table, weight, range, and choice is driven by that PRNG — same seed always gives the same world. No LLMs, no APIs, just pure procedural generation in ~400 lines of Python.

## License

MIT
