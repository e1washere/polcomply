"""
Tests for XSD validator

Licensed under the Business Source License 1.1 (BSL).
See LICENSE file for full terms.
"""

from pathlib import Path

import pytest

from polcomply.validators.xsd import ValidationError, XSDValidator, validate_fax

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "golden_files"


class TestXSDValidator:
    """Test XSD validator functionality"""

    @pytest.fixture
    def sample_schema(self, tmp_path):
        """Create a sample XSD schema for testing"""
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
                <xs:element name="Seller" type="tns:PartyType" minOccurs="1" maxOccurs="1"/>
                <xs:element name="Buyer" type="tns:PartyType" minOccurs="1" maxOccurs="1"/>
                <xs:element name="Items" type="tns:ItemsType" minOccurs="1" maxOccurs="1"/>
                <xs:element name="TotalAmount" type="xs:decimal" minOccurs="1" maxOccurs="1"/>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
    
    <xs:complexType name="PartyType">
        <xs:sequence>
            <xs:element name="Name" type="xs:string" minOccurs="1" maxOccurs="1"/>
            <xs:element name="NIP" type="xs:string" minOccurs="1" maxOccurs="1"/>
            <xs:element name="Address" type="tns:AddressType" minOccurs="1" maxOccurs="1"/>
        </xs:sequence>
    </xs:complexType>
    
    <xs:complexType name="AddressType">
        <xs:sequence>
            <xs:element name="Street" type="xs:string" minOccurs="1" maxOccurs="1"/>
            <xs:element name="City" type="xs:string" minOccurs="1" maxOccurs="1"/>
            <xs:element name="PostalCode" type="xs:string" minOccurs="1" maxOccurs="1"/>
        </xs:sequence>
    </xs:complexType>
    
    <xs:complexType name="ItemsType">
        <xs:sequence>
            <xs:element name="Item" type="tns:ItemType" minOccurs="1" maxOccurs="unbounded"/>
        </xs:sequence>
    </xs:complexType>
    
    <xs:complexType name="ItemType">
        <xs:sequence>
            <xs:element name="Name" type="xs:string" minOccurs="1" maxOccurs="1"/>
            <xs:element name="Quantity" type="xs:decimal" minOccurs="1" maxOccurs="1"/>
            <xs:element name="UnitPrice" type="xs:decimal" minOccurs="1" maxOccurs="1"/>
            <xs:element name="TotalPrice" type="xs:decimal" minOccurs="1" maxOccurs="1"/>
        </xs:sequence>
    </xs:complexType>
</xs:schema>"""

        schema_path = tmp_path / "invoice.xsd"
        schema_path.write_text(schema_content, encoding="utf-8")
        return schema_path

    @pytest.fixture
    def valid_xml(self):
        """Valid XML invoice"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="http://example.com/invoice">
    <InvoiceNumber>FA/2024/001</InvoiceNumber>
    <IssueDate>2024-01-15</IssueDate>
    <Seller>
        <Name>Test Company Sp. z o.o.</Name>
        <NIP>1234567890</NIP>
        <Address>
            <Street>ul. Testowa 1</Street>
            <City>Warszawa</City>
            <PostalCode>00-001</PostalCode>
        </Address>
    </Seller>
    <Buyer>
        <Name>Client Company</Name>
        <NIP>0987654321</NIP>
        <Address>
            <Street>ul. Klienta 2</Street>
            <City>Kraków</City>
            <PostalCode>30-001</PostalCode>
        </Address>
    </Buyer>
    <Items>
        <Item>
            <Name>Test Product</Name>
            <Quantity>2</Quantity>
            <UnitPrice>100.00</UnitPrice>
            <TotalPrice>200.00</TotalPrice>
        </Item>
    </Items>
    <TotalAmount>200.00</TotalAmount>
</Invoice>""".encode()

    @pytest.fixture
    def invalid_xml_missing_element(self):
        """Invalid XML - missing required element"""
        return b"""<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="http://example.com/invoice">
    <InvoiceNumber>FA/2024/001</InvoiceNumber>
    <IssueDate>2024-01-15</IssueDate>
    <Seller>
        <Name>Test Company Sp. z o.o.</Name>
        <NIP>1234567890</NIP>
        <Address>
            <Street>ul. Testowa 1</Street>
            <City>Warszawa</City>
            <PostalCode>00-001</PostalCode>
        </Address>
    </Seller>
    <!-- Missing Buyer element -->
    <Items>
        <Item>
            <Name>Test Product</Name>
            <Quantity>2</Quantity>
            <UnitPrice>100.00</UnitPrice>
            <TotalPrice>200.00</TotalPrice>
        </Item>
    </Items>
    <TotalAmount>200.00</TotalAmount>
