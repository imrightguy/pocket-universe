#!/usr/bin/env python3
"""Generative bestiary — creatures that emerge from a world's physics and ecology.

Standalone prototype. Usage:
    python3 bestiary.py --gravity 0.68 --terrain forest
    python3 bestiary.py --gravity 0.95 --terrain desert --day-length 29 --atmosphere 0.8
"""

import argparse
import math
import json
import hashlib
import struct
import random

# ── Seeded RNG (same SplitMix64 as main generator for compatibility) ──────────

class Seed:
    def __init__(self, value):
        if isinstance(value, str):
            h = hashlib.sha256(value.encode("utf-8")).digest()
            value = struct.unpack("<Q", h[:8])[0]
        self._state = value & 0xFFFFFFFFFFFFFFFF

    def _next(self):
        self._state = (self._state + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
        z = self._state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
        return z ^ (z >> 31)

    def float(self):
        return (self._next() >> 11) * (1.0 / (1 << 53))

    def int(self, lo, hi):
        return lo + (self.u64() % (hi - lo + 1))

    def u64(self):
        return self._next()

    def choice(self, items):
        return items[self.int(0, len(items) - 1)]

    def sample(self, items, k):
        result = list(items)
        random.Random(self._next()).shuffle(result)
        return result[:k]


# ── Body plan tables ──────────────────────────────────────────────────────────

GRAVITY_BODY_PLANS = {
    "low": {      # < 0.6 G — tall, leggy, fragile
        "height_range": (2.5, 8.0),
        "limb_count_range": (4, 8),
        "build": "elongated",
        "skeleton": "lightweight endoskeleton or hydrostatic",
        "locomotion_modes": ["striding", "leaping", "gliding", "ambulatory"],
    },
    "medium": {   # 0.6 - 1.2 G — earth-like range
        "height_range": (0.5, 3.0),
        "limb_count_range": (2, 6),
        "build": "proportional",
        "skeleton": "endoskeleton or chitinous exoskeleton",
        "locomotion_modes": ["walking", "running", "digging", "climbing"],
    },
    "high": {     # > 1.2 G — squat, dense, powerful
        "height_range": (0.1, 1.2),
        "limb_count_range": (2, 8),
        "build": "compressed",
        "skeleton": "dense endoskeleton or reinforced exoskeleton",
        "locomotion_modes": ["crawling", "burrowing", "undulating", "pressing"],
    },
}

TERRAIN_LOCOMOTION = {
    "forest":      ["climbing", "gliding", "stalking", "ambush"],
    "desert":      ["burrowing", "striding", "nocturnal-foraging", "sand-swimming"],
    "tundra":      ["migratory", "burrowing", "pack-hunting", "hibernating"],
    "marsh":       ["wading", "swimming", "amphibious", "floating"],
    "oceanic":     ["swimming", "drift-hunting", "deep-diving", "surface-skimming"],
    "plains":      ["running", "stalking", "pack-hunting", "ambush"],
    "highlands":   ["leaping", "gliding", "climbing", "perching"],
    "volcanic":    ["heat-tolerant", "burrowing", "scavenging", "mineral-feeding"],
    "archipelago": ["swimming", "wading", "clambering", "flying"],
    "continent":   ["walking", "running", "digging", "migratory"],
}

DIET_TYPES = ["herbivore", "carnivore", "omnivore", "detritivore", "filter-feeder", "mineralotroph"]

SENSES = ["sight", "hearing", "vibration", "electroreception", "thermoreception",
          "echolocation", "magnetoreception", "pressure", "chemical-gradient"]

NIGHT_CYCLE_DESCRIPTIONS = {
    0: "perpetual light — no cycle",
    1: "diurnal — active by day",
    2: "crepuscular — active at twilight",
    3: "nocturnal — active by night",
    4: "tidal — regulated by moon phases",
}

BODY_COVERINGS = ["fur", "scales", "chitin", "leathery hide", "feathers",
                  "gelatinous membrane", "silica shards", "moss-like pelt",
                  "biomineralized plates", "transparent integument"]

COLOR_TABLES = {
    "forest":  ["deep green", "mottled brown", "goldfleck", "moss-gray", "umber"],
    "desert":  ["sandy ochre", "pale rust", "dun", "cream-mottle", "faded rose"],
    "tundra":  ["ice-white", "ash-gray", "pale blue", "frost-mottle", "silver"],
    "marsh":   ["olive", "sludge-brown", "murk-green", "bronze", "blackwater"],
    "oceanic": ["abyssal black", "cobalt", "pearlescent", "bioturbid", "deep violet"],
    "plains":  ["tawny", "straw-gold", "dun", "flaxen", "pale russet"],
    "highlands": ["slate", "iron-gray", "basalt black", "ochre", "quartz-white"],
    "volcanic": ["ember-red", "obsidian", "cinder-gray", "sulfur-yellow", "magma-orange"],
    "archipelago": ["reef-blue", "coral-pink", "sand-white", "kelp-green", "shell-mottle"],
}

SOCIAL_STRUCTURES = ["solitary", "pair-bonded", "pack", "herd", "colony", "hive-mind",
                     "symbiotic-pair", "nomadic-band", "territorial-solo"]

BODY_PARTS = [
    "crested head", "beaked snout", "segmented tail", "prehensile tongue",
    "manipulator claws", "wing-membrane", "dorsal fin", "feathered crest",
    "crystalline growths", "bioluminescent lures", "venomous spines",
    "keeled chest", "articulated plates", "telescoping neck", "fan-like tail",
]


def determine_gravity_tier(gravity):
    if gravity < 0.6:
        return "low"
    elif gravity < 1.2:
        return "medium"
    else:
        return "high"


def generate_creature(seed, gravity, terrain, day_length, atmosphere=1.0):
    """Generate a single creature adapted to its world."""
    rng = Seed(seed)
    gravity_tier = determine_gravity_tier(gravity)
    body_plan = GRAVITY_BODY_PLANS[gravity_tier]

    # Height scales with gravity
    height = rng.float() * (body_plan["height_range"][1] - body_plan["height_range"][0]) + body_plan["height_range"][0]
    height = round(height, 1)

    limb_count = rng.int(*body_plan["limb_count_range"])
    if limb_count % 2 == 1:  # even limbs feel more natural
        limb_count += 1

    locomotion = rng.choice(TERRAIN_LOCOMOTION.get(terrain, ["walking"]))

    diet = rng.choice(DIET_TYPES)
    if gravity_tier == "low":
        diet = rng.choice(["herbivore", "omnivore", "filter-feeder"])  # less need for dense muscle
    if terrain == "desert" and diet == "filter-feeder":
        diet = "detritivore"

    primary_sense = rng.choice(SENSES)
    if "nocturnal" in locomotion or "night" in locomotion:
        primary_sense = rng.choice(["thermoreception", "echolocation", "electroreception", "vibration"])

    night_cycle_idx = min(int(day_length / 10), 4)
    if night_cycle_idx > 3:
        night_cycle_idx = rng.int(1, 3)
    activity = NIGHT_CYCLE_DESCRIPTIONS.get(night_cycle_idx, "diurnal")

    colors = COLOR_TABLES.get(terrain, ["gray", "brown"])
    color = rng.choice(colors)

    covering = rng.choice(BODY_COVERINGS)
    if terrain == "oceanic":
        covering = rng.choice(["gelatinous membrane", "scales", "leathery hide"])
    if gravity_tier == "high":
        covering = rng.choice(["chitin", "biomineralized plates", "dense scales"])

    social = rng.choice(SOCIAL_STRUCTURES)
    if diet == "carnivore" and rng.float() < 0.6:
        social = rng.choice(["solitary", "pair-bonded", "pack"])
    if diet == "herbivore":
        social = rng.choice(["herd", "nomadic-band", "pair-bonded"])

    # Build a name from morphological stems
    prefixes = ["Thorn", "Ash", "Mist", "Sun", "Moon", "Iron", "Crystal", "Void", "Bone", "Silk",
                "Deep", "Still", "Red", "Grey", "Pale"]
    suffixes = ["strider", "gazer", "weaver", "burrower", "skimmer", "drifter",
                "tongue", "wing", "scale", "hide", "crawler", "soarer"]
    name = f"{rng.choice(prefixes)}{rng.choice(suffixes).capitalize()}"

    # Signature traits (2-4)
    trait_count = rng.int(2, 4)
    traits = rng.sample(BODY_PARTS, trait_count)

    return {
        "name": name,
        "height_m": height,
        "limbs": limb_count,
        "body_plan": body_plan["build"],
        "skeleton": body_plan["skeleton"],
        "locomotion": locomotion,
        "diet": diet,
        "primary_sense": primary_sense,
        "activity_cycle": activity,
        "coloration": color,
        "integument": covering,
        "social_structure": social,
        "traits": traits,
        "gravity_adapted": gravity_tier,
        "notes": []
    }


def generate_ecosystem(seed, gravity, terrain, day_length, atmosphere=1.0, creature_count=6):
    """Generate a full ecosystem of creatures for a world."""
    rng = Seed(seed)
    creatures = []
    for i in range(creature_count):
        c_seed = f"{seed}:creature:{i}"
        creature = generate_creature(c_seed, gravity, terrain, day_length, atmosphere)
        creatures.append(creature)

    # Assign trophic levels
    sorted_creatures = sorted(creatures, key=lambda c: c["height_m"], reverse=True)
    for i, c in enumerate(sorted_creatures):
        if i == 0 and c["diet"] == "herbivore":
            c["notes"].append("dominant species — large herbivore")
        elif i == 0:
            c["notes"].append("apex predator")
        elif i == len(sorted_creatures) - 1:
            c["notes"].append("smallest species — high reproductive rate")
        if c["diet"] == "detritivore":
            c["notes"].append("waste processor — ecosystem recycler")

    return {
        "gravity_g": round(gravity, 2),
        "terrain": terrain,
        "day_length_h": day_length,
        "creature_count": len(creatures),
        "creatures": creatures,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Procedural bestiary — creatures from physics")
    parser.add_argument("--gravity", type=float, default=0.68, help="Surface gravity in G (0.4-2.0)")
    parser.add_argument("--terrain", type=str, default="forest", help="Terrain type")
    parser.add_argument("--day-length", type=float, default=24.0, help="Day length in hours")
    parser.add_argument("--atmosphere", type=float, default=1.0, help="Atmospheric density relative to Earth")
    parser.add_argument("--count", type=int, default=6, help="Number of creatures to generate")
    parser.add_argument("--seed", type=str, default="ember", help="RNG seed")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    eco = generate_ecosystem(
        seed=args.seed,
        gravity=args.gravity,
        terrain=args.terrain,
        day_length=args.day_length,
        atmosphere=args.atmosphere,
        creature_count=args.count,
    )

    if args.json:
        print(json.dumps(eco, indent=2))
    else:
        print(f"╔═══ Ecosystem — {args.terrain}, {args.gravity}G, {args.day_length}h days ═══╗\n")
        for c in eco["creatures"]:
            print(f"  {c['name']}")
            print(f"    Height: {c['height_m']}m  |  Limbs: {c['limbs']}  |  Build: {c['body_plan']}")
            print(f"    Locomotion: {c['locomotion']}  |  Diet: {c['diet']}")
            print(f"    Active: {c['activity_cycle']}  |  Sense: {c['primary_sense']}")
            print(f"    Coloration: {c['coloration']}  |  Covering: {c['integument']}")
            print(f"    Social: {c['social_structure']}")
            print(f"    Traits: {', '.join(c['traits'])}")
            if c["notes"]:
                print(f"    Notes: {'; '.join(c['notes'])}")
            print()
        print(f"╚═══ {eco['creature_count']} species ═══╝")
