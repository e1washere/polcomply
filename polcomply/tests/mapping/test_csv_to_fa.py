"""
Tests for CSV to FA-3 mapping

Licensed under the Business Source License 1.1 (BSL).
See LICENSE file for full terms.
"""

from pathlib import Path

import pandas as pd
import pytest

from polcomply.mapping.csv_to_fa import CSVToFAMapper, MappingError

# Test data directory
TEST_DATA_DIR = Path(__file__).parent.parent / "examples"


class TestCSVToFAMapper:
    """Test CSV to FA-3 mapping functionality"""

    @pytest.fixture
    def sample_config(self, tmp_path):
        """Create a sample mapping configuration"""
        config_content = """# Sample FA-3 Mapping Configuration
namespaces:
  tns: "http://example.com/invoice"

root_element: "tns:FA"

fields:
  invoice_number:
    xpath: "tns:NrFaktury"
    type: "string"
    required: true
    description: "Numer faktury"

  issue_date:
    xpath: "tns:DataWystawienia"
    type: "date"
    required: true
    format: "%Y-%m-%d"
    description: "Data wystawienia faktury"

  seller_nip:
    xpath: "tns:Sprzedawca/tns:NIP"
    type: "string"
    required: true
    pattern: "^[0-9]{10}$"
    description: "NIP sprzedawcy"

  seller_name:
    xpath: "tns:Sprzedawca/tns:Nazwa"
    type: "string"
    required: true
    description: "Nazwa sprzedawcy"

  item_name:
    xpath: "tns:PozycjaFaktury/tns:Nazwa"
    type: "string"
    required: true
    description: "Nazwa pozycji"

  item_quantity:
    xpath: "tns:PozycjaFaktury/tns:Ilosc"
    type: "decimal"
    required: true
    description: "Ilość"

  item_net_price:
    xpath: "tns:PozycjaFaktury/tns:CenaJednostkowa"
    type: "decimal"
    required: true
    description: "Cena jednostkowa netto"

  total_net_amount:
    xpath: "tns:Podsumowanie/tns:WartoscNetto"
    type: "decimal"
    required: true
    description: "Suma wartości netto"

csv_columns:
  default_mapping:
    "Numer faktury": "invoice_number"
    "Data wystawienia": "issue_date"
    "NIP sprzedawcy": "seller_nip"
    "Nazwa sprzedawcy": "seller_name"
    "Nazwa pozycji": "item_name"
    "Ilość": "item_quantity"
    "Cena netto": "item_net_price"
    "Suma netto": "total_net_amount"

validation:
  date_rules:
    - "issue_date <= sale_date"
  vat_rules:
    allowed_rates: [0, 5, 8, 23]
"""

        config_path = tmp_path / "test_config.yaml"
        config_path.write_text(config_content, encoding="utf-8")
        return config_path

    @pytest.fixture
    def sample_csv(self, tmp_path):
        """Create a sample CSV file"""
        csv_content = """Numer faktury,Data wystawienia,NIP sprzedawcy,Nazwa sprzedawcy,Nazwa pozycji,Ilość,Cena netto,Suma netto
FA/2024/001,2024-01-15,1234567890,Test Company,Test Product,2,100.00,200.00"""

        csv_path = tmp_path / "test.csv"
        csv_path.write_text(csv_content, encoding="utf-8")
        return csv_path

    def test_mapper_initialization(self, sample_config):
        """Test mapper initialization with valid config"""
        mapper = CSVToFAMapper(sample_config)
        assert mapper.config_path == sample_config
        assert mapper.fields is not None
        assert len(mapper.fields) > 0

    def test_mapper_initialization_invalid_config(self, tmp_path):
        """Test mapper initialization with invalid config"""
        invalid_config = tmp_path / "invalid.yaml"
        invalid_config.write_text("invalid yaml content", encoding="utf-8")

        with pytest.raises(MappingError) as exc_info:
            CSVToFAMapper(invalid_config)

        assert "Failed to load mapping config" in str(exc_info.value)

    def test_read_csv(self, sample_config, sample_csv):
        """Test CSV reading functionality"""
        mapper = CSVToFAMapper(sample_config)
        df = mapper.read_csv(sample_csv)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert "Numer faktury" in df.columns
        assert df.iloc[0]["Numer faktury"] == "FA/2024/001"

    def test_map_columns(self, sample_config, sample_csv):
        """Test column mapping functionality"""
        mapper = CSVToFAMapper(sample_config)
        df = mapper.read_csv(sample_csv)
        df_mapped = mapper.map_columns(df)

        assert "invoice_number" in df_mapped.columns
        assert "issue_date" in df_mapped.columns
        assert df_mapped.iloc[0]["invoice_number"] == "FA/2024/001"

    def test_validate_data_valid(self, sample_config, sample_csv):
        """Test data validation with valid data"""
        mapper = CSVToFAMapper(sample_config)
        df = mapper.read_csv(sample_csv)
        df_mapped = mapper.map_columns(df)
        errors = mapper.validate_data(df_mapped)

        assert len(errors) == 0

    def test_validate_data_missing_required(self, sample_config, tmp_path):
        """Test data validation with missing required fields"""
        # Create CSV with missing required field
        csv_content = """Numer faktury,Data wystawienia,NIP sprzedawcy,Nazwa sprzedawcy
FA/2024/001,2024-01-15,1234567890,Test Company"""

        csv_path = tmp_path / "incomplete.csv"
        csv_path.write_text(csv_content, encoding="utf-8")

        mapper = CSVToFAMapper(sample_config)
        df = mapper.read_csv(csv_path)
        df_mapped = mapper.map_columns(df)
        errors = mapper.validate_data(df_mapped)

        assert len(errors) > 0
        assert any("Required field" in str(error) for error in errors)

    def test_validate_data_invalid_types(self, sample_config, tmp_path):
        """Test data validation with invalid data types"""
        # Create CSV with invalid data types
        csv_content = """Numer faktury,Data wystawienia,NIP sprzedawcy,Nazwa sprzedawcy,Nazwa pozycji,Ilość,Cena netto,Suma netto
FA/2024/001,invalid-date,1234567890,Test Company,Test Product,not-a-number,100.00,200.00"""

        csv_path = tmp_path / "invalid_types.csv"
        csv_path.write_text(csv_content, encoding="utf-8")

        mapper = CSVToFAMapper(sample_config)
        df = mapper.read_csv(csv_path)
        df_mapped = mapper.map_columns(df)
        errors = mapper.validate_data(df_mapped)

        assert len(errors) > 0
        assert any("Invalid date format" in str(error) for error in errors)
        assert any("Expected decimal number" in str(error) for error in errors)

    def test_generate_xml(self, sample_config, sample_csv):
        """Test XML generation"""
        mapper = CSVToFAMapper(sample_config)
        df = mapper.read_csv(sample_csv)
        df_mapped = mapper.map_columns(df)
        xml_content = mapper.generate_xml(df_mapped)

        assert isinstance(xml_content, str)
        assert "<?xml version=" in xml_content
        assert "<tns:FA" in xml_content
        assert "FA/2024/001" in xml_content

    def test_process_csv_complete(self, sample_config, sample_csv, tmp_path):
        """Test complete CSV processing"""
        output_path = tmp_path / "output.xml"

        mapper = CSVToFAMapper(sample_config)
        xml_content = mapper.process_csv(sample_csv, output_path)

        assert isinstance(xml_content, str)
        assert output_path.exists()

        # Verify output file content
        with open(output_path, encoding="utf-8") as f:
            file_content = f.read()
        assert "FA/2024/001" in file_content

    def test_process_csv_validation_error(self, sample_config, tmp_path):
        """Test CSV processing with validation errors"""
        # Create CSV with validation errors
        csv_content = """Numer faktury,Data wystawienia,NIP sprzedawcy,Nazwa sprzedawcy
FA/2024/001,2024-01-15,invalid-nip,Test Company"""

        csv_path = tmp_path / "invalid.csv"
        csv_path.write_text(csv_content, encoding="utf-8")

        mapper = CSVToFAMapper(sample_config)

        with pytest.raises(MappingError) as exc_info:
            mapper.process_csv(csv_path)

        assert "Validation failed" in str(exc_info.value)

    def test_get_missing_fields_report(self, sample_config, sample_csv):
        """Test missing fields report generation"""
        mapper = CSVToFAMapper(sample_config)
        df = mapper.read_csv(sample_csv)
        df_mapped = mapper.map_columns(df)
        report = mapper.get_missing_fields_report(df_mapped)

        assert isinstance(report, dict)
        assert "missing_required" in report
        assert "missing_optional" in report
        assert "available_fields" in report
        assert len(report["available_fields"]) > 0


