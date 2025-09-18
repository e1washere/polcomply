"""
Validate command for PolComply CLI

Licensed under the Business Source License 1.1 (BSL).
See LICENSE file for full terms.
"""

from pathlib import Path

import typer
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

from reporting.html_report import generate_html_report
from validators.xsd import ValidationError, XSDValidator
from validators.paths import resolve_fa3_schema

console = Console()

validate_command = typer.Typer(
    name="validate",
    help="Validate XML documents against XSD schemas",
    rich_markup_mode="rich",
)


@validate_command.command("invoice")
def validate_invoice(
    xml_file: Path = typer.Argument(..., help="Path to XML invoice file"),
    schema: Path = typer.Option(None, "--schema", "-s", help="Path to XSD schema file (auto-resolve FA-3 if not provided)"),
    output_format: str = typer.Option(
        "table", "--format", "-f", help="Output format: table, json, summary"
    ),
    report: Path = typer.Option(
        None, "--report", "-r", help="Path to save HTML report"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed error information"
    ),
    show_xml: bool = typer.Option(
        False, "--show-xml", help="Show XML content with error highlighting"
    ),
):
    """
    Validate FA-3 invoice XML against XSD schema

    Example:
        polcomply validate invoice.xml --schema schemas/FA-3.xsd
    """
    try:
        # Auto-resolve schema if not provided
        if schema is None:
            schema = resolve_fa3_schema()
            if schema is None:
                console.print("[red]❌ FA-3 schema not found. Please provide --schema or place FA-3.xsd in schemas/[/red]")
                raise typer.Exit(1)
            console.print(f"[dim]Using auto-resolved schema: {schema}[/dim]")
        
        # Validate XML file
        validator = XSDValidator(schema)
        errors = validator.validate_file(xml_file)

        # Generate HTML report if requested
        if report:
            generate_html_report(errors, str(xml_file.name), report)
            console.print(f"[green]✓[/green] HTML report saved to: {report}")

        if output_format == "json":
            _output_json(errors, xml_file)
        elif output_format == "summary":
            _output_summary(errors, xml_file)
        else:
            _output_table(errors, xml_file, verbose, show_xml)

    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise typer.Exit(1)


@validate_command.command("xml")
def validate_xml(
    xml_file: Path = typer.Argument(..., help="Path to XML file"),
    schema: Path = typer.Option(..., "--schema", "-s", help="Path to XSD schema file"),
    output_format: str = typer.Option(
        "table", "--format", "-f", help="Output format: table, json, summary"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed error information"
    ),
):
    """
    Validate any XML file against XSD schema

    Example:
        polcomply validate xml document.xml --schema schemas/document.xsd
    """
    try:
        # Validate XML file
        validator = XSDValidator(schema)
        errors = validator.validate_file(xml_file)

        if output_format == "json":
            _output_json(errors, xml_file)
        elif output_format == "summary":
            _output_summary(errors, xml_file)
        else:
            _output_table(errors, xml_file, verbose, False)

    except FileNotFoundError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        raise typer.Exit(1)


def _output_table(
    errors: list[ValidationError], xml_file: Path, verbose: bool, show_xml: bool
):
    """Output validation results as a table"""

    if not errors:
        console.print(
            "[green]✓[/green] [bold green]Validation successful![/bold green]"
        )
        console.print(f"File: [blue]{xml_file}[/blue]")
        return

    # Create error table
    table = Table(title=f"Validation Errors - {xml_file.name}")
    table.add_column("Line", style="cyan", width=6)
    table.add_column("Column", style="cyan", width=8)
    table.add_column("Code", style="yellow", width=20)
    table.add_column("Message", style="red")

    for error in errors:
        line = str(error.line) if error.line else "-"
        column = str(error.column) if error.column else "-"
        code = error.code or "-"
        message = error.message

        if not verbose and len(message) > 80:
            message = message[:77] + "..."

        table.add_row(line, column, code, message)

    console.print(table)

    # Show XML with highlighting if requested
    if show_xml and xml_file.exists():
        try:
            with open(xml_file, encoding="utf-8") as f:
                xml_content = f.read()

            syntax = Syntax(xml_content, "xml", theme="monokai", line_numbers=True)
            console.print("\n[bold]XML Content:[/bold]")
            console.print(syntax)
        except Exception as e:
            console.print(
                f"[yellow]Warning: Could not display XML content: {e}[/yellow]"
            )


def _output_json(errors: list[ValidationError], xml_file: Path):
    """Output validation results as JSON"""
    import json

    result = {
        "file": str(xml_file),
        "valid": len(errors) == 0,
        "error_count": len(errors),
        "errors": [error.to_dict() for error in errors],
    }

    console.print(json.dumps(result, indent=2))


def _output_summary(errors: list[ValidationError], xml_file: Path):
    """Output validation results as summary"""

    if not errors:
        console.print(
            f"[green]✓[/green] [bold green]Valid[/bold green] - {xml_file.name}"
        )
    else:
        console.print(
            f"[red]✗[/red] [bold red]Invalid[/bold red] - {xml_file.name} ({len(errors)} errors)"
        )

        # Group errors by type
        error_types: dict[str, int] = {}
        for error in errors:
            code = error.code or "UNKNOWN"
            error_types[code] = error_types.get(code, 0) + 1

        if error_types:
            console.print("\nError summary:")
            for code, count in sorted(error_types.items()):
                console.print(f"  {code}: {count}")


if __name__ == "__main__":
    validate_command()
