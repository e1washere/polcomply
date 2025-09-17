"""Tests for FA(3) validator service"""

from decimal import Decimal
from app.services.fa3_validator import FA3Validator


class TestFA3Validator:
    """Test cases for FA(3) validation"""

    def setup_method(self):
        """Set up test fixtures"""
        self.validator = FA3Validator()

        # Valid invoice data template
        self.valid_invoice = {
            "invoice_number": "FV/2024/001",
            "issue_date": "2024-01-15",
            "sale_date": "2024-01-15",
            "due_date": "2024-02-15",
            "contractor_data": {
                "nip": "1234567890",
                "name": "Test Company Sp. z o.o.",
                "address": {
                    "street": "ul. Testowa 1",
                    "city": "Warszawa",
                    "postal_code": "00-001",
                    "country": "PL",
                },
            },
            "items": [
                {
                    "name": "Test Product",
                    "quantity": Decimal("2"),
                    "unit": "szt.",
                    "net_price": Decimal("100.00"),
                    "vat_rate": 23,
                }
            ],
            "payment_method": "transfer",
            "net_amount": Decimal("200.00"),
            "vat_amount": Decimal("46.00"),
            "gross_amount": Decimal("246.00"),
            "currency": "PLN",
        }

    def test_valid_invoice_passes_validation(self):
        """Test that a valid invoice passes all validation checks"""
        result = self.validator.validate_invoice(self.valid_invoice)

        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0

    def test_missing_invoice_number(self):
        """Test validation fails when invoice number is missing"""
        invoice = self.valid_invoice.copy()
        invoice["invoice_number"] = ""

        result = self.validator.validate_invoice(invoice)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "FA3_001"
        assert "Numer faktury jest wymagany" in result.errors[0].message

    def test_invoice_number_too_long(self):
        """Test validation fails when invoice number is too long"""
        invoice = self.valid_invoice.copy()
        invoice["invoice_number"] = "A" * 51

        result = self.validator.validate_invoice(invoice)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "FA3_003"
        assert "za długi" in result.errors[0].message

    def test_invoice_number_format_warning(self):
        """Test warning when invoice number doesn't contain separator"""
        invoice = self.valid_invoice.copy()
        invoice["invoice_number"] = "FV2024001"

        result = self.validator.validate_invoice(invoice)

        assert result.is_valid is True
        assert len(result.warnings) == 1
        assert result.warnings[0].code == "FA3_002"
        assert "separator" in result.warnings[0].message

    def test_missing_issue_date(self):
        """Test validation fails when issue date is missing"""
        invoice = self.valid_invoice.copy()
        invoice["issue_date"] = ""

        result = self.validator.validate_invoice(invoice)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "FA3_004"
        assert "Data wystawienia jest wymagana" in result.errors[0].message

    def test_invalid_date_format(self):
        """Test validation fails with invalid date format"""
        invoice = self.valid_invoice.copy()
        invoice["issue_date"] = "15-01-2024"

        result = self.validator.validate_invoice(invoice)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "FA3_005"
        assert "Nieprawidłowy format daty" in result.errors[0].message

    def test_due_date_before_issue_date(self):
        """Test validation fails when due date is before issue date"""
        invoice = self.valid_invoice.copy()
        invoice["due_date"] = "2024-01-10"

        result = self.validator.validate_invoice(invoice)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "FA3_011"
        assert "wcześniejszy niż data wystawienia" in result.errors[0].message

    def test_sale_date_after_issue_date_warning(self):
        """Test warning when sale date is after issue date"""
        invoice = self.valid_invoice.copy()
        invoice["sale_date"] = "2024-01-20"

        result = self.validator.validate_invoice(invoice)

        assert result.is_valid is True
        assert len(result.warnings) == 1
        assert result.warnings[0].code == "FA3_010"
        assert "późniejsza niż data wystawienia" in result.warnings[0].message

    def test_missing_contractor_nip(self):
        """Test validation fails when contractor NIP is missing"""
        invoice = self.valid_invoice.copy()
        invoice["contractor_data"]["nip"] = ""

        result = self.validator.validate_invoice(invoice)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "FA3_012"
        assert "NIP kontrahenta jest wymagany" in result.errors[0].message

    def test_invalid_nip_format(self):
        """Test validation fails with invalid NIP format"""
        invoice = self.valid_invoice.copy()
        invoice["contractor_data"]["nip"] = "123456789"

        result = self.validator.validate_invoice(invoice)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "FA3_013"
        assert "dokładnie 10 cyfr" in result.errors[0].message

    def test_invalid_nip_checksum(self):
        """Test validation fails with invalid NIP checksum"""
        invoice = self.valid_invoice.copy()
        invoice["contractor_data"]["nip"] = "1234567891"  # Invalid checksum

        result = self.validator.validate_invoice(invoice)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "FA3_014"
        assert "suma kontrolna" in result.errors[0].message

    def test_valid_nip_checksum(self):
        """Test validation passes with valid NIP checksum"""
        # Valid NIP: 5260305408
        invoice = self.valid_invoice.copy()
        invoice["contractor_data"]["nip"] = "5260305408"

        result = self.validator.validate_invoice(invoice)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_missing_contractor_address(self):
        """Test validation fails when contractor address is missing"""
        invoice = self.valid_invoice.copy()
        invoice["contractor_data"]["address"]["street"] = ""

        result = self.validator.validate_invoice(invoice)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "FA3_015"
        assert "Ulica jest wymagana" in result.errors[0].message

    def test_invalid_postal_code_format(self):
        """Test validation fails with invalid postal code format"""
        invoice = self.valid_invoice.copy()
        invoice["contractor_data"]["address"]["postal_code"] = "00001"

        result = self.validator.validate_invoice(invoice)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "FA3_016"
        assert "Nieprawidłowy format kodu pocztowego" in result.errors[0].message

    def test_missing_items(self):
        """Test validation fails when no items are provided"""
        invoice = self.valid_invoice.copy()
        invoice["items"] = []

        result = self.validator.validate_invoice(invoice)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "FA3_017"
        assert "przynajmniej jedną pozycję" in result.errors[0].message

    def test_item_missing_name(self):
        """Test validation fails when item name is missing"""
        invoice = self.valid_invoice.copy()
        invoice["items"][0]["name"] = ""

        result = self.validator.validate_invoice(invoice)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "FA3_018"
        assert "Nazwa pozycji jest wymagana" in result.errors[0].message

    def test_item_invalid_quantity(self):
        """Test validation fails with invalid item quantity"""
        invoice = self.valid_invoice.copy()
        invoice["items"][0]["quantity"] = Decimal("0")

        result = self.validator.validate_invoice(invoice)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "FA3_019"
        assert "większa niż 0" in result.errors[0].message

    def test_item_invalid_vat_rate(self):
        """Test validation fails with invalid VAT rate"""
        invoice = self.valid_invoice.copy()
        invoice["items"][0]["vat_rate"] = 15

        result = self.validator.validate_invoice(invoice)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "FA3_022"
        assert "Nieprawidłowa stawka VAT" in result.errors[0].message

    def test_vat_calculation_mismatch(self):
        """Test validation fails when VAT calculations don't match"""
        invoice = self.valid_invoice.copy()
        invoice["vat_amount"] = Decimal("50.00")  # Should be 46.00

        result = self.validator.validate_invoice(invoice)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "FA3_024"
        assert "podatku VAT nie zgadza się" in result.errors[0].message

    def test_net_amount_calculation_mismatch(self):
        """Test validation fails when net amount calculations don't match"""
        invoice = self.valid_invoice.copy()
        invoice["net_amount"] = Decimal("250.00")  # Should be 200.00

        result = self.validator.validate_invoice(invoice)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "FA3_023"
        assert "wartości netto nie zgadza się" in result.errors[0].message

    def test_gross_amount_calculation_mismatch(self):
        """Test validation fails when gross amount doesn't equal net + VAT"""
        invoice = self.valid_invoice.copy()
        invoice["gross_amount"] = Decimal("250.00")  # Should be 246.00

        result = self.validator.validate_invoice(invoice)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "FA3_027"
        assert "brutto nie zgadza się" in result.errors[0].message

    def test_invalid_payment_method(self):
        """Test validation fails with invalid payment method"""
        invoice = self.valid_invoice.copy()
        invoice["payment_method"] = "bitcoin"

        result = self.validator.validate_invoice(invoice)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "FA3_026"
        assert "Nieprawidłowa metoda płatności" in result.errors[0].message

    def test_negative_amounts(self):
        """Test validation fails with negative amounts"""
        invoice = self.valid_invoice.copy()
        invoice["net_amount"] = Decimal("-100.00")

        result = self.validator.validate_invoice(invoice)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "FA3_028"
        assert "nie może być ujemna" in result.errors[0].message

    def test_non_pln_currency(self):
        """Test validation fails with non-PLN currency"""
        invoice = self.valid_invoice.copy()
        invoice["currency"] = "EUR"

        result = self.validator.validate_invoice(invoice)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0].code == "FA3_030"
        assert "wymaga waluty PLN" in result.errors[0].message

    def test_multiple_validation_errors(self):
        """Test multiple validation errors are reported"""
        invoice = self.valid_invoice.copy()
        invoice["invoice_number"] = ""
        invoice["contractor_data"]["nip"] = ""
        invoice["items"] = []

        result = self.validator.validate_invoice(invoice)

        assert result.is_valid is False
        assert len(result.errors) == 3
        assert any(error.code == "FA3_001" for error in result.errors)
        assert any(error.code == "FA3_012" for error in result.errors)
        assert any(error.code == "FA3_017" for error in result.errors)

    def test_validation_error_structure(self):
        """Test validation error structure is correct"""
        invoice = self.valid_invoice.copy()
        invoice["invoice_number"] = ""

        result = self.validator.validate_invoice(invoice)
        error = result.errors[0]

        assert hasattr(error, "path")
        assert hasattr(error, "code")
        assert hasattr(error, "message")
        assert hasattr(error, "fix_hint")
        assert hasattr(error, "severity")
        assert error.severity == "error"

    def test_warning_structure(self):
        """Test warning structure is correct"""
        invoice = self.valid_invoice.copy()
        invoice["invoice_number"] = "FV2024001"  # No separator

        result = self.validator.validate_invoice(invoice)
        warning = result.warnings[0]

        assert hasattr(warning, "path")
        assert hasattr(warning, "code")
        assert hasattr(warning, "message")
        assert hasattr(warning, "fix_hint")
        assert hasattr(warning, "severity")
        assert warning.severity == "warning"
