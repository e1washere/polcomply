"""
CSV to FA-3 XML mapping module

Licensed under the Business Source License 1.1 (BSL).
See LICENSE file for full terms.
"""

import logging
import re
import xml.etree.ElementTree as ET
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

logger = logging.getLogger(__name__)


class MappingError(Exception):
    """Exception raised for mapping errors"""

    def __init__(self, message: str, field: str | None = None, row: int | None = None):
        super().__init__(message)
        self.message = message
        self.field = field
        self.row = row

    def __str__(self) -> str:
        location = ""
        if self.field:
            location += f" field '{self.field}'"
        if self.row is not None:
            location += f" row {self.row + 1}"
        return f"{self.message}{location}"


class CSVToFAMapper:
    """Maps CSV data to FA-3 XML format"""

    def __init__(self, config_path: Path):
        """
        Initialize mapper with configuration file

        Args:
            config_path: Path to FA-3 mapping configuration YAML file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.namespaces = self.config.get("namespaces", {})
        self.fields = self.config.get("fields", {})
        self.csv_columns = self.config.get("csv_columns", {}).get("default_mapping", {})
        self.validation_rules = self.config.get("validation", {})

        logger.info(f"FA-3 mapper initialized with config: {config_path}")

    def _load_config(self) -> dict[str, Any]:
        """Load mapping configuration from YAML file"""
        try:
            with open(self.config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            raise MappingError(f"Failed to load mapping config: {e}")

    def read_csv(self, csv_path: Path, **kwargs) -> pd.DataFrame:
        """
        Read CSV file with pandas

        Args:
            csv_path: Path to CSV file
            **kwargs: Additional arguments for pandas.read_csv

        Returns:
            DataFrame with CSV data
        """
        try:
            # Try to detect file format
            if csv_path.suffix.lower() in [".xlsx", ".xls"]:
                df = pd.read_excel(csv_path, **kwargs)
            else:
                df = pd.read_csv(csv_path, **kwargs)

            logger.info(f"Loaded CSV with {len(df)} rows and {len(df.columns)} columns")
            return df
        except Exception as e:
            raise MappingError(f"Failed to read CSV file: {e}")

    def map_columns(
        self, df: pd.DataFrame, column_mapping: dict[str, str] | None = None
    ) -> pd.DataFrame:
        """
        Map CSV columns to field names

        Args:
            df: Input DataFrame
            column_mapping: Custom column mapping (overrides default)

        Returns:
            DataFrame with mapped columns
        """
        mapping = column_mapping or self.csv_columns

        # Create reverse mapping (field -> column)
        field_to_column = {v: k for k, v in mapping.items()}

        # Rename columns
        df_mapped = df.copy()
        for field, column in field_to_column.items():
            if column in df_mapped.columns:
                df_mapped = df_mapped.rename(columns={column: field})

        logger.info(f"Mapped {len(mapping)} columns")
        return df_mapped

    def validate_data(self, df: pd.DataFrame) -> list[MappingError]:
        """
        Validate DataFrame data according to mapping rules

        Args:
            df: DataFrame to validate

        Returns:
            List of validation errors
        """
        errors = []

        for field_name, field_config in self.fields.items():
            if field_config.get("required", False):
                if field_name not in df.columns:
                    errors.append(
                        MappingError(
                            f"Required field '{field_name}' not found in CSV",
                            field=field_name,
                        )
                    )
                    continue

                # Check for missing values
                missing_mask = df[field_name].isna()
                if missing_mask.any():
                    missing_rows = df[missing_mask].index.tolist()
                    for row in missing_rows:
                        errors.append(
                            MappingError(
                                f"Required field '{field_name}' is missing",
                                field=field_name,
                                row=row,
                            )
                        )

        # Validate data types
        for field_name, field_config in self.fields.items():
            if field_name not in df.columns:
                continue

            field_type = field_config.get("type")
            if not field_type:
                continue

            for idx, value in df[field_name].items():
                if pd.isna(value):
                    continue

                try:
                    self._validate_field_type(value, field_type, field_config)
                except MappingError as e:
                    e.row = (
                        int(idx)
                        if isinstance(idx, int | str) and str(idx).isdigit()
                        else None
                    )
                    errors.append(e)

        # Validate business rules
        errors.extend(self._validate_business_rules(df))

        logger.info(f"Validation completed: {len(errors)} errors found")
        return errors

    def _validate_field_type(
        self, value: Any, field_type: str, field_config: dict[str, Any]
    ) -> None:
        """Validate individual field value"""
        if field_type == "string":
            if not isinstance(value, str):
                raise MappingError(f"Expected string, got {type(value).__name__}")

            # Check pattern if specified
            pattern = field_config.get("pattern")
            if pattern and not re.match(pattern, str(value)):
                raise MappingError(
                    f"Value '{value}' does not match pattern '{pattern}'"
                )

        elif field_type == "decimal":
            try:
                Decimal(str(value))
            except (InvalidOperation, ValueError):
                raise MappingError(f"Expected decimal number, got '{value}'")

        elif field_type == "date":
            try:
                date_format = field_config.get("format", "%Y-%m-%d")
                if isinstance(value, str):
                    datetime.strptime(value, date_format)
                elif isinstance(value, datetime | date):
                    pass  # Already a date
                else:
                    raise MappingError(f"Expected date, got {type(value).__name__}")
            except ValueError:
                raise MappingError(f"Invalid date format: '{value}'")

        elif field_type == "array":
            if not isinstance(value, list | tuple):
                raise MappingError(f"Expected array, got {type(value).__name__}")

    def _validate_business_rules(self, df: pd.DataFrame) -> list[MappingError]:
        """Validate business rules"""
        errors = []

        # Date validation rules
        date_rules = self.validation_rules.get("date_rules", [])
        for rule in date_rules:
            if "issue_date <= sale_date" in rule:
                if "issue_date" in df.columns and "sale_date" in df.columns:
                    for idx, row in df.iterrows():
                        if pd.notna(row.get("issue_date")) and pd.notna(
                            row.get("sale_date")
                        ):
                            try:
                                issue_date = pd.to_datetime(row["issue_date"])
                                sale_date = pd.to_datetime(row["sale_date"])
                                if issue_date > sale_date:
                                    errors.append(
                                        MappingError(
                                            "Issue date cannot be later than sale date",
                                            row=(
                                                int(idx)
                                                if isinstance(idx, int | str)
                                                and str(idx).isdigit()
                                                else None
                                            ),
                                        )
                                    )
                            except Exception:
                                pass  # Skip if dates are invalid

        # VAT rate validation
        vat_rules = self.validation_rules.get("vat_rules", {})
        allowed_rates = vat_rules.get("allowed_rates", [0, 5, 8, 23])

        if "item_vat_rate" in df.columns:
            for idx, value in df["item_vat_rate"].items():
                if pd.notna(value):
                    try:
                        rate = float(value)
                        if rate not in allowed_rates:
                            errors.append(
                                MappingError(
                                    f"Invalid VAT rate {rate}%. Allowed rates: {allowed_rates}",
                                    field="item_vat_rate",
                                    row=(
                                        int(idx)
                                        if isinstance(idx, int | str)
                                        and str(idx).isdigit()
                                        else None
                                    ),
                                )
                            )
                    except (ValueError, TypeError):
                        errors.append(
                            MappingError(
                                f"Invalid VAT rate format: '{value}'",
                                field="item_vat_rate",
                                row=(
                                    int(idx)
                                    if isinstance(idx, int | str) and str(idx).isdigit()
                                    else None
                                ),
                            )
                        )

        return errors

    def generate_xml(self, df: pd.DataFrame) -> str:
        """
        Generate FA-3 XML from DataFrame

        Args:
            df: DataFrame with mapped data

        Returns:
            XML string
        """
        # Create root element
        root_tag = self.config.get("root_element", "tns:FA")
        root = ET.Element(root_tag)

        # Add namespace declarations
        for prefix, uri in self.namespaces.items():
            root.set(f"xmlns:{prefix}", uri)

        # Process each row (assuming single invoice per CSV for now)
        for idx, row in df.iterrows():
            self._process_invoice_row(
                root,
                row,
                (
                    int(idx)
                    if isinstance(idx, int | str) and str(idx).isdigit()
                    else None
                ),
            )

        # Convert to string
        ET.indent(root, space="  ", level=0)
        xml_str = ET.tostring(root, encoding="unicode", xml_declaration=True)

        logger.info("FA-3 XML generated successfully")
        return xml_str

    def _process_invoice_row(
        self, root: ET.Element, row: pd.Series, row_idx: int | None
    ) -> None:
        """Process single invoice row"""
        # Create invoice structure based on FA-3 schema
        faktura = ET.SubElement(root, "tns:Faktura")

        # Map basic fields
        self._map_field(faktura, row, "invoice_number", "tns:NrFaktury")
        self._map_field(faktura, row, "issue_date", "tns:DataWystawienia")
        self._map_field(faktura, row, "sale_date", "tns:DataSprzedazy")
        self._map_field(faktura, row, "due_date", "tns:TerminPlatnosci")

        # Map seller information
        seller = ET.SubElement(faktura, "tns:Sprzedawca")
        self._map_field(seller, row, "seller_nip", "tns:NIP")
        self._map_field(seller, row, "seller_name", "tns:Nazwa")

        seller_address = ET.SubElement(seller, "tns:Adres")
        self._map_field(seller_address, row, "seller_street", "tns:Ulica")
        self._map_field(seller_address, row, "seller_city", "tns:Miejscowosc")
        self._map_field(seller_address, row, "seller_postal_code", "tns:KodPocztowy")
        self._map_field(seller_address, row, "seller_country", "tns:Kraj", default="PL")

        # Map buyer information
        buyer = ET.SubElement(faktura, "tns:Nabywca")
        self._map_field(buyer, row, "buyer_nip", "tns:NIP")
        self._map_field(buyer, row, "buyer_name", "tns:Nazwa")

        buyer_address = ET.SubElement(buyer, "tns:Adres")
        self._map_field(buyer_address, row, "buyer_street", "tns:Ulica")
        self._map_field(buyer_address, row, "buyer_city", "tns:Miejscowosc")
        self._map_field(buyer_address, row, "buyer_postal_code", "tns:KodPocztowy")
        self._map_field(buyer_address, row, "buyer_country", "tns:Kraj", default="PL")

        # Map invoice items
        self._map_invoice_items(faktura, row)

        # Map totals
        self._map_totals(faktura, row)

        # Map payment information
        self._map_payment_info(faktura, row)

        # Map invoice type
        self._map_field(
            faktura, row, "invoice_type", "tns:RodzajFaktury", default="VAT"
        )

        # Map currency
        self._map_field(faktura, row, "currency", "tns:Waluta", default="PLN")

    def _map_field(
        self,
        parent: ET.Element,
        row: pd.Series,
        field_name: str,
        xml_tag: str,
        default: str | None = None,
    ) -> None:
        """Map a single field to XML element"""
        value = row.get(field_name)

        if pd.isna(value) or value is None:
            if default is not None:
                value = default
            else:
                return  # Skip if no value and no default

        # Format value based on field type
        field_config = self.fields.get(field_name, {})
        field_type = field_config.get("type", "string")

        if field_type == "date" and isinstance(value, str):
            # Keep date as string for XML
            pass
        elif field_type == "decimal":
            try:
                value = str(Decimal(str(value)))
            except (InvalidOperation, ValueError):
                logger.warning(f"Invalid decimal value for {field_name}: {value}")
                return

        # Create XML element
        element = ET.SubElement(parent, xml_tag)
        element.text = str(value)

    def _map_invoice_items(self, faktura: ET.Element, row: pd.Series) -> None:
        """Map invoice items"""
        pozycje = ET.SubElement(faktura, "tns:PozycjeFaktury")

        # For now, assume single item per row
        # In a real implementation, you might have multiple items in a single row
        pozycja = ET.SubElement(pozycje, "tns:PozycjaFaktury")

        self._map_field(pozycja, row, "item_name", "tns:Nazwa")
        self._map_field(pozycja, row, "item_quantity", "tns:Ilosc")
        self._map_field(pozycja, row, "item_unit", "tns:JednostkaMiary", default="szt")
        self._map_field(pozycja, row, "item_net_price", "tns:CenaJednostkowa")
        self._map_field(pozycja, row, "item_vat_rate", "tns:StawkaPodatku")
        self._map_field(pozycja, row, "item_net_amount", "tns:WartoscNetto")
        self._map_field(pozycja, row, "item_vat_amount", "tns:WartoscVAT")
        self._map_field(pozycja, row, "item_gross_amount", "tns:WartoscBrutto")

    def _map_totals(self, faktura: ET.Element, row: pd.Series) -> None:
        """Map invoice totals"""
        podsumowanie = ET.SubElement(faktura, "tns:Podsumowanie")

        self._map_field(podsumowanie, row, "total_net_amount", "tns:WartoscNetto")
        self._map_field(podsumowanie, row, "total_vat_amount", "tns:WartoscVAT")
        self._map_field(podsumowanie, row, "total_gross_amount", "tns:WartoscBrutto")

    def _map_payment_info(self, faktura: ET.Element, row: pd.Series) -> None:
        """Map payment information"""
        platnosc = ET.SubElement(faktura, "tns:Platnosc")

        self._map_field(
            platnosc, row, "payment_method", "tns:FormaPlatnosci", default="P"
        )
        self._map_field(platnosc, row, "payment_due_date", "tns:TerminPlatnosci")

    def process_csv(
        self,
        csv_path: Path,
        output_path: Path | None = None,
        column_mapping: dict[str, str] | None = None,
    ) -> str:
        """
        Process CSV file and generate FA-3 XML

        Args:
            csv_path: Path to input CSV file
            output_path: Path to output XML file (optional)
            column_mapping: Custom column mapping (optional)

        Returns:
            Generated XML string
        """
        # Read CSV
        df = self.read_csv(csv_path)

        # Map columns
        df_mapped = self.map_columns(df, column_mapping)

        # Validate data
        errors = self.validate_data(df_mapped)
        if errors:
            error_summary = "\n".join(
                str(e) for e in errors[:10]
            )  # Show first 10 errors
            if len(errors) > 10:
                error_summary += f"\n... and {len(errors) - 10} more errors"
            raise MappingError(
                f"Validation failed with {len(errors)} errors:\n{error_summary}"
            )

        # Generate XML
        xml_content = self.generate_xml(df_mapped)

        # Save to file if output path specified
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(xml_content)
            logger.info(f"XML saved to: {output_path}")

        return xml_content

    def get_missing_fields_report(
        self, df: pd.DataFrame
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Generate report of missing required fields

        Args:
            df: DataFrame to analyze

        Returns:
            Dictionary with missing fields and their descriptions
        """
        report: dict[str, list[dict[str, Any]]] = {
            "missing_required": [],
            "missing_optional": [],
            "available_fields": [],
        }

        for field_name, field_config in self.fields.items():
            if field_name in df.columns:
                report["available_fields"].append(
                    {
                        "field": field_name,
                        "description": field_config.get("description", ""),
                        "type": field_config.get("type", "string"),
                        "required": field_config.get("required", False),
                    }
                )
            else:
                field_info = {
                    "field": field_name,
                    "description": field_config.get("description", ""),
                    "type": field_config.get("type", "string"),
                    "required": field_config.get("required", False),
                }

                if field_config.get("required", False):
                    report["missing_required"].append(field_info)
                else:
                    report["missing_optional"].append(field_info)

        return report
