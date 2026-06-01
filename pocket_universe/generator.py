"""Procedural generation engine — seed-based, deterministic, no external deps."""

import hashlib
import struct
import math

# ── Seeded RNG (SplitMix64 style) ──────────────────────────────────────────

class Seed:
    """A deterministic seed that can fork into child seeds for different systems."""

    def __init__(self, value: int | str):
        if isinstance(value, str):
            h = hashlib.sha256(value.encode("utf-8")).digest()
            value = struct.unpack("<Q", h[:8])[0]  # first 8 bytes as u64
        self._state = value & 0xFFFFFFFFFFFFFFFF

    def _next(self) -> int:
        self._state = (self._state + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
        z = self._state
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
        return z ^ (z >> 31)

    def u64(self) -> int:
        """Random unsigned 64-bit integer."""
        return self._next()

    def u32(self) -> int:
        """Random unsigned 32-bit integer."""
        return self._next() & 0xFFFFFFFF

    def float(self) -> float:
        """Random float in [0.0, 1.0)."""
        return (self._next() >> 11) * (1.0 / (1 << 53))

    def int(self, lo: int, hi: int) -> int:
        """Random integer in [lo, hi] inclusive."""
        return lo + (self.u64() % (hi - lo + 1))

    def choice(self, items: list) -> object:
        """Pick a random element."""
        return items[self.int(0, len(items) - 1)]

    def shuffle(self, items: list) -> list:
        """Fisher-Yates shuffle — returns new list."""
        result = list(items)
        for i in range(len(result) - 1, 0, -1):
            j = self.int(0, i)
            result[i], result[j] = result[j], result[i]
        return result

    def sample(self, items: list, k: int) -> list:
        """Pick k random elements without replacement."""
        shuffled = self.shuffle(items)
        return shuffled[:k]

    def fork(self, tag: str) -> "Seed":
        """Create a child seed for a specific subsystem."""
        raw = f"{self._state:x}:{tag}"
        h = hashlib.sha256(raw.encode("utf-8")).digest()
        val = struct.unpack("<Q", h[:8])[0]
        return Seed(val)

    def weighted(self, weights: dict[str, float]) -> str:
        """Pick a key from a dict of {key: weight}."""
        total = sum(weights.values())
        r = self.float() * total
        cumulative = 0.0
        for key, weight in weights.items():
            cumulative += weight
            if r < cumulative:
                return key
        return list(weights.keys())[-1]


# ── Naming Tables ──────────────────────────────────────────────────────────

# These feel like they belong to different kinds of places.
# Each table is a different "mood" for generating names.

SOVEREIGN_SUFFIXES = [
    " Dominion", " Reach", " March", " Imperium", " Accord",
    " Compact", " Protectorate", " Commonwealth", " Federation",
    " Sovereignty", " Expanse", " Verge", " Pale", " Demesne",
]

GEOGRAPHIC_PREFIXES = [
    "The", "Old", "New", "Sunken", "Iron", "Crimson", "Pale",
    "Deep", "High", "Far", "Silent", "Burning", "Frozen", "Glass",
]

CORE_STEMS = [
    "Ar", "Val", "Dor", "Mir", "Kal", "Vor", "Tar", "Bel",
    "Cor", "Lor", "Nir", "Sel", "Mor", "Pal", "Ran", "Sol",
    "Thal", "Vern", "Xyl", "Zeph", "Bryn", "Cael", "Durn", "Ery",
    "Faln", "Glyr", "Hast", "Ith", "Jorn", "Kest", "Lith", "Morn",
]

CORE_MIDDLES = [
    "an", "en", "in", "on", "ar", "or", "el", "al", "ur", "ir",
    "ath", "eth", "ith", "oth", "and", "end", "ind", "ond",
    "mar", "nar", "var", "dor", "lor", "mor", "nor", "tor",
]

CORE_ENDS = [
    "ia", "is", "os", "us", "ar", "or", "on", "en", "ax", "ox",
    "ium", "ath", "esh", "oth", "and", "eld", "olt", "ant",
    "ore", "ara", "oss", "ell", "ara", "une", "ain", "ath",
]

TERRAIN_TYPES = {
    "archipelago": ("chain", "isles", "keys", "atolls", "shoals", "sounds", "straits", "reefs"),
    "continent": ("land", "main", "vast", "deep", "heart", "spine", "shield", "cradle"),
    "desert": ("waste", "dunes", "sands", "barrens", "scar", "ash", "drift", "burn"),
    "forest": ("weald", "wood", "deep", "thicket", "grove", "copse", "holt", "shade"),
    "highlands": ("peaks", "heights", "spires", "teeth", "crown", "ridge", "horn", "crest"),
    "marsh": ("fen", "mire", "bog", "moor", "low", "sump", "wash", "quag"),
    "oceanic": ("deep", "brine", "trench", "abyss", "gulf", "current", "drift", "swell"),
    "plains": ("fields", "steppe", "downs", "mead", "plain", "sward", "lea", "flats"),
    "tundra": ("frost", "barrens", "wastes", "chill", "ice", "rime", "snows", "drift"),
    "volcanic": ("furnace", "caldera", "scorch", "forge", "cinder", "slag", "vents", "spire"),
}

# ── World Generation ───────────────────────────────────────────────────────

def generate(seed_str: str) -> dict:
    """Generate a complete pocket universe from a seed string."""

    root = Seed(seed_str)

    # ── World identity ─────────────────────────────────────────────────
    world_seed = root.fork("world")
    terrain_type = world_seed.choice(list(TERRAIN_TYPES.keys()))
    terrain_names = TERRAIN_TYPES[terrain_type]

    # Generate a 2-3 syllable name
    stem = world_seed.choice(CORE_STEMS)
    middle = world_seed.choice(CORE_MIDDLES)
    end = world_seed.choice(CORE_ENDS)
    name = f"{stem}{middle}{end}"
    # Capitalize properly
    name = name[0].upper() + name[1:]

    suffix = world_seed.choice(terrain_names)
    full_name = f"{name} {suffix.capitalize()}"

    # ── Physical properties ────────────────────────────────────────────
    phys_seed = root.fork("physics")
    radius = round(phys_seed.float() * 0.8 + 0.4, 2)  # 0.4–1.2 Earth radii
    gravity = round(radius * phys_seed.float() * 1.2 + 0.6, 2)
    day_length = round(phys_seed.float() * 20 + 10, 1)  # 10–30 hours
    year_length = round(10 ** (phys_seed.float() * 2.5 + 0.7), 1)  # 50–1600 days

    axial_tilt = round(phys_seed.float() * 50 + 5, 1)  # 5°–55°
    has_rings = phys_seed.float() < 0.25
    moon_count = phys_seed.int(0, 4)

    # ── Map ────────────────────────────────────────────────────────────
    map_seed = root.fork("map")
    region_count = map_seed.int(4, 8)
    region_stems = [map_seed.choice(CORE_STEMS) + map_seed.choice(CORE_ENDS) for _ in range(region_count)]
    regions = [r[0].upper() + r[1:] for r in region_stems]

    # Generate terrain for each region
    other_terrains = [t for t in TERRAIN_TYPES if t != terrain_type]
    region_terrains = [terrain_type] + [map_seed.choice(other_terrains) for _ in range(region_count - 1)]

    # Capitals / cities
    city_seed = root.fork("cities")
    city_count = city_seed.int(3, 6)
    cities = []
    for _ in range(city_count):
        s = city_seed.choice(CORE_STEMS) + city_seed.choice(CORE_MIDDLES) + city_seed.choice(CORE_ENDS)
        cname = s[0].upper() + s[1:].lower()
        cities.append(cname)

    # ── Calendar ───────────────────────────────────────────────────────
    cal_seed = root.fork("calendar")
    season_names = [
        "Awakening", "Kindling", "Flourish", "Waning",
        "Duskfall", "Hollowing", "Deepfrost", "Thaw",
    ]
    # Pick 2-6 seasons based on axial tilt
    num_seasons = cal_seed.int(2, 6)
    active_seasons = cal_seed.sample(season_names, num_seasons)
    # Order them
    season_order = [s for s in season_names if s in active_seasons]

    month_names = [
        "Primer", "Hearth", "Bloom", "Rill", "Sunwind", "Goldleaf",
        "Reap", "Shade", "Falling", "Barren", "Hewn", "Ember",
    ]
    active_months = cal_seed.sample(month_names, 8)
    festival_count = cal_seed.int(2, 5)
    festival_stems = ["Feast", "Night", "Dawn", "Rite", "Trial", "Crown", "Binding", "Turning"]
    festivals = cal_seed.sample(festival_stems, festival_count)

    # ── Mythology ──────────────────────────────────────────────────────
    myth_seed = root.fork("mythology")

    archetypes = {
        "Creator": ["The Shaper", "The First Breath", "The Weaver", "The Potter", "The Sower"],
        "Destroyer": ["The Sunderer", "The Devourer", "The Unmaker", "The Ashen", "The End"],
        "Trickster": ["The Grin", "The Mirror", "The Unraveler", "The Forked Tongue", "The Prank"],
        "Guardian": ["The Gatekeeper", "The Watcher", "The Warden", "The Anchor", "The Shield"],
        "Scholar": ["The Rememberer", "The Archive", "The Inquisitor", "The Loom", "The Scribe"],
        "Traveler": ["The Wanderer", "The Drift", "The Passage", "The Compass", "The Stranger"],
    }

    pantheon_size = myth_seed.int(3, 5)
    selected_archetypes = myth_seed.sample(list(archetypes.keys()), pantheon_size)
    gods = {}
    for arch in selected_archetypes:
        god_name = myth_seed.choice(archetypes[arch])
        # Give them a domain
        domains = {
            "Creator": ["creation", "life", "art", "dawn", "birth"],
            "Destroyer": ["destruction", "death", "ending", "change", "fire"],
            "Trickster": ["chaos", "luck", "secrets", "laughter", "doors"],
            "Guardian": ["protection", "duty", "oaths", "walls", "memory"],
            "Scholar": ["knowledge", "truth", "stars", "time", "wisdom"],
            "Traveler": ["journeys", "trade", "horizons", "storms", "discovery"],
        }
        domain = myth_seed.choice(domains[arch])
        epithet_stems = ["Whose Eyes Are", "Who Walks", "Of the", "Whose Voice Is", "Who Holds"]
        epithet = myth_seed.choice(epithet_stems) + " " + myth_seed.choice(CORE_STEMS + CORE_ENDS).lower()
        gods[god_name] = {
            "archetype": arch,
            "domain": domain,
            "epithet": epithet,
        }

    # Choose a creation myth pattern
    creation_patterns = [
        "dreamt into being",
        "carved from the body of a slain titan",
        "formed from the first note of a song",
        "woven on a cosmic loom",
        "shaped from silence",
        "born from a tear in the void",
        "crystallized from a thought",
        "pulled from deep water with a great hook",
    ]
    creation_myth = myth_seed.choice(creation_patterns)

    # ── Ecology ────────────────────────────────────────────────────────
    eco_seed = root.fork("ecology")

    flora_prefixes = ["Ghost", "Iron", "Blood", "Star", "Thorn", "Moon", "Sun", "Ash", "Void", "Crystal"]
    fauna_prefixes = ["Shadow", "Ember", "Frost", "Dune", "Vale", "Mist", "Stone", "Cinder"]
    creature_types = ["Stalker", "Drifter", "Weaver", "Burrower", "Glider", "Swimmer"]

    flora = []
    for _ in range(eco_seed.int(4, 7)):
        f = eco_seed.choice(flora_prefixes) + eco_seed.choice(CORE_MIDDLES).capitalize() + eco_seed.choice(["vine", "moss", "weed", "fern", "lichen", "bloom", "root", "bark", "pod"])
        flora.append(f)

    fauna = []
    for _ in range(eco_seed.int(4, 7)):
        f = eco_seed.choice(fauna_prefixes) + eco_seed.choice(creature_types)
        fauna.append(f)

    # Determine which flora/fauna are dominant signatures
    signature_flora = eco_seed.choice(flora)
    signature_fauna = eco_seed.choice(fauna)

    # ── Language fragment ──────────────────────────────────────────────
    lang_seed = root.fork("language")

    word_themes = {
        "greeting": ["salutation", "acknowledgment", "welcome"],
        "water": ["rain", "river", "sea", "ice", "spring"],
        "home": ["house", "hearth", "settlement", "cave", "nest"],
        "sky": ["star", "cloud", "wind", "storm", "sun"],
        "earth": ["stone", "soil", "mountain", "valley", "cave"],
        "life": ["birth", "growth", "death", "sleep", "awake"],
        "journey": ["path", "road", "horizon", "return", "wander"],
        "spirit": ["soul", "dream", "shadow", "light", "breath"],
    }

    lexicon = {}
    for theme, concepts in word_themes.items():
        used_words = set()
        for concept in concepts:
            word = ""
            attempts = 0
            while not word or word in used_words:
                syllables = lang_seed.int(2, 3)  # min 2 to avoid single-letter words
                parts = []
                for _ in range(syllables):
                    pool = CORE_STEMS + CORE_MIDDLES
                    p = lang_seed.choice(pool).lower()
                    parts.append(p)
                word = "".join(parts)
                attempts += 1
                if attempts > 20:
                    break
            used_words.add(word)
            lexicon[concept] = word

    # Determine basic grammar rule
    grammar_patterns = [
        "SOV — subject-object-verb (like Japanese, Turkish)",
        "SVO — subject-verb-object (like English)",
        "VSO — verb-subject-object (like Welsh, Arabic)",
        "OVS — object-verb-subject (rare, alien feel)",
        "Free — case-marked, flexible word order",
    ]
    grammar = lang_seed.choice(grammar_patterns)
    has_gender = lang_seed.float() < 0.4
    has_tones = lang_seed.float() < 0.35

    # ── Culture ────────────────────────────────────────────────────────
    cult_seed = root.fork("culture")

    social_structures = [
        "meritocratic council of elders",
        "hereditary monarchy under a sacred sovereign",
        "stratified guild system",
        "consensus-based village assemblies",
        "tribal chiefdoms bound by blood-oaths",
        "theocratic hierarchy serving the pantheon",
        "collective hive-mind consensus",
        "loose federation of autonomous holds",
    ]
    social_structure = cult_seed.choice(social_structures)

    values = cult_seed.sample([
        "honor", "knowledge", "hospitality", "strength", "cunning",
        "patience", "adaptability", "memory", "curiosity", "silence",
    ], 3)

    taboos = cult_seed.sample([
        "naming the dead", "refusing hospitality", "wasting water",
        "breaking a vow", "shedding blood without cause",
        "looking at the sun during eclipse", "eating while standing",
        "speaking during the night meal", "touching another's tools",
    ], 2)

    burial_traditions = [
        "returned to the earth in unmarked graves",
        "cast into the deepest waters",
        "preserved and kept in ancestral halls",
        "burned on pyres facing west",
        "left on high peaks for the sky to take",
        "planted as trees in remembrance groves",
        "fed to the sacred fauna of the realm",
    ]
    burial = cult_seed.choice(burial_traditions)

    ## ── Compile result ──────────────────────────────────────────────────
    return {
        "seed": seed_str,
        "name": full_name,
        "terrain": terrain_type,
        "physics": {
            "radius": radius,
            "gravity": gravity,
            "day_length": day_length,
            "year_length": year_length,
            "axial_tilt": axial_tilt,
            "has_rings": has_rings,
            "moon_count": moon_count,
        },
        "regions": [
            {"name": regions[i], "terrain": region_terrains[i]}
            for i in range(region_count)
        ],
        "cities": cities,
        "calendar": {
            "seasons": season_order,
            "months": active_months,
            "festivals": festivals,
        },
        "pantheon": gods,
        "creation_myth": creation_myth,
        "ecology": {
            "flora": flora,
            "fauna": fauna,
            "signature_flora": signature_flora,
            "signature_fauna": signature_fauna,
        },
        "language": {
            "lexicon": lexicon,
            "grammar": grammar,
            "has_gender": has_gender,
            "has_tones": has_tones,
        },
        "culture": {
            "social_structure": social_structure,
            "values": values,
            "taboos": taboos,
            "burial": burial,
        },
    }
