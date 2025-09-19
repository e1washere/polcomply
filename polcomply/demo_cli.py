#!/usr/bin/env python3
"""
Demo CLI for PolComply FA-3 validation
"""
import sys
import argparse
from pathlib import Path
from typing import List

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from validators.xsd import XSDValidator, ValidationError
from validators.paths import resolve_fa3_schema
from reporting.html_report import generate_html_report

def format_table_output(errors: List[ValidationError], filename: str) -> str:
    """Format validation errors as a table"""
    if not errors:
        return f"✅ {filename} - VALID (0 errors)"
    
    output = f"❌ {filename} - INVALID ({len(errors)} errors)\n"
    output += "─" * 80 + "\n"
    output += f"{'Line':<8} {'Column':<8} {'Code':<20} {'Message':<40}\n"
    output += "─" * 80 + "\n"
    
    for error in errors:
        line = str(error.line) if error.line else "-"
        column = str(error.column) if error.column else "-"
        code = error.code[:18] + "..." if error.code and len(error.code) > 18 else (error.code or "-")
        message = error.message[:38] + "..." if len(error.message) > 38 else error.message
        
        output += f"{line:<8} {column:<8} {code:<20} {message:<40}\n"
    
    return output

def main():
    parser = argparse.ArgumentParser(description="PolComply FA-3 XML Validator")
    parser.add_argument("xml_file", help="Path to XML file to validate")
    parser.add_argument("--schema", help="Path to XSD schema file (auto-resolve if not provided)")
    parser.add_argument("--report", help="Path to save HTML report")
    parser.add_argument("--format", choices=["table", "json", "summary"], default="table", help="Output format")
    
    args = parser.parse_args()
    
    # Resolve schema
    if args.schema:
        schema_path = Path(args.schema)
    else:
        schema_path = resolve_fa3_schema()
        
    if not schema_path or not schema_path.exists():
        print("❌ FA-3 schema not found. Please provide --schema or place FA-3.xsd in schemas/")
        return 1
    
    # Validate XML
    xml_path = Path(args.xml_file)
    if not xml_path.exists():
        print(f"❌ XML file not found: {args.xml_file}")
        return 1
    
    try:
        validator = XSDValidator(schema_path)
        errors = validator.validate_file(xml_path)
        
        # Generate HTML report if requested
        if args.report:
            generate_html_report(errors, xml_path.name, Path(args.report))
            print(f"📄 HTML report saved to: {args.report}")
        
        # Output results
        if args.format == "table":
            print(format_table_output(errors, xml_path.name))
        elif args.format == "json":
            import json
            result = {
                "file": str(xml_path),
                "is_valid": len(errors) == 0,
                "errors": [
                    {
                        "line": error.line,
                        "column": error.column,
                        "code": error.code,
                        "message": error.message
                    }
                    for error in errors
                ]
            }
            print(json.dumps(result, indent=2))
        elif args.format == "summary":
            if errors:
                print(f"❌ INVALID - {xml_path.name} ({len(errors)} errors)")
                for error in errors:
                    print(f"  • Line {error.line}: {error.message}")
            else:
                print(f"✅ VALID - {xml_path.name}")
        
        return 1 if errors else 0
        
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
