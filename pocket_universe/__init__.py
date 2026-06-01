"""Pocket Universe Generator — create a complete fictional microcosm from a seed word.

Usage:
    pocket-universe <seed>          # Generate and display a world
    pocket-universe <seed> --map    # Export SVG topographic map
    pocket-universe <seed> --json   # Raw data output
    pocket-universe --list-seeds    # Generate 5 random worlds

A single seed word produces deterministically:
  - World name + terrain
  - Physics (radius, gravity, day/year, axial tilt, rings, moons)
  - 4-8 named regions with terrain types
  - 3-6 procedurally named cities
  - Calendar (seasons, months, festivals)
  - Pantheon (3-5 gods with archetypes, domains, epithets)
  - Creation myth
  - Ecology (signature flora/fauna, species lists)
  - Language (36-word lexicon, grammar, gender/tones)
  - Culture (social structure, values, taboos, burial)
  - Climate (wind cells, climate zones, seasonal weather, extreme events)
  - Economy (exports, imports, currency, trade partners, luxury goods)
  - SVG topographic map

All generated procedurally — no LLMs, no APIs, no external data.
"""

from pocket_universe.generator import generate
from pocket_universe.format import render
from pocket_universe.map_viz import render_topology
from pocket_universe.climate import generate_climate
from pocket_universe.economy import generate_economy
