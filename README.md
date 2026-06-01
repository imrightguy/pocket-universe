# Pocket Universe Generator

**Procedural microcosms from a single seed.**

Give it a word — any word — and it builds a complete fictional world: physics, geography, calendar, pantheon, ecology, language, and culture. All procedural, all interlinked, all deterministic from the seed. No LLMs, no APIs, no external generation.

```
pocket-universe "ember"
# → Durnnaren Copse — A forest world with OVS grammar, loose federation, zero moons
```

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

# Show version
pocket-universe --version
```

## How it works

The seed feeds a deterministic PRNG (seeded `random.Random`). Every table, weight, range, and choice is driven by that PRNG — same seed always gives the same world. The whole thing is ~1500 lines of pure Python.

## License

MIT
