#!/usr/bin/env python3
"""Simple test script for FA3Validator"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.fa3_validator import FA3Validator
from decimal import Decimal


def test_fa3_validator():
    """Test FA3Validator with sample data"""
    print("Testing FA3Validator...")

    validator = FA3Validator()

    # Valid invoice data
    valid_invoice = {
        "invoice_number": "FV/2024/001",
        "issue_date": "2024-01-15",
        "sale_date": "2024-01-15",
        "due_date": "2024-02-15",
        "contractor_data": {
            "nip": "5260305408",  # Valid NIP
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

    # Test valid invoice
    result = validator.validate_invoice(valid_invoice)
    print(f"Valid invoice test: {'PASS' if result.is_valid else 'FAIL'}")
    print(f"Errors: {len(result.errors)}")
    print(f"Warnings: {len(result.warnings)}")

    # Test invalid invoice
    invalid_invoice = valid_invoice.copy()
    invalid_invoice["invoice_number"] = ""
    invalid_invoice["contractor_data"]["nip"] = "123456789"

    result = validator.validate_invoice(invalid_invoice)
    print(f"\nInvalid invoice test: {'PASS' if not result.is_valid else 'FAIL'}")
    print(f"Errors: {len(result.errors)}")
    for error in result.errors:
        print(f"  - {error.code}: {error.message}")

    print("\nFA3Validator test completed successfully!")


if __name__ == "__main__":
    test_fa3_validator()