</Invoice>"""

    @pytest.fixture
    def invalid_xml_wrong_type(self):
        """Invalid XML - wrong data type"""
        return """<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="http://example.com/invoice">
    <InvoiceNumber>FA/2024/001</InvoiceNumber>
    <IssueDate>invalid-date</IssueDate>
    <Seller>
        <Name>Test Company Sp. z o.o.</Name>
        <NIP>1234567890</NIP>
        <Address>
            <Street>ul. Testowa 1</Street>
            <City>Warszawa</City>
            <PostalCode>00-001</PostalCode>
        </Address>
    </Seller>
    <Buyer>
        <Name>Client Company</Name>
        <NIP>0987654321</NIP>
        <Address>
            <Street>ul. Klienta 2</Street>
            <City>Kraków</City>
            <PostalCode>30-001</PostalCode>
        </Address>
    </Buyer>
    <Items>
        <Item>
            <Name>Test Product</Name>
            <Quantity>2</Quantity>
            <UnitPrice>100.00</UnitPrice>
            <TotalPrice>200.00</TotalPrice>
        </Item>
    </Items>
    <TotalAmount>200.00</TotalAmount>
</Invoice>""".encode()

    def test_validator_initialization(self, sample_schema):
        """Test validator initialization with valid schema"""
        validator = XSDValidator(sample_schema)
        assert validator.schema_path == sample_schema
        assert validator._schema is not None

    def test_validator_initialization_invalid_schema(self, tmp_path):
        """Test validator initialization with invalid schema"""
        invalid_schema = tmp_path / "invalid.xsd"
        invalid_schema.write_text("invalid xml content", encoding="utf-8")

        with pytest.raises(ValidationError) as exc_info:
            XSDValidator(invalid_schema)

        assert "Invalid XSD schema syntax" in str(exc_info.value)
        assert exc_info.value.code == "XSD_SYNTAX_ERROR"

    def test_validator_initialization_missing_schema(self, tmp_path):
        """Test validator initialization with missing schema file"""
        missing_schema = tmp_path / "missing.xsd"

        with pytest.raises(FileNotFoundError):
            XSDValidator(missing_schema)

    def test_validate_valid_xml(self, sample_schema, valid_xml):
        """Test validation of valid XML"""
        validator = XSDValidator(sample_schema)
        errors = validator.validate(valid_xml)
        assert len(errors) == 0

    def test_validate_invalid_xml_missing_element(
        self, sample_schema, invalid_xml_missing_element
    ):
        """Test validation of invalid XML with missing element"""
        validator = XSDValidator(sample_schema)
        errors = validator.validate(invalid_xml_missing_element)

        assert len(errors) > 0
        assert any("Buyer" in error.message for error in errors)

    def test_validate_invalid_xml_wrong_type(
        self, sample_schema, invalid_xml_wrong_type
    ):
        """Test validation of invalid XML with wrong data type"""
        validator = XSDValidator(sample_schema)
        errors = validator.validate(invalid_xml_wrong_type)

        assert len(errors) > 0
        assert any("date" in error.message.lower() for error in errors)

    def test_validate_malformed_xml(self, sample_schema):
        """Test validation of malformed XML"""
        malformed_xml = b"<Invoice><InvoiceNumber>FA/2024/001</InvoiceNumber></Invoice"  # Missing closing tag

        validator = XSDValidator(sample_schema)
        errors = validator.validate(malformed_xml)

        assert len(errors) > 0
        assert any(error.code == "XML_SYNTAX_ERROR" for error in errors)

    def test_validate_file_valid(self, sample_schema, valid_xml, tmp_path):
        """Test validation of valid XML file"""
        xml_file = tmp_path / "valid.xml"
        xml_file.write_bytes(valid_xml)

        validator = XSDValidator(sample_schema)
        errors = validator.validate_file(xml_file)
        assert len(errors) == 0

    def test_validate_file_invalid(
        self, sample_schema, invalid_xml_missing_element, tmp_path
    ):
        """Test validation of invalid XML file"""
        xml_file = tmp_path / "invalid.xml"
        xml_file.write_bytes(invalid_xml_missing_element)

        validator = XSDValidator(sample_schema)
        errors = validator.validate_file(xml_file)
        assert len(errors) > 0

    def test_validate_file_missing(self, sample_schema, tmp_path):
        """Test validation of missing XML file"""
        missing_file = tmp_path / "missing.xml"

        validator = XSDValidator(sample_schema)
        errors = validator.validate_file(missing_file)

        assert len(errors) == 1
        assert errors[0].code == "FILE_NOT_FOUND"

    def test_is_valid_valid_xml(self, sample_schema, valid_xml):
        """Test is_valid method with valid XML"""
        validator = XSDValidator(sample_schema)
        assert validator.is_valid(valid_xml) is True

    def test_is_valid_invalid_xml(self, sample_schema, invalid_xml_missing_element):
        """Test is_valid method with invalid XML"""
        validator = XSDValidator(sample_schema)
        assert validator.is_valid(invalid_xml_missing_element) is False

    def test_get_schema_info(self, sample_schema):
        """Test getting schema information"""
        validator = XSDValidator(sample_schema)
        info = validator.get_schema_info()

        assert info["schema_path"] == str(sample_schema)
        assert info["schema_loaded"] is True
        assert info["target_namespace"] == "http://example.com/invoice"

    def test_validation_error_creation(self):
        """Test ValidationError creation and string representation"""
        error = ValidationError("Test error", line=10, column=5, code="TEST_ERROR")

        assert error.message == "Test error"
        assert error.line == 10
        assert error.column == 5
        assert error.code == "TEST_ERROR"
        assert "Test error (line 10, column 5) [TEST_ERROR]" == str(error)

    def test_validation_error_to_dict(self):
        """Test ValidationError to_dict method"""
        error = ValidationError("Test error", line=10, column=5, code="TEST_ERROR")
        error_dict = error.to_dict()

        expected = {
            "message": "Test error",
            "line": 10,
            "column": 5,
            "code": "TEST_ERROR",
        }
        assert error_dict == expected


class TestValidateFaxFunction:
    """Test validate_fax convenience function"""

    def test_validate_fax_valid(self, sample_schema, valid_xml):
        """Test validate_fax function with valid XML"""
        errors = validate_fax(valid_xml, sample_schema)
        assert len(errors) == 0

    def test_validate_fax_invalid(self, sample_schema, invalid_xml_missing_element):
        """Test validate_fax function with invalid XML"""
        errors = validate_fax(invalid_xml_missing_element, sample_schema)
        assert len(errors) > 0


class TestGoldenFiles:
    """Test with golden files (if they exist)"""

    def test_golden_files_exist(self):
        """Test that golden files directory exists"""
        assert (
            TEST_DATA_DIR.exists()
        ), f"Golden files directory not found: {TEST_DATA_DIR}"

    @pytest.mark.parametrize(
        "xml_file",
        [
            "valid_invoice_1.xml",
            "valid_invoice_2.xml",
            "valid_invoice_3.xml",
            "valid_invoice_4.xml",
            "valid_invoice_5.xml",
        ],
    )
    def test_valid_golden_files(self, xml_file, sample_schema):
        """Test valid golden files"""
        xml_path = TEST_DATA_DIR / xml_file
        if not xml_path.exists():
            pytest.skip(f"Golden file not found: {xml_file}")

        validator = XSDValidator(sample_schema)
        errors = validator.validate_file(xml_path)

        assert len(errors) == 0, f"Valid golden file {xml_file} has errors: {errors}"

    @pytest.mark.parametrize(
        "xml_file",
        [
            "invalid_invoice_1.xml",
            "invalid_invoice_2.xml",
            "invalid_invoice_3.xml",
            "invalid_invoice_4.xml",
            "invalid_invoice_5.xml",
        ],
    )
    def test_invalid_golden_files(self, xml_file, sample_schema):
        """Test invalid golden files"""
        xml_path = TEST_DATA_DIR / xml_file
        if not xml_path.exists():
            pytest.skip(f"Golden file not found: {xml_file}")

        validator = XSDValidator(sample_schema)
        errors = validator.validate_file(xml_path)

        assert len(errors) > 0, f"Invalid golden file {xml_file} should have errors"
