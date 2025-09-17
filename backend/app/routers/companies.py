"""Company management endpoints"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import logging

from app.database import get_db
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
async def list_companies(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """
    List all companies the current user has access to.
    """
    # Simplified implementation
    # In production, this would query the actual company_users relationship

    return [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "Przykładowa Firma Sp. z o.o.",
            "nip": "1234567890",
            "address": {
                "street": "ul. Marszałkowska 100",
                "city": "Warszawa",
                "postal_code": "00-001",
                "country": "PL",
            },
        }
    ]
