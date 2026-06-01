#!/usr/bin/env python3
"""Pocket Universe Generator — create a complete fictional microcosm from a seed word."""

import sys
import json
from pocket_universe.generator import generate
from pocket_universe.format import render
from pocket_universe.map_viz import render_topology


def main():
    import click

    @click.command()
    @click.argument("seed", required=False)
    @click.option("--json", "as_json", is_flag=True, help="Output as raw JSON")
    @click.option("--map", "as_map", is_flag=True, help="Generate SVG map file")
    @click.option("--output", "-o", "output_path", default=None, help="Save output to file")
    @click.option("--list-seeds", is_flag=True, help="Generate multiple seeds from a list file")
    def cli(seed, as_json, as_map, output_path, list_seeds):
        if list_seeds:
            import random
            words = [
                "ember", "thaw", "drift", "cinder", "hollow", "veil",
                "fold", "knot", "pulse", "spark", "shard", "echo",
                "bloom", "rust", "salt", "tar", "lime", "frost",
                "dust", "flint", "mica", "resin", "silt", "brine",
                "char", "flux", "grit", "haze", "loam", "moss",
            ]
            for w in random.sample(words, min(5, len(words))):
                u = generate(w)
                if as_json:
                    print(json.dumps(u, indent=2))
                else:
                    print(render(u))
                    print("─" * 60)
            return

        if not seed:
            click.echo("Usage: pocket-universe <seed>")
            click.echo("   or: pocket-universe --list-seeds")
            sys.exit(1)

        universe = generate(seed)

        if as_map:
            svg = render_topology(universe)
            path = output_path or f"{seed}-world-map.svg"
            with open(path, "w") as f:
                f.write(svg)
            click.echo(f"Map saved to {path}")
            return
        if as_json:
            print(json.dumps(universe, indent=2))
        else:
            print(render(universe))

    cli()


if __name__ == "__main__":
    main()
