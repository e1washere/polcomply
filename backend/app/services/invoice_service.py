"""Invoice service for business logic operations"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date
from app.models.invoice import Invoice
from app.models.company import Company
from app.schemas.invoice import InvoiceCreate, InvoiceResponse


class InvoiceService:
    """Service for invoice operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_invoice(self, invoice_data: InvoiceCreate, user_id: UUID) -> Invoice:
        """Create a new invoice"""
        # Calculate totals
        net_amount = 0
        vat_amount = 0
        
        for item in invoice_data.items:
            item_net = item.quantity * item.net_price
            item_vat = item_net * (item.vat_rate / 100)
            net_amount += item_net
            vat_amount += item_vat
        
        gross_amount = net_amount + vat_amount
        
        # Create invoice
        invoice = Invoice(
            company_id=invoice_data.company_id,
            invoice_number=invoice_data.invoice_number,
            issue_date=invoice_data.issue_date,
            sale_date=invoice_data.sale_date,
            due_date=invoice_data.due_date,
            contractor_data=invoice_data.contractor_data.dict(),
            items=[item.dict() for item in invoice_data.items],
            net_amount=net_amount,
            vat_amount=vat_amount,
            gross_amount=gross_amount,
            payment_method=invoice_data.payment_method,
            created_by=user_id,
            ksef_status="pending"
        )
        
        self.db.add(invoice)
        self.db.commit()
        self.db.refresh(invoice)
        
        return invoice
    
    def get_invoice(self, invoice_id: UUID) -> Optional[Invoice]:
        """Get invoice by ID"""
        return self.db.query(Invoice).filter(Invoice.id == invoice_id).first()
    
    def list_invoices(self, company_id: Optional[UUID] = None, 
                     from_date: Optional[date] = None,
                     to_date: Optional[date] = None,
                     status: Optional[str] = None,
                     page: int = 1,
                     limit: int = 20) -> Dict[str, Any]:
        """List invoices with filters"""
        query = self.db.query(Invoice)
        
        if company_id:
            query = query.filter(Invoice.company_id == company_id)
        
        if from_date:
            query = query.filter(Invoice.issue_date >= from_date)
        
        if to_date:
            query = query.filter(Invoice.issue_date <= to_date)
        
        if status:
            query = query.filter(Invoice.ksef_status == status)
        
        total = query.count()
        offset = (page - 1) * limit
        
        invoices = query.order_by(Invoice.issue_date.desc()).offset(offset).limit(limit).all()
        
        return {
            "items": invoices,
            "total": total,
            "page": page,
            "limit": limit
        }
    
    def update_invoice_status(self, invoice_id: UUID, status: str, 
                            upo: Optional[str] = None, error: Optional[str] = None) -> Invoice:
        """Update invoice KSeF status"""
        invoice = self.get_invoice(invoice_id)
        if not invoice:
            raise ValueError("Invoice not found")
        
        invoice.ksef_status = status
        if upo:
            invoice.ksef_upo = upo
        if error:
            invoice.ksef_error = error
        
        self.db.commit()
        self.db.refresh(invoice)
        
        return invoice
    
    def update_validation_errors(self, invoice_id: UUID, errors: List[Dict[str, Any]]) -> Invoice:
        """Update invoice validation errors"""
        invoice = self.get_invoice(invoice_id)
        if not invoice:
            raise ValueError("Invoice not found")
        
        invoice.validation_errors = errors
        self.db.commit()
        self.db.refresh(invoice)
        
        return invoice
