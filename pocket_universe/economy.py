"""Economy and trade — derived from terrain, culture, and seeded variation."""

from pocket_universe.generator import Seed


RESOURCE_POOL = {
    "archipelago": {
        "exports": ["pearls", "sea salt", "dried fish", "coral", "amber", "silk kelp"],
        "imports": ["grain", "timber", "metal ore", "leather"],
    },
    "continent": {
        "exports": ["grain", "livestock", "iron ore", "coal", "stone", "timber"],
        "imports": ["spices", "salt", "exotic timber", "precious gems"],
    },
    "desert": {
        "exports": ["salt", "glass", "spices", "precious metals", "fossil fuels"],
        "imports": ["water", "grain", "timber", "livestock", "cloth"],
    },
    "forest": {
        "exports": ["timber", "herbs", "game", "resin", "medicinal bark", "dyes"],
        "imports": ["metal", "salt", "stone", "glass"],
    },
    "highlands": {
        "exports": ["precious gems", "metal ore", "stone", "wool", "cheese"],
        "imports": ["grain", "wine", "cloth", "spices"],
    },
    "marsh": {
        "exports": ["peat", "medicinal leeches", "rice", "reeds", "amphibian leather"],
        "imports": ["metal", "dry timber", "salt", "cloth"],
    },
    "oceanic": {
        "exports": ["whale oil", "sea salt", "fish", "shell", "ambergris"],
        "imports": ["metal", "grain", "timber", "cloth"],
    },
    "plains": {
        "exports": ["grain", "leather", "wool", "horses", "cheese"],
        "imports": ["metal ore", "spices", "precious gems", "salt"],
    },
    "tundra": {
        "exports": ["furs", "ivory", "whale products", "cold-adapted livestock"],
        "imports": ["grain", "metal", "cloth", "spices", "fuel"],
    },
    "volcanic": {
        "exports": ["obsidian", "sulfur", "pumice", "geothermal energy", "rare minerals"],
        "imports": ["food", "timber", "cloth", "water"],
    },
}

LUXURY_GOODS = [
    "spice silk", "glow wine", "star-sapphires", "moon-opals",
    "dream-cured tobacco", "amber honey", "obsidian mirrors",
    "living jewelry", "memory-salt", "phoenix feathers",
    "dusk-wood", "echo shells", "void-dyed cloth",
    "singing crystals", "fermented cloud-nectar",
]

CURRENCY_FORMS = [
    "stamped bronze coins",
    "carved bone discs",
    "woven shell strings",
    "marked clay tablets",
    "gold rings of standardized weight",
    "cowrie shells on hemp cord",
    "iron ingots graded by purity",
    "glass beads with sealed air bubbles",
    "crimson-dyed wool strips",
    "salt bricks stamped with a seal",
    "bar-coded crystal slivers readable in sunlight",
    "etched copper leaves",
]


def generate_economy(universe: dict) -> dict:
    """Generate economic data for a pocket universe."""
    seed = Seed(universe["seed"] + ":economy")
    terrain = universe["terrain"]
    culture = universe["culture"]

    pools = RESOURCE_POOL.get(terrain, RESOURCE_POOL["plains"])
    exports = seed.sample(pools["exports"], seed.int(3, 5))
    imports = seed.sample(pools["imports"], seed.int(2, 4))

    # Luxury goods — 1-3 that this world is known for
    luxury_count = seed.int(1, 3)
    luxury_goods = seed.sample(LUXURY_GOODS, luxury_count)

    # Currency
    currency = seed.choice(CURRENCY_FORMS)

    # Economic structure
    structures = [
        "guild-regulated market economy with protectionist tariffs",
        "feudal agrarian with localized barter networks",
        "mercantile city-states controlling trade routes",
        "resource-extraction monoculture exporting to off-world",
        "subsistence agriculture supplemented by craft exports",
        "command economy managed by theocratic administrators",
        "gift-based prestige economy for elite goods, barter for necessities",
        "post-scarcity communal allocation overseen by councils",
    ]
    structure = seed.choice(structures)

    # Trade partners — generate names of nearby realms
    trade_partners = []
    for _ in range(seed.int(2, 4)):
        stem1 = seed.choice(["Ar", "Bel", "Cor", "Dor", "Fal", "Glyr", "Hast", "Ith", "Jorn", "Kest", "Lith", "Mir"])
        stem2 = seed.choice(["an", "en", "in", "on", "ar", "or", "el"])
        stem3 = seed.choice(["ia", "is", "os", "us", "ar", "or", "ath"])
        name = f"{stem1}{stem2}{stem3}".capitalize()
        trade_partners.append(name)

    # Economic health
    health_indicators = [
        ("stable", "steady growth in the craft sector"),
        ("booming", "a resource rush drawing foreign merchants"),
        ("stagnant", "trade routes disrupted by political instability"),
        ("declining", "over-extraction depleting key resources"),
        ("recovering", "post-conflict reconstruction driving demand"),
        ("isolated", "self-sufficient but cut off from external markets"),
    ]
    health, details = seed.choice(health_indicators)

    return {
        "structure": structure,
        "currency": currency,
        "exports": exports,
        "imports": imports,
        "luxury_goods": luxury_goods,
        "trade_partners": trade_partners,
        "economic_health": {"status": health, "details": details},
        "primary_industry": exports[0] if exports else "subsistence",
    }
