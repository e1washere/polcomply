"""
Main CLI application for PolComply

Licensed under the Business Source License 1.1 (BSL).
See LICENSE file for full terms.
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .commands.map import map_command
from .commands.validate import validate_command

app = typer.Typer(
    name="polcomply",
    help="Polish KSeF compliance toolkit",
    add_completion=False,
    rich_markup_mode="rich",
)

console = Console()

# Add subcommands
app.add_typer(
    validate_command, name="validate", help="Validate XML documents against XSD schemas"
)
app.add_typer(map_command, name="map", help="Map invoice data between formats")


@app.command()
def version() -> None:
    """Show version information"""
    try:
        from polcomply import __version__

        console.print(f"PolComply SDK v{__version__}")
    except ImportError:
        console.print("PolComply SDK v0.1.0")


@app.command()
def info() -> None:
    """Show SDK information"""
    info_text = Text()
    info_text.append("PolComply SDK\n", style="bold blue")
    info_text.append("Polish KSeF compliance toolkit\n\n")
    info_text.append("Features:\n", style="bold")
    info_text.append("• XSD validation for FA-3 invoices\n")
    info_text.append("• Invoice data mapping\n")
    info_text.append("• CLI tools for validation\n")
    info_text.append("• Python SDK for integration\n\n")
    info_text.append("Licensed under Business Source License 1.1 (BSL)", style="dim")

    panel = Panel(info_text, title="SDK Information", border_style="blue")
    console.print(panel)


if __name__ == "__main__":
    app()
