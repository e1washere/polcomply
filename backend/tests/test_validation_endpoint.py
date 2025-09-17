"""Tests for FA(3) validation endpoint"""

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app.models.user import User
from app.models.company import Company, UserCompany
from app.utils.auth import create_access_token


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


class TestValidationEndpoint:
    """Test cases for /validate-fa3 endpoint"""

    def setup_method(self):
        """Set up test database and data"""
        Base.metadata.create_all(bind=engine)

        # Create test user
        self.test_user = User(
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User",
            role="accountant",
        )

        # Create test company
        self.test_company = Company(
            nip="1234567890",
            name="Test Company",
            address={
                "street": "ul. Testowa 1",
                "city": "Warszawa",
                "postal_code": "00-001",
                "country": "PL",
            },
        )

        # Add to database
        db = TestingSessionLocal()
        db.add(self.test_user)
        db.add(self.test_company)
        db.commit()
        db.refresh(self.test_user)
        db.refresh(self.test_company)

        # Create user-company relationship
        user_company = UserCompany(
            user_id=self.test_user.id,
            company_id=self.test_company.id,
            role="accountant",
        )
        db.add(user_company)
        db.commit()
        db.close()

        # Create access token
        self.access_token = create_access_token(data={"sub": str(self.test_user.id)})
        self.headers = {"Authorization": f"Bearer {self.access_token}"}

        # Valid invoice data
        self.valid_invoice_data = {
            "company_id": str(self.test_company.id),
            "invoice_number": "FV/2024/001",
            "issue_date": "2024-01-15",
            "sale_date": "2024-01-15",
            "due_date": "2024-02-15",
            "contractor_data": {
                "nip": "5260305408",
                "name": "Test Contractor Sp. z o.o.",
                "address": {
                    "street": "ul. Kontrahenta 1",
                    "city": "Kraków",
                    "postal_code": "30-001",
                    "country": "PL",
                },
            },
            "items": [
                {
                    "name": "Test Product",
                    "quantity": 2,
                    "unit": "szt.",
                    "net_price": 100.00,
                    "vat_rate": 23,
                }
            ],
            "payment_method": "transfer",
        }

    def teardown_method(self):
        """Clean up test database"""
        Base.metadata.drop_all(bind=engine)

    def test_validate_valid_invoice(self):
        """Test validation of a valid invoice"""
        response = client.post(
            "/v1/invoices/validate-fa3",
            json=self.valid_invoice_data,
            headers=self.headers,
        )

        assert response.status_code == 200
        data = response.json()

        assert data["is_valid"] is True
        assert len(data["errors"]) == 0
        assert len(data["warnings"]) == 0

    def test_validate_invoice_without_auth(self):
        """Test validation fails without authentication"""
        response = client.post(
            "/v1/invoices/validate-fa3", json=self.valid_invoice_data
        )

        assert response.status_code == 401

    def test_validate_invoice_invalid_company(self):
        """Test validation fails with invalid company ID"""
        import uuid

        invalid_data = self.valid_invoice_data.copy()
        invalid_data["company_id"] = str(uuid.uuid4())

        response = client.post(
            "/v1/invoices/validate-fa3", json=invalid_data, headers=self.headers
        )

        assert response.status_code == 404
        assert "Firma nie została znaleziona" in response.json()["detail"]

    def test_validate_invoice_missing_invoice_number(self):
        """Test validation fails with missing invoice number"""
        invalid_data = self.valid_invoice_data.copy()
        invalid_data["invoice_number"] = ""

        response = client.post(
            "/v1/invoices/validate-fa3", json=invalid_data, headers=self.headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["is_valid"] is False
        assert len(data["errors"]) == 1
        assert data["errors"][0]["code"] == "FA3_001"
        assert "Numer faktury jest wymagany" in data["errors"][0]["message"]

    def test_validate_invoice_invalid_nip(self):
        """Test validation fails with invalid NIP"""
        invalid_data = self.valid_invoice_data.copy()
        invalid_data["contractor_data"]["nip"] = "123456789"

        response = client.post(
            "/v1/invoices/validate-fa3", json=invalid_data, headers=self.headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["is_valid"] is False
        assert len(data["errors"]) == 1
        assert data["errors"][0]["code"] == "FA3_013"
        assert "dokładnie 10 cyfr" in data["errors"][0]["message"]

    def test_validate_invoice_invalid_postal_code(self):
        """Test validation fails with invalid postal code"""
        invalid_data = self.valid_invoice_data.copy()
        invalid_data["contractor_data"]["address"]["postal_code"] = "00001"

        response = client.post(
            "/v1/invoices/validate-fa3", json=invalid_data, headers=self.headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["is_valid"] is False
        assert len(data["errors"]) == 1
        assert data["errors"][0]["code"] == "FA3_016"
        assert "Nieprawidłowy format kodu pocztowego" in data["errors"][0]["message"]

    def test_validate_invoice_invalid_vat_rate(self):
        """Test validation fails with invalid VAT rate"""
        invalid_data = self.valid_invoice_data.copy()
        invalid_data["items"][0]["vat_rate"] = 15

        response = client.post(
            "/v1/invoices/validate-fa3", json=invalid_data, headers=self.headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["is_valid"] is False
        assert len(data["errors"]) == 1
        assert data["errors"][0]["code"] == "FA3_022"
        assert "Nieprawidłowa stawka VAT" in data["errors"][0]["message"]

    def test_validate_invoice_multiple_errors(self):
        """Test validation reports multiple errors"""
        invalid_data = self.valid_invoice_data.copy()
        invalid_data["invoice_number"] = ""
        invalid_data["contractor_data"]["nip"] = "123456789"
        invalid_data["items"] = []

        response = client.post(
            "/v1/invoices/validate-fa3", json=invalid_data, headers=self.headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["is_valid"] is False
        assert len(data["errors"]) == 3

        error_codes = [error["code"] for error in data["errors"]]
        assert "FA3_001" in error_codes
        assert "FA3_013" in error_codes
        assert "FA3_017" in error_codes

    def test_validate_invoice_warning(self):
        """Test validation includes warnings"""
        invalid_data = self.valid_invoice_data.copy()
        invalid_data["invoice_number"] = "FV2024001"  # No separator

        response = client.post(
            "/v1/invoices/validate-fa3", json=invalid_data, headers=self.headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["is_valid"] is True
        assert len(data["warnings"]) == 1
        assert data["warnings"][0]["code"] == "FA3_002"
        assert "separator" in data["warnings"][0]["message"]
        assert data["warnings"][0]["severity"] == "warning"

    def test_validate_invoice_error_structure(self):
        """Test validation error structure is correct"""
        invalid_data = self.valid_invoice_data.copy()
        invalid_data["invoice_number"] = ""

        response = client.post(
            "/v1/invoices/validate-fa3", json=invalid_data, headers=self.headers
        )

        assert response.status_code == 200
        data = response.json()
        error = data["errors"][0]

        assert "path" in error
        assert "code" in error
        assert "message" in error
        assert "fix_hint" in error
        assert "severity" in error
        assert error["severity"] == "error"

    def test_validate_invoice_calculation_validation(self):
        """Test validation checks VAT and amount calculations"""
        invalid_data = self.valid_invoice_data.copy()
        # Add calculated amounts that don't match items
        invalid_data["net_amount"] = 300.00  # Should be 200.00
        invalid_data["vat_amount"] = 69.00  # Should be 46.00
        invalid_data["gross_amount"] = 369.00  # Should be 246.00

        response = client.post(
            "/v1/invoices/validate-fa3", json=invalid_data, headers=self.headers
        )

        assert response.status_code == 200
        data = response.json()

        assert data["is_valid"] is False
        assert len(data["errors"]) >= 2  # Should have calculation errors

        error_codes = [error["code"] for error in data["errors"]]
        assert (
            "FA3_023" in error_codes
            or "FA3_024" in error_codes
            or "FA3_027" in error_codes
        )
