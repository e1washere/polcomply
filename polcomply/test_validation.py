#!/usr/bin/env python3
"""
Test script for FA-3 validation
"""
from pathlib import Path

from polcomply.validators.paths import resolve_fa3_schema
from polcomply.validators.xsd import XSDValidator


def test_validation():
    """Test FA-3 validation with golden files"""

    # Find schema
    schema_path = resolve_fa3_schema()
    if schema_path is None:
        print("❌ FA-3 schema not found")
        return False

    print(f"✅ Using schema: {schema_path}")

    # Test files
    test_files = [
        ("tests/golden/fa3/valid_fv_b2b.xml", True),
        ("tests/golden/fa3/invalid_nip.xml", False),
    ]

    validator = XSDValidator(schema_path)

    for xml_file, should_be_valid in test_files:
        xml_path = Path(xml_file)
        if not xml_path.exists():
            print(f"❌ Test file not found: {xml_file}")
            continue

        print(f"\n📄 Testing: {xml_file}")

        try:
            errors = validator.validate_file(xml_path)
            is_valid = len(errors) == 0

            if is_valid == should_be_valid:
                status = "✅ PASS"
            else:
                status = "❌ FAIL"

            print(f"{status} - Valid: {is_valid}, Errors: {len(errors)}")

            if errors:
                for error in errors[:3]:  # Show first 3 errors
                    print(f"  • Line {error.line}: {error.message}")
                if len(errors) > 3:
                    print(f"  • ... and {len(errors) - 3} more errors")

        except Exception as e:
            print(f"❌ ERROR: {e}")

    return True


if __name__ == "__main__":
    test_validation()
