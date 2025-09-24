"""Invoice management endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from datetime import date
import logging

from app.database import get_db
from app.models.invoice import Invoice
from app.models.company import Company
from app.schemas.invoice import (
    InvoiceCreate,
    InvoiceResponse,
    InvoiceList,
    ValidationResult,
)
from app.services.fa3_validator import FA3Validator
from app.utils.auth import get_current_user
from app.models.user import User
from app.models.audit import create_audit_log

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice_data: InvoiceCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a new invoice and queue it for KSeF submission.

    This endpoint:
    1. Validates invoice data
    2. Calculates VAT amounts
    3. Saves invoice to database
    4. Queues KSeF submission as background task
    """
    # Verify user has access to the company
    company = db.query(Company).filter(Company.id == invoice_data.company_id).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Firma nie została znaleziona",  # Company not found
        )

    # Check user permissions
    if not current_user.has_company_access(company.id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Brak dostępu do tej firmy",  # No access to this company
        )

    # Initialize invoice service
    # invoice_service = InvoiceService(db)  # TODO: Use for business logic

    # Calculate totals
    net_amount = 0
    vat_amount = 0

    for item in invoice_data.items:
        item_net = item.quantity * item.net_price
        item_vat = item_net * (item.vat_rate / 100)
        net_amount += item_net
        vat_amount += item_vat
        item.net_amount = item_net
        item.vat_amount = item_vat

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
        created_by=current_user.id,
        ksef_status="pending",
    )

    db.add(invoice)
    db.commit()
    db.refresh(invoice)

    # Create audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        company_id=company.id,
        action="invoice.create",
        entity_type="invoice",
        entity_id=invoice.id,
        changes={
            "invoice_number": invoice.invoice_number,
            "gross_amount": float(invoice.gross_amount),
        },
    )

    # Queue KSeF submission as background task
    background_tasks.add_task(
        submit_invoice_to_ksef, invoice_id=invoice.id, company_id=company.id
    )

    logger.info(
        f"Invoice {invoice.invoice_number} created by user {current_user.email}"
    )

    return invoice


async def submit_invoice_to_ksef(invoice_id: UUID, company_id: UUID):
    """Background task to submit invoice to KSeF"""
    try:
        # This would be implemented with Celery in production
        # For now, we'll use FastAPI's BackgroundTasks
        from app.workers.tasks import submit_invoice_task

        submit_invoice_task.delay(str(invoice_id), str(company_id))
    except Exception as e:
        logger.error(f"Failed to queue KSeF submission for invoice {invoice_id}: {e}")


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get invoice details by ID"""
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faktura nie została znaleziona",  # Invoice not found
        )

    # Check access
    if not current_user.has_company_access(invoice.company_id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Brak dostępu do tej faktury",  # No access to this invoice
        )

    return invoice


@router.get("/", response_model=InvoiceList)
async def list_invoices(
    company_id: Optional[UUID] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List invoices with filters"""
    query = db.query(Invoice)

    # Filter by company if specified
    if company_id:
        if not current_user.has_company_access(company_id, db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Brak dostępu do tej firmy",
            )
        query = query.filter(Invoice.company_id == company_id)
    else:
        # Get all companies user has access to
        user_companies = current_user.get_companies(db)
        company_ids = [c.id for c in user_companies]
        query = query.filter(Invoice.company_id.in_(company_ids))

    # Apply date filters
    if from_date:
        query = query.filter(Invoice.issue_date >= from_date)
    if to_date:
        query = query.filter(Invoice.issue_date <= to_date)

    # Apply status filter
    if status:
        query = query.filter(Invoice.ksef_status == status)

    # Calculate pagination
    total = query.count()
    offset = (page - 1) * limit

    # Get invoices
    invoices = (
        query.order_by(Invoice.issue_date.desc()).offset(offset).limit(limit).all()
    )

    return {"items": invoices, "total": total, "page": page, "limit": limit}


@router.post("/validate-fa3", response_model=ValidationResult)
async def validate_fa3(
    invoice_data: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Validate invoice data against FA(3) requirements.

    This endpoint performs comprehensive validation of invoice data
    against Polish FA(3) compliance rules and returns detailed error
    messages with fix hints in Polish.
    """
    # Verify user has access to the company
    company = db.query(Company).filter(Company.id == invoice_data.company_id).first()

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Firma nie została znaleziona"
        )

    # Check user permissions
    if not current_user.has_company_access(company.id, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Brak dostępu do tej firmy"
        )

    # Initialize FA(3) validator
    validator = FA3Validator()

    # Convert Pydantic model to dict for validation
    invoice_dict = invoice_data.dict()

    # Add calculated amounts for validation
    net_amount = 0
    vat_amount = 0

    for item in invoice_data.items:
        item_net = item.quantity * item.net_price
        item_vat = item_net * (item.vat_rate / 100)
        net_amount += item_net
        vat_amount += item_vat

    invoice_dict["net_amount"] = net_amount
    invoice_dict["vat_amount"] = vat_amount
    invoice_dict["gross_amount"] = net_amount + vat_amount
    invoice_dict["currency"] = "PLN"  # FA(3) requires PLN

    # Perform validation
    validation_result = validator.validate_invoice(invoice_dict)

    # Create audit log
    create_audit_log(
        db=db,
        user_id=current_user.id,
        company_id=company.id,
        action="invoice.validate_fa3",
        entity_type="invoice",
        changes={
            "invoice_number": invoice_data.invoice_number,
            "validation_errors_count": len(validation_result.errors),
            "validation_warnings_count": len(validation_result.warnings),
            "is_valid": validation_result.is_valid,
        },
    )

    logger.info(
        f"FA(3) validation completed for invoice {invoice_data.invoice_number} by user {current_user.email}"
    )

    return validation_result
