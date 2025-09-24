"""
Invoice model for FA(3) compliant invoices

Licensed under the Business Source License 1.1 (BSL).
See LICENSE file for full terms.
"""

from sqlalchemy import Column, String, DateTime, JSON, Numeric, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
from app.database import Base


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    invoice_number = Column(String(100), nullable=False)
    issue_date = Column(DateTime, nullable=False)
    sale_date = Column(DateTime, nullable=False)
    due_date = Column(DateTime, nullable=False)
    contractor_data = Column(JSON, nullable=False)  # {nip, name, address}
    items = Column(JSON, nullable=False)  # Array of invoice items
    net_amount = Column(Numeric(10, 2), nullable=False)
    vat_amount = Column(Numeric(10, 2), nullable=False)
    gross_amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(50), nullable=False)
    ksef_status = Column(
        String(50), default="pending"
    )  # pending, submitted, accepted, rejected
    ksef_upo = Column(Text, nullable=True)  # KSeF UPO (Unique Payment Order)
    ksef_error = Column(Text, nullable=True)  # KSeF error message
    validation_errors = Column(JSON, nullable=True)  # FA(3) validation errors
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="invoices")
    created_by_user = relationship("User", back_populates="invoices")

    def __repr__(self):
        return f"<Invoice(id={self.id}, number='{self.invoice_number}', status='{self.ksef_status}')>"
