"""
Invoice Pydantic schemas for API validation

Licensed under the Business Source License 1.1 (BSL).
See LICENSE file for full terms.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from uuid import UUID
from decimal import Decimal


class InvoiceItemCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Nazwa produktu lub usługi")
    quantity: Decimal = Field(..., gt=0, description="Ilość")
    unit: str = Field(..., min_length=1, description="Jednostka miary")
    net_price: Decimal = Field(..., gt=0, description="Cena jednostkowa netto")
    vat_rate: int = Field(..., ge=0, le=23, description="Stawka VAT w procentach")
    net_amount: Optional[Decimal] = None
    vat_amount: Optional[Decimal] = None

    @field_validator('vat_rate')
    @classmethod
    def validate_vat_rate(cls, v):
        allowed_rates = [0, 5, 8, 23]
        if v not in allowed_rates:
            raise ValueError(f"Stawka VAT {v}% nie jest dozwolona. Dozwolone stawki: {allowed_rates}")
        return v


class ContractorAddress(BaseModel):
    street: str = Field(..., min_length=1, description="Ulica i numer")
    city: str = Field(..., min_length=1, description="Miasto")
    postal_code: str = Field(..., pattern=r'^\d{2}-\d{3}$', description="Kod pocztowy w formacie XX-XXX")
    country: str = Field(default="PL", description="Kod kraju")


class ContractorData(BaseModel):
    nip: str = Field(..., pattern=r'^\d{10}$', description="NIP - 10 cyfr")
    name: str = Field(..., min_length=1, description="Nazwa kontrahenta")
    address: ContractorAddress


class InvoiceCreate(BaseModel):
    company_id: UUID = Field(..., description="ID firmy")
    invoice_number: str = Field(..., min_length=1, description="Numer faktury")
    issue_date: date = Field(..., description="Data wystawienia")
    sale_date: date = Field(..., description="Data sprzedaży")
    due_date: date = Field(..., description="Termin płatności")
    contractor_data: ContractorData
    items: List[InvoiceItemCreate] = Field(..., min_length=1, description="Pozycje faktury")
    payment_method: str = Field(..., description="Metoda płatności")

    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v, info):
        if 'issue_date' in info.data and v < info.data['issue_date']:
            raise ValueError("Termin płatności nie może być wcześniejszy niż data wystawienia")
        return v


class InvoiceResponse(BaseModel):
    id: UUID
    company_id: UUID
    invoice_number: str
    issue_date: datetime
    sale_date: datetime
    due_date: datetime
    contractor_data: Dict[str, Any]
    items: List[Dict[str, Any]]
    net_amount: Decimal
    vat_amount: Decimal
    gross_amount: Decimal
    payment_method: str
    ksef_status: str
    ksef_upo: Optional[str] = None
    ksef_error: Optional[str] = None
    validation_errors: Optional[List[Dict[str, Any]]] = None
    created_by: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class InvoiceList(BaseModel):
    items: List[InvoiceResponse]
    total: int
    page: int
    limit: int


class ValidationError(BaseModel):
    path: str = Field(..., description="Ścieżka do pola z błędem")
    code: str = Field(..., description="Kod błędu")
    message: str = Field(..., description="Komunikat błędu w języku polskim")
    fix_hint: str = Field(..., description="Wskazówka jak naprawić błąd")
    severity: str = Field(default="error", description="Poziom ważności: error, warning, info")


class ValidationResult(BaseModel):
    is_valid: bool = Field(..., description="Czy faktura jest poprawna")
    errors: List[ValidationError] = Field(default_factory=list, description="Lista błędów walidacji")
    warnings: List[ValidationError] = Field(default_factory=list, description="Lista ostrzeżeń")
    invoice_data: Optional[Dict[str, Any]] = None
