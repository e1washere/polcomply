"""User model for authentication and authorization"""

from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
from typing import List, TYPE_CHECKING
from app.database import Base

if TYPE_CHECKING:
    from app.models.company import Company


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(
        String(50), nullable=False, default="accountant"
    )  # owner, supervisor, accountant
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    companies = relationship(
        "Company", secondary="user_companies", back_populates="users"
    )
    invoices = relationship("Invoice", back_populates="created_by_user")
    audit_logs = relationship("AuditLog", back_populates="user")

    def has_company_access(self, company_id: str, db) -> bool:
        """Check if user has access to a specific company"""
        from app.models.company import UserCompany

        return (
            db.query(UserCompany)
            .filter(
                UserCompany.user_id == str(self.id),
                UserCompany.company_id == company_id,
            )
            .first()
            is not None
        )

    def get_companies(self, db) -> List["Company"]:
        """Get all companies user has access to"""
        return [uc.company for uc in self.companies]

    def has_role(self, required_role: str) -> bool:
        """Check if user has required role or higher"""
        role_hierarchy = {"accountant": 1, "supervisor": 2, "owner": 3}
        return role_hierarchy.get(self.role, 0) >= role_hierarchy.get(required_role, 0)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
