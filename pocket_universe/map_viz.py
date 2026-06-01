"""SVG map generator for pocket universes — renders world topography from seed data."""

from pocket_universe.generator import Seed
import math


TERRAIN_COLORS = {
    "archipelago": "#4a9be0",
    "continent": "#6bbf59",
    "desert": "#e8c86a",
    "forest": "#3a7d34",
    "highlands": "#8b7355",
    "marsh": "#7a9a6b",
    "oceanic": "#2a6bb0",
    "plains": "#b8d4a0",
    "tundra": "#d4d4d4",
    "volcanic": "#8b4513",
}

HATCH_IDS = {
    "desert": "dots",
    "tundra": "dots",
    "forest": "crosshatch",
    "highlands": "hatch",
    "marsh": "waves",
    "oceanic": "waves",
}


def render_topology(universe: dict, width: int = 600, height: int = 400) -> str:
    """Generate an SVG topographical map of the world's regions."""

    seed = Seed(universe["seed"] + ":map-viz")
    regions = universe["regions"]
    n = len(regions)

    spread = 0.35 * min(width, height)

    # Generate region center points
    centers = []
    for _ in range(n):
        a = seed.float() * 360
        d = seed.float() * spread + 40
        cx = width / 2 + d * math.cos(math.radians(a))
        cy = height / 2 + d * math.sin(math.radians(a))
        cx = max(30, min(width - 30, cx))
        cy = max(30, min(height - 30, cy))
        centers.append((cx, cy))

    # Generate polygons for each region
    polygons = []
    for cx, cy in centers:
        num_pts = seed.int(6, 10)
        pts = []
        for j in range(num_pts):
            a = (j / num_pts) * 360 + seed.float() * 20
            r = seed.float() * 60 + 25
            px = cx + r * math.cos(math.radians(a))
            py = cy + r * math.sin(math.radians(a))
            pts.append(f"{px:.1f},{py:.1f}")
        polygons.append(" ".join(pts))

    terrain = universe["terrain"]
    bg_color = TERRAIN_COLORS.get(terrain, "#2a6bb0")

    # Build SVG as parts
    parts = []

    # Opening
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}">'
    )

    # Defs
    parts.append(f"""  <defs>
    <filter id="shadow" x="-2" y="-2" width="8" height="8">
      <feDropShadow dx="0" dy="1" stdDeviation="1" flood-color="rgba(0,0,0,0.6)"/>
    </filter>
    <pattern id="dots" width="8" height="8" patternUnits="userSpaceOnUse">
      <circle cx="2" cy="2" r="1" fill="rgba(0,0,0,0.15)"/>
    </pattern>
    <pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse">
      <line x1="0" y1="8" x2="8" y2="0" stroke="rgba(0,0,0,0.12)" stroke-width="1"/>
    </pattern>
    <pattern id="crosshatch" width="8" height="8" patternUnits="userSpaceOnUse">
      <line x1="0" y1="0" x2="8" y2="8" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
      <line x1="0" y1="8" x2="8" y2="0" stroke="rgba(0,0,0,0.1)" stroke-width="1"/>
    </pattern>
    <pattern id="waves" width="12" height="6" patternUnits="userSpaceOnUse">
      <path d="M0,3 Q3,0 6,3 Q9,6 12,3" fill="none" stroke="rgba(255,255,255,0.15)" stroke-width="1"/>
    </pattern>
    <radialGradient id="ocean" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="{bg_color}" stop-opacity="0.3"/>
      <stop offset="70%" stop-color="{bg_color}" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="#1a3a5c" stop-opacity="1"/>
    </radialGradient>
  </defs>""")

    # Ocean background
    parts.append(f'  <rect width="{width}" height="{height}" fill="#1a3a5c"/>')
    parts.append(f'  <rect width="{width}" height="{height}" fill="url(#ocean)"/>')

    # Sea-level contour rings
    for r in [0.85, 0.7, 0.55, 0.4]:
        d = (
            f'M {width/2},{height/2 - r*height/2} '
            f'A {r*width/2},{r*height/2} 0 1,0 {width/2},{height/2 + r*height/2} '
            f'A {r*width/2},{r*height/2} 0 1,0 {width/2},{height/2 - r*height/2}'
        )
        parts.append(f'  <path d="{d}" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="1"/>')

    # Landmass glow
    parts.append(
        f'  <ellipse cx="{width/2}" cy="{height/2}" rx="{spread+80}" '
        f'ry="{spread+60}" fill="#3a5a3a" opacity="0.3"/>'
    )

    # Graticule
    for i in range(0, width, 100):
        parts.append(f'  <line x1="{i}" y1="0" x2="{i}" y2="{height}" stroke="rgba(255,255,255,0.04)" stroke-width="1"/>')
    for i in range(0, height, 100):
        parts.append(f'  <line x1="0" y1="{i}" x2="{width}" y2="{i}" stroke="rgba(255,255,255,0.04)" stroke-width="1"/>')

    # Region polygons
    for i, r in enumerate(regions):
        color = TERRAIN_COLORS.get(r["terrain"], "#666")
        hatch_id = HATCH_IDS.get(r["terrain"])
        if hatch_id:
            parts.append(
                f'  <path d="{polygons[i]}" fill="url(#{hatch_id})" '
                f'fill-opacity="0.4" stroke="{color}" stroke-width="2" />'
            )
            parts.append(
                f'  <path d="{polygons[i]}" fill="{color}" '
                f'fill-opacity="0.3" stroke="rgba(0,0,0,0.3)" stroke-width="1.5" />'
            )
        else:
            parts.append(
                f'  <path d="{polygons[i]}" fill="{color}" '
                f'fill-opacity="0.6" stroke="rgba(0,0,0,0.3)" stroke-width="1.5" />'
            )

    # Labels
    for i, (cx, cy) in enumerate(centers):
        r = regions[i]
        parts.append(
            f'  <text x="{cx:.1f}" y="{cy-6:.1f}" text-anchor="middle" '
            f'font-family="monospace" font-size="10" fill="white" '
            f'font-weight="bold" filter="url(#shadow)">{r["name"]}</text>'
        )
        parts.append(
            f'  <text x="{cx:.1f}" y="{cy+8:.1f}" text-anchor="middle" '
            f'font-family="monospace" font-size="8" fill="rgba(255,255,255,0.6)" '
            f'font-style="italic">{r["terrain"].title()}</text>'
        )

    # Title and footer
    parts.append(
        f'  <text x="{width/2}" y="20" text-anchor="middle" font-family="monospace" '
        f'font-size="12" fill="rgba(255,255,255,0.4)">{universe["name"]} \u2014 Topographic Survey</text>'
    )
    parts.append(
        f'  <text x="{width/2}" y="{height-8}" text-anchor="middle" font-family="monospace" '
        f'font-size="8" fill="rgba(255,255,255,0.25)">seed: {universe["seed"]}</text>'
    )

    parts.append("</svg>")

    return "\n".join(parts)
