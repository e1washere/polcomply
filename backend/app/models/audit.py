"""Audit log model for tracking user actions"""

from sqlalchemy import Column, String, DateTime, JSON, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.sqlite import UUID as SQLiteUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid import uuid4
from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(SQLiteUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(SQLiteUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(SQLiteUUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    action = Column(String(100), nullable=False)  # invoice.create, invoice.update, etc.
    entity_type = Column(String(50), nullable=False)  # invoice, company, user, etc.
    entity_id = Column(SQLiteUUID(as_uuid=True), nullable=True)
    changes = Column(JSON, nullable=True)  # What was changed
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', user_id={self.user_id})>"


def create_audit_log(db, user_id: str, company_id: str = None, action: str = None, 
                    entity_type: str = None, entity_id: str = None, changes: dict = None,
                    ip_address: str = None, user_agent: str = None):
    """Helper function to create audit log entries"""
    audit_log = AuditLog(
        user_id=user_id,
        company_id=company_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        changes=changes,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(audit_log)
    db.commit()
    return audit_log
