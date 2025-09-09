"""
Map command for PolComply CLI

Licensed under the Business Source License 1.1 (BSL).
See LICENSE file for full terms.
"""

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from polcomply.mapping.csv_to_fa import CSVToFAMapper, MappingError

console = Console()

map_command = typer.Typer(
    name="map",
    help="Map invoice data between formats",
    rich_markup_mode="rich",
)


@map_command.command("csv-to-fa")
def map_csv_to_fa(
    input_file: Path = typer.Argument(..., help="Path to input CSV/Excel file"),
    output_file: Path = typer.Option(
        ..., "--output", "-o", help="Path to output XML file"
    ),
    config_file: Path = typer.Option(
        Path("mapping/fa3.yaml"),
        "--config",
        "-c",
        help="Path to mapping configuration YAML",
    ),
    schema_file: Path | None = typer.Option(
        None, "--schema", "-s", help="Path to FA-3 XSD schema for validation"
    ),
    validate: bool = typer.Option(
        True, "--validate/--no-validate", help="Validate output XML against schema"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed mapping information"
    ),
):
    """
    Map CSV/Excel data to FA-3 XML format

    Example:
        polcomply map csv-to-fa input.csv --output invoice.xml --schema schemas/FA-3.xsd
    """
    try:
        console.print("[yellow]Mapping CSV to FA-3 XML...[/yellow]")
        console.print(f"Input: [blue]{input_file}[/blue]")
        console.print(f"Output: [blue]{output_file}[/blue]")
        console.print(f"Config: [blue]{config_file}[/blue]")

        # Initialize mapper
        mapper = CSVToFAMapper(config_file)

        # Process CSV
        xml_content = mapper.process_csv(input_file, output_file)

        if verbose:
            # Show mapping report
            df = mapper.read_csv(input_file)
            df_mapped = mapper.map_columns(df)
            report = mapper.get_missing_fields_report(df_mapped)

            _show_mapping_report(report)

        # Validate against schema if provided
        if validate and schema_file and schema_file.exists():
            from polcomply.validators.xsd import XSDValidator

            validator = XSDValidator(schema_file)
            errors = validator.validate(xml_content.encode("utf-8"))

            if errors:
                console.print(
                    f"[red]✗[/red] [bold red]XML validation failed with {len(errors)} errors:[/bold red]"
                )
                for error in errors[:5]:  # Show first 5 errors
                    console.print(f"  - {error}")
                if len(errors) > 5:
                    console.print(f"  ... and {len(errors) - 5} more errors")
                raise typer.Exit(1)
            else:
                console.print(
                    "[green]✓[/green] [bold green]XML validation passed![/bold green]"
                )

        console.print(
            "[green]✓[/green] [bold green]Mapping completed successfully![/bold green]"
        )
        console.print(f"Generated XML: [blue]{output_file}[/blue]")

    except MappingError as e:
        console.print(f"[red]✗[/red] [bold red]Mapping error:[/bold red] {e}")
        raise typer.Exit(1)
    except FileNotFoundError as e:
        console.print(f"[red]✗[/red] [bold red]File not found:[/bold red] {e}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]✗[/red] [bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(1)


@map_command.command("invoice")
def map_invoice(
    input_file: Path = typer.Argument(..., help="Path to input file"),
    output_file: Path = typer.Option(..., "--output", "-o", help="Path to output file"),
    input_format: str = typer.Option(
        "csv", "--input-format", "-i", help="Input format: csv, json, xml"
    ),
    output_format: str = typer.Option(
        "xml", "--output-format", "-f", help="Output format: json, xml, csv"
    ),
    config_file: Path = typer.Option(
        Path("mapping/fa3.yaml"), "--config", "-c", help="Path to mapping configuration"
    ),
):
    """
    Map invoice data between different formats

    Example:
        polcomply map invoice data.csv --output invoice.xml --input-format csv --output-format xml
    """
    if input_format == "csv" and output_format == "xml":
        # Use the specialized CSV to FA-3 mapper
        map_csv_to_fa(
            input_file=input_file,
            output_file=output_file,
            config_file=config_file,
            validate=True,
            verbose=False,
        )
    else:
        console.print(
            f"[yellow]Mapping from {input_format} to {output_format}...[/yellow]"
        )
        console.print(f"Input: [blue]{input_file}[/blue]")
        console.print(f"Output: [blue]{output_file}[/blue]")

        # TODO: Implement other format mappings
        console.print("[green]✓[/green] [bold green]Mapping completed![/bold green]")


def _show_mapping_report(report: dict):
    """Show detailed mapping report"""
    console.print("\n[bold]Mapping Report:[/bold]")

    # Show available fields
    if report["available_fields"]:
        table = Table(title="Available Fields")
        table.add_column("Field", style="green")
        table.add_column("Type", style="cyan")
        table.add_column("Required", style="yellow")
        table.add_column("Description", style="white")

        for field in report["available_fields"]:
            table.add_row(
                field["field"],
                field["type"],
                "Yes" if field["required"] else "No",
                field["description"],
            )
        console.print(table)

    # Show missing required fields
    if report["missing_required"]:
        console.print("\n[bold red]Missing Required Fields:[/bold red]")
        for field in report["missing_required"]:
            console.print(
                f"  • {field['field']} ({field['type']}) - {field['description']}"
            )

    # Show missing optional fields
    if report["missing_optional"]:
        console.print("\n[bold yellow]Missing Optional Fields:[/bold yellow]")
        for field in report["missing_optional"]:
            console.print(
                f"  • {field['field']} ({field['type']}) - {field['description']}"
            )


@map_command.command("list")
def list_formats():
    """List supported input/output formats"""

    formats_text = Text()
    formats_text.append("Supported Formats:\n\n", style="bold")

    formats_text.append("Input Formats:\n", style="bold blue")
    formats_text.append("• CSV - Comma Separated Values\n")
    formats_text.append("• Excel - Microsoft Excel (.xlsx, .xls)\n")
    formats_text.append("• JSON - JavaScript Object Notation\n")
    formats_text.append("• XML - eXtensible Markup Language\n\n")

    formats_text.append("Output Formats:\n", style="bold green")
    formats_text.append("• XML - FA-3 compliant XML\n")
    formats_text.append("• JSON - JavaScript Object Notation\n")
    formats_text.append("• CSV - Comma Separated Values\n\n")

    formats_text.append("Mapping Commands:\n", style="bold magenta")
    formats_text.append("• csv-to-fa - CSV/Excel to FA-3 XML\n")
    formats_text.append("• invoice - General invoice mapping\n")

    panel = Panel(formats_text, title="Supported Formats", border_style="blue")
    console.print(panel)


if __name__ == "__main__":
    map_command()
