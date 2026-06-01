"""Climate and weather generation — derived from world physics and terrain."""

from pocket_universe.generator import Seed


def generate_climate(universe: dict) -> dict:
    """Generate climate zones and weather patterns from world data."""
    phys = universe["physics"]
    seed = Seed(universe["seed"] + ":climate")
    
    tilt = phys["axial_tilt"]
    day = phys["day_length"]
    gravity = phys["gravity"]
    
    # Climate zones determined by axial tilt
    # Higher tilt = more extreme seasons, weaker latitudinal bands
    if tilt < 15:
        polar_cap = 75
        tropic_band = 15
        seasonality = "mild"
    elif tilt < 30:
        polar_cap = 65
        tropic_band = 25
        seasonality = "moderate"
    elif tilt < 45:
        polar_cap = 55
        tropic_band = 30
        seasonality = "extreme"
    else:
        polar_cap = 45
        tropic_band = 35
        seasonality = "chaotic"
    
    # Number of prevailing wind cells
    wind_cells = seed.int(3, 6)
    
    wind_patterns = [
        "trade winds", "westerlies", "polar easterlies",
        "monsoon gyres", "zephyr bands", "katabatic flows",
        "antipodal convection", "rift updrafts",
    ]
    selected_winds = seed.sample(wind_patterns, min(wind_cells, len(wind_patterns)))
    
    # Generate climate zones
    zone_names = [
        "Equatorial Doldrums", "Tropical Belt", "Subtropical Ridge",
        "Temperate Zone", "Subpolar Low", "Polar Cap",
        "Rain Shadow", "Highland Steppe",
    ]
    
    num_zones = seed.int(4, 7)
    active_zones = seed.sample(zone_names, num_zones)
    
    # Generate weather events
    event_types = [
        "thunderstorm", "blizzard", "dust storm", "monsoon downpour",
        "ice fog", "heat wave", "cold snap", "haboob",
        "firestorm", "hail", "whiteout", "rain of ash",
    ]
    
    num_events = seed.int(3, 6)
    events = seed.sample(event_types, num_events)
    
    # Season characteristics
    seasons = universe["calendar"]["seasons"]
    season_weather = {}
    for s in seasons:
        temps = {"Awakening": "warming", "Kindling": "hot", "Flourish": "temperate",
                 "Waning": "cooling", "Duskfall": "cold", "Hollowing": "frigid",
                 "Deepfrost": "arctic", "Thaw": "thawing"}
        precips = {"Awakening": "rain", "Kindling": "dry", "Flourish": "variable",
                   "Waning": "rain", "Duskfall": "snow", "Hollowing": "snow",
                   "Deepfrost": "ice", "Thaw": "sleet"}
        
        temp = temps.get(s, "temperate")
        precip = precips.get(s, "variable")
        
        # Modify by tilt
        if seasonality == "extreme" and temp in ("temperate", "cooling"):
            temp = "extreme " + temp
        if seasonality == "mild" and temp in ("frigid", "arctic"):
            temp = "cool"
        
        season_weather[s] = {"temperature": temp, "precipitation": precip}
    
    # Precipitation patterns
    rain_shadow_zones = [z for z in active_zones if "Rain" in z or "Steppe" in z]
    
    return {
        "axial_tilt_classification": seasonality,
        "polar_cap_latitude": polar_cap,
        "tropic_band_latitude": tropic_band,
        "wind_cells": selected_winds,
        "climate_zones": active_zones,
        "extreme_weather": events,
        "seasonal_patterns": season_weather,
        "annual_precipitation": seed.choice([
            "scarce", "low", "moderate", "abundant", "torrential"
        ]),
        "dominant_wind": selected_winds[0] if selected_winds else "variable",
        "notable_feature": seed.choice([
            "permanent anticyclone over the eastern continent",
            "ring-shadow band casting a perpetual twilight belt",
            "tidal locking resonance creating a storm belt",
            "volcanic winter cycle every 12-15 years",
            "bipolar circulation with mirror storms",
            "high-altitude ice crystals forming prismatic displays",
        ]),
    }
