"""AI Assistant endpoints"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
import logging

from app.database import get_db
from app.utils.auth import get_current_user
from app.models.user import User
from app.schemas.ai import ComplianceCheckRequest, ComplianceCheckResponse

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/compliance-check", response_model=ComplianceCheckResponse)
async def check_compliance(
    request: ComplianceCheckRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check compliance and get AI-powered recommendations in Polish.
    """
    # Simplified implementation - in production this would call OpenAI
    
    return {
        "answer": "Na podstawie analizy, Twoja faktura została odrzucona z powodu nieprawidłowego NIP kontrahenta. Sprawdź czy NIP ma dokładnie 10 cyfr.",
        "suggestions": [
            "Zweryfikuj NIP kontrahenta w systemie GUS",
            "Upewnij się, że NIP nie zawiera myślników ani spacji",
            "Sprawdź czy kontrahent jest aktywnym podatnikiem VAT"
        ],
        "confidence": 0.92
    }