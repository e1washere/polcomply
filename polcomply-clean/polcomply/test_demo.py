#!/usr/bin/env python3
"""
Demo script for PolComply XSD validator

Licensed under the Business Source License 1.1 (BSL).
See LICENSE file for full terms.
"""

from validators.xsd import XSDValidator
import tempfile
from pathlib import Path


def create_test_schema():
    """Create a simple test XSD schema"""
    schema_content = """<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
           targetNamespace="http://example.com/invoice"
           xmlns:tns="http://example.com/invoice"
           elementFormDefault="qualified">
    
    <xs:element name="Invoice">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="InvoiceNumber" type="xs:string" minOccurs="1" maxOccurs="1"/>
                <xs:element name="IssueDate" type="xs:date" minOccurs="1" maxOccurs="1"/>
                <xs:element name="TotalAmount" type="xs:decimal" minOccurs="1" maxOccurs="1"/>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".xsd", delete=False) as f:
        f.write(schema_content)
        return Path(f.name)


def test_valid_xml():
    """Test with valid XML"""
    valid_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="http://example.com/invoice">
    <InvoiceNumber>FA/2024/001</InvoiceNumber>
    <IssueDate>2024-01-15</IssueDate>
    <TotalAmount>100.00</TotalAmount>
</Invoice>"""
    return valid_xml


def test_invalid_xml():
    """Test with invalid XML"""
    invalid_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="http://example.com/invoice">
    <InvoiceNumber>FA/2024/001</InvoiceNumber>
    <IssueDate>invalid-date</IssueDate>
    <TotalAmount>100.00</TotalAmount>
</Invoice>"""
    return invalid_xml


def main():
    print("🚀 PolComply XSD Validator Demo")
    print("=" * 50)

    # Create test schema
    schema_path = create_test_schema()
    print(f"📄 Created test schema: {schema_path}")

    try:
        # Initialize validator
        validator = XSDValidator(schema_path)
        print("✅ XSD validator initialized successfully")

        # Test valid XML
        print("\n🧪 Testing valid XML...")
        valid_xml = test_valid_xml()
        errors = validator.validate(valid_xml)

        if not errors:
            print("✅ Valid XML: No errors found")
        else:
            print(f"❌ Valid XML: {len(errors)} errors found")
            for error in errors:
                print(f"   - {error}")

        # Test invalid XML
        print("\n🧪 Testing invalid XML...")
        invalid_xml = test_invalid_xml()
        errors = validator.validate(invalid_xml)

        if not errors:
            print("✅ Invalid XML: No errors found (unexpected)")
        else:
            print(f"❌ Invalid XML: {len(errors)} errors found (expected)")
            for error in errors:
                print(f"   - {error}")

        # Test convenience function
        print("\n🧪 Testing convenience function...")
        from validators.xsd import validate_fax

        errors = validate_fax(valid_xml, schema_path)
        print(f"✅ Convenience function: {len(errors)} errors")

        # Test schema info
        print("\n📊 Schema information:")
        info = validator.get_schema_info()
        for key, value in info.items():
            print(f"   {key}: {value}")

        print("\n🎉 All tests completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Cleanup
        schema_path.unlink()
        print(f"🧹 Cleaned up test schema: {schema_path}")


if __name__ == "__main__":
    main()