class TestInvoiceTypes:
    """Test different invoice types"""

    @pytest.fixture
    def full_config(self, tmp_path):
        """Create full mapping configuration"""
        config_path = tmp_path / "full_config.yaml"
        # Copy the full config from the actual file
        full_config_path = Path(__file__).parent.parent.parent / "mapping" / "fa3.yaml"
        if full_config_path.exists():
            config_path.write_text(
                full_config_path.read_text(encoding="utf-8"), encoding="utf-8"
            )
        else:
            # Fallback to basic config
            config_path.write_text(
                '''namespaces:
  tns: "http://example.com/invoice"
root_element: "tns:FA"
fields:
  invoice_number:
    xpath: "tns:NrFaktury"
    type: "string"
    required: true
csv_columns:
  default_mapping:
    "Numer faktury": "invoice_number"''',
                encoding="utf-8",
            )
        return config_path

    def test_basic_invoice(self, full_config):
        """Test basic VAT invoice"""
        csv_path = TEST_DATA_DIR / "basic_invoice.csv"
        if not csv_path.exists():
            pytest.skip(f"Test file not found: {csv_path}")

        mapper = CSVToFAMapper(full_config)
        df = mapper.read_csv(csv_path)
        df_mapped = mapper.map_columns(df)

        # Should not have validation errors
        errors = mapper.validate_data(df_mapped)
        assert len(errors) == 0

        # Should generate valid XML
        xml_content = mapper.generate_xml(df_mapped)
        assert "FA/2024/001" in xml_content
        assert "VAT" in xml_content

    def test_minimum_invoice(self, full_config):
        """Test minimum required fields invoice"""
        csv_path = TEST_DATA_DIR / "minimum_invoice.csv"
        if not csv_path.exists():
            pytest.skip(f"Test file not found: {csv_path}")

        mapper = CSVToFAMapper(full_config)
        df = mapper.read_csv(csv_path)
        df_mapped = mapper.map_columns(df)

        # Should not have validation errors
        errors = mapper.validate_data(df_mapped)
        assert len(errors) == 0

        # Should generate valid XML
        xml_content = mapper.generate_xml(df_mapped)
        assert "FA/2024/002" in xml_content

    def test_vat_invoice(self, full_config):
        """Test VAT invoice with different rates"""
        csv_path = TEST_DATA_DIR / "vat_invoice.csv"
        if not csv_path.exists():
            pytest.skip(f"Test file not found: {csv_path}")

        mapper = CSVToFAMapper(full_config)
        df = mapper.read_csv(csv_path)
        df_mapped = mapper.map_columns(df)

        # Should not have validation errors
        errors = mapper.validate_data(df_mapped)
        assert len(errors) == 0

        # Should generate valid XML
        xml_content = mapper.generate_xml(df_mapped)
        assert "FA/2024/003" in xml_content
        assert "23" in xml_content  # VAT rate

    def test_advance_invoice(self, full_config):
        """Test advance payment invoice"""
        csv_path = TEST_DATA_DIR / "advance_invoice.csv"
        if not csv_path.exists():
            pytest.skip(f"Test file not found: {csv_path}")

        mapper = CSVToFAMapper(full_config)
        df = mapper.read_csv(csv_path)
        df_mapped = mapper.map_columns(df)

        # Should not have validation errors
        errors = mapper.validate_data(df_mapped)
        assert len(errors) == 0

        # Should generate valid XML
        xml_content = mapper.generate_xml(df_mapped)
        assert "ZAL/2024/001" in xml_content
        assert "ZALICZKA" in xml_content

    def test_correction_invoice(self, full_config):
        """Test correction invoice"""
        csv_path = TEST_DATA_DIR / "correction_invoice.csv"
        if not csv_path.exists():
            pytest.skip(f"Test file not found: {csv_path}")

        mapper = CSVToFAMapper(full_config)
        df = mapper.read_csv(csv_path)
        df_mapped = mapper.map_columns(df)

        # Should not have validation errors
        errors = mapper.validate_data(df_mapped)
        assert len(errors) == 0

        # Should generate valid XML
        xml_content = mapper.generate_xml(df_mapped)
        assert "KOR/2024/001" in xml_content
        assert "KOREKTA" in xml_content

    def test_mpp_invoice(self, full_config):
        """Test MPP (Simplified Invoice)"""
        csv_path = TEST_DATA_DIR / "mpp_invoice.csv"
        if not csv_path.exists():
            pytest.skip(f"Test file not found: {csv_path}")

        mapper = CSVToFAMapper(full_config)
        df = mapper.read_csv(csv_path)
        df_mapped = mapper.map_columns(df)

        # Should not have validation errors
        errors = mapper.validate_data(df_mapped)
        assert len(errors) == 0

        # Should generate valid XML
        xml_content = mapper.generate_xml(df_mapped)
        assert "MPP/2024/001" in xml_content
        assert "MPP" in xml_content
        assert "0" in xml_content  # 0% VAT rate


class TestMappingError:
    """Test MappingError exception"""

    def test_mapping_error_creation(self):
        """Test MappingError creation and string representation"""
        error = MappingError("Test error", field="test_field", row=5)

        assert error.message == "Test error"
        assert error.field == "test_field"
        assert error.row == 5
        assert "Test error field 'test_field' row 6" == str(error)

    def test_mapping_error_no_location(self):
        """Test MappingError without location information"""
        error = MappingError("Test error")

        assert error.message == "Test error"
        assert error.field is None
        assert error.row is None
        assert "Test error" == str(error)
