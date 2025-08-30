"""Company model for managing business entities"""

from sqlalchemy import Column, String, DateTime, JSON, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.sqlite import UUID as SQLiteUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
from app.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(SQLiteUUID(as_uuid=True), primary_key=True, default=uuid4)
    nip = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    address = Column(JSON, nullable=False)  # {street, city, postal_code, country}
    ksef_token = Column(Text, nullable=True)  # KSeF API token
    ksef_environment = Column(String(20), default="sandbox")  # sandbox, production
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    users = relationship("User", secondary="user_companies", back_populates="companies")
    invoices = relationship("Invoice", back_populates="company")

    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', nip='{self.nip}')>"


class UserCompany(Base):
    """Many-to-many relationship between users and companies"""
    __tablename__ = "user_companies"

    user_id = Column(SQLiteUUID(as_uuid=True), primary_key=True)
    company_id = Column(SQLiteUUID(as_uuid=True), primary_key=True)
    role = Column(String(50), nullable=False, default="accountant")  # owner, supervisor, accountant
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User")
    company = relationship("Company")
