"""
XSD validator for FA-3 invoices

Licensed under the Business Source License 1.1 (BSL).
See LICENSE file for full terms.
"""

import logging
from pathlib import Path
from typing import Any

from lxml import etree

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Represents a validation error with location information"""

    def __init__(
        self,
        message: str,
        line: int | None = None,
        column: int | None = None,
        code: str | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column
        self.code = code

    def __str__(self) -> str:
        location = ""
        if self.line is not None:
            location = f" (line {self.line}"
            if self.column is not None:
                location += f", column {self.column}"
            location += ")"

        code_info = f" [{self.code}]" if self.code else ""
        return f"{self.message}{location}{code_info}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "code": self.code,
        }


class XSDValidator:
    """XSD schema validator for XML documents"""

    def __init__(self, schema_path: Path):
        """
        Initialize XSD validator with schema file

        Args:
            schema_path: Path to XSD schema file

        Raises:
            FileNotFoundError: If schema file doesn't exist
            ValidationError: If schema file is invalid
        """
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")

        self.schema_path = schema_path
        self._schema: etree.XMLSchema | None = None
        self._schema_doc: etree._ElementTree | None = None
        self._load_schema()

    def _load_schema(self) -> None:
        """Load and parse XSD schema"""
        try:
            # Parse XSD schema
            self._schema_doc = etree.parse(str(self.schema_path))
            self._schema = etree.XMLSchema(self._schema_doc)
            logger.info(f"XSD schema loaded successfully: {self.schema_path}")
        except etree.XMLSyntaxError as e:
            raise ValidationError(
                f"Invalid XSD schema syntax: {e.msg}",
                line=e.lineno,
                column=e.position[0] if e.position else None,
                code="XSD_SYNTAX_ERROR",
            )
        except Exception as e:
            raise ValidationError(
                f"Failed to load XSD schema: {str(e)}", code="XSD_LOAD_ERROR"
            )

    def validate(self, xml_bytes: bytes) -> list[ValidationError]:
        """
        Validate XML document against XSD schema

        Args:
            xml_bytes: XML document as bytes

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        try:
            # Parse XML document
            xml_doc = etree.fromstring(xml_bytes)
        except etree.XMLSyntaxError as e:
            # XML syntax error - document is malformed
            errors.append(
                ValidationError(
                    f"XML syntax error: {e.msg}",
                    line=e.lineno,
                    column=e.position[0] if e.position else None,
                    code="XML_SYNTAX_ERROR",
                )
            )
            return errors
        except Exception as e:
            errors.append(
                ValidationError(
                    f"Failed to parse XML: {str(e)}", code="XML_PARSE_ERROR"
                )
            )
            return errors

        # Validate against XSD schema
        try:
            if self._schema is not None:
                self._schema.assertValid(xml_doc)
            logger.debug("XML document is valid according to XSD schema")
        except etree.DocumentInvalid as e:
            # Collect all validation errors
            try:
                for error in e.error_log:  # type: ignore
                    errors.append(
                        ValidationError(
                            message=error.message,
                            line=error.line,
                            column=error.column,
                            code=error.type_name,
                        )
                    )
            except Exception:
                # Fallback if error_log iteration fails
                errors.append(
                    ValidationError(
                        message=str(e),
                        code="SCHEMA_VALIDATION_ERROR",
                    )
                )
        except Exception as e:
            errors.append(
                ValidationError(
                    f"Schema validation failed: {str(e)}",
                    code="SCHEMA_VALIDATION_ERROR",
                )
            )

        return errors

    def validate_file(self, xml_path: Path) -> list[ValidationError]:
        """
        Validate XML file against XSD schema

        Args:
            xml_path: Path to XML file

        Returns:
            List of validation errors (empty if valid)
        """
        if not xml_path.exists():
            return [
                ValidationError(
                    f"XML file not found: {xml_path}", code="FILE_NOT_FOUND"
                )
            ]

        try:
            with open(xml_path, "rb") as f:
                xml_bytes = f.read()
            return self.validate(xml_bytes)
        except OSError as e:
            return [
                ValidationError(
                    f"Failed to read XML file: {str(e)}", code="FILE_READ_ERROR"
                )
            ]

    def is_valid(self, xml_bytes: bytes) -> bool:
        """
        Check if XML document is valid (convenience method)

        Args:
            xml_bytes: XML document as bytes

        Returns:
            True if valid, False otherwise
        """
        return len(self.validate(xml_bytes)) == 0

    def get_schema_info(self) -> dict[str, Any]:
        """
        Get information about loaded schema

        Returns:
            Dictionary with schema information
        """
        target_namespace = None
        if self._schema_doc:
            root = self._schema_doc.getroot()
            target_namespace = root.get("targetNamespace")

        return {
            "schema_path": str(self.schema_path),
            "schema_loaded": self._schema is not None,
            "target_namespace": target_namespace,
        }


def validate_fax(xml_bytes: bytes, schema: Path) -> list[ValidationError]:
    """
    Convenience function to validate FA-3 XML against XSD schema

    Args:
        xml_bytes: FA-3 XML document as bytes
        schema: Path to FA-3 XSD schema file

    Returns:
        List of validation errors (empty if valid)
    """
    validator = XSDValidator(schema)
    return validator.validate(xml_bytes)
