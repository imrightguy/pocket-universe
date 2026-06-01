"""Rich-formatted output for a pocket universe."""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box


def render(universe: dict) -> str:
    """Render a universe dict as a rich-formatted string and return it."""
    console = Console(width=80, force_terminal=True)

    lines = []
    with console.capture() as capture:
        _render(console, universe)
    return capture.get()


def _render(console: Console, u: dict) -> None:
    phy = u["physics"]
    cal = u["calendar"]
    eco = u["ecology"]
    lang = u["language"]
    cul = u["culture"]

    # ── Title ──────────────────────────────────────────────────────────
    title = Text()
    title.append(u["name"], style="bold cyan")
    title.append(f"  •  {u['terrain'].title()} World", style="dim white")
    title.append(f"\nSeed: {u['seed']}", style="italic dim")
    console.print(Panel(title, box=box.HEAVY, border_style="cyan"))
    console.print()

    # ── Physics ────────────────────────────────────────────────────────
    t = Table.grid(padding=(0, 2))
    t.add_column(style="yellow", justify="right")
    t.add_column(style="white")
    t.add_row("Radius", f"{phy['radius']}× Earth")
    t.add_row("Gravity", f"{phy['gravity']}× Earth")
    t.add_row("Day", f"{phy['day_length']}h")
    t.add_row("Year", f"{phy['year_length']} days")
    t.add_row("Axial tilt", f"{phy['axial_tilt']}°")
    t.add_row("Rings", "Yes" if phy["has_rings"] else "No")
    t.add_row("Moons", str(phy["moon_count"]))
    console.print(Panel(t, title="[bold]Physics[/bold]", border_style="blue"))
    console.print()

    # ── Regions ────────────────────────────────────────────────────────
    reg_table = Table(box=box.SIMPLE, border_style="green")
    reg_table.add_column("Region", style="green")
    reg_table.add_column("Terrain", style="white")
    for r in u["regions"]:
        reg_table.add_row(r["name"], r["terrain"].title())
    console.print(Panel(reg_table, title="[bold]Regions[/bold]", border_style="green"))
    console.print()

    # ── Cities ─────────────────────────────────────────────────────────
    console.print("[bold]Cities:[/bold]", style="magenta")
    for city in u["cities"]:
        console.print(f"  • {city}")
    console.print()

    # ── Calendar ───────────────────────────────────────────────────────
    c = Table.grid(padding=(0, 2))
    c.add_column(style="cyan", justify="right")
    c.add_column(style="white")
    c.add_row("Seasons", ", ".join(cal["seasons"]))
    c.add_row("Months", ", ".join(cal["months"]))
    c.add_row("Festivals", ", ".join(cal["festivals"]))
    console.print(Panel(c, title="[bold]Calendar[/bold]", border_style="cyan"))
    console.print()

    # ── Pantheon ───────────────────────────────────────────────────────
    pantheon_table = Table(box=box.SIMPLE, border_style="yellow")
    pantheon_table.add_column("God", style="bold yellow")
    pantheon_table.add_column("Archetype", style="white")
    pantheon_table.add_column("Domain", style="green")
    pantheon_table.add_column("Epithet", style="dim italic")
    for name, info in u["pantheon"].items():
        pantheon_table.add_row(name, info["archetype"], info["domain"], info["epithet"])
    console.print(Panel(pantheon_table, title="[bold]Pantheon[/bold]", border_style="yellow"))
    console.print(f"  [dim italic]The world was {u['creation_myth']}.[/dim italic]")
    console.print()

    # ── Ecology ────────────────────────────────────────────────────────
    console.print("[bold]Signature Species[/bold]", style="green")
    console.print(f"  Flora: [italic]{eco['signature_flora']}[/italic]")
    console.print(f"  Fauna: [italic]{eco['signature_fauna']}[/italic]")
    console.print()
    console.print(f"  [dim]Flora:[/dim] {', '.join(eco['flora'])}")
    console.print(f"  [dim]Fauna:[/dim] {', '.join(eco['fauna'])}")
    console.print()

    # ── Language ───────────────────────────────────────────────────────
    lex_table = Table(box=box.SIMPLE, border_style="blue")
    lex_table.add_column("Concept", style="yellow", justify="right")
    lex_table.add_column("Word", style="cyan")
    for concept, word in lang["lexicon"].items():
        lex_table.add_row(concept, word)
    console.print(Panel(lex_table, title="[bold]Language Fragments[/bold]", border_style="blue"))
    syntax_info = f"Grammar: {lang['grammar']}"
    if lang["has_gender"]:
        syntax_info += " • Grammatical gender"
    if lang["has_tones"]:
        syntax_info += " • Tonal"
    console.print(f"  [dim]{syntax_info}[/dim]")
    console.print()

    # ── Culture ────────────────────────────────────────────────────────
    console.print("[bold]Social Structure[/bold]", style="magenta")
    console.print(f"  {cul['social_structure']}")
    console.print()
    console.print(f"[bold]Values:[/bold] {', '.join(cul['values'])}")
    console.print(f"[bold]Taboos:[/bold] {', '.join(cul['taboos'])}")
    console.print()
    console.print(f"[dim]The dead are {cul['burial']}.[/dim]")
