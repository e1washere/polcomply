"""KSeF integration router (mock/sandbox via pluggable client)."""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.config import settings
from app.services.ksef_client import make_ksef_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ksef", tags=["ksef"])

# Pluggable client (mock by default, sandbox if configured)
_client = make_ksef_client(
    mode=settings.KSEF_MODE,
    base_url=settings.KSEF_SANDBOX_BASE_URL,
    timeout_sec=settings.KSEF_TIMEOUT_SEC,
)


class KSeFSendRequest(BaseModel):
    xml_content: str
    nip: str
    environment: str = "sandbox"


class KSeFSendResponse(BaseModel):
    submission_id: str
    status: str
    message: str


class KSeFStatusResponse(BaseModel):
    submission_id: str
    status: str  # "PENDING", "UPO", "ERROR"
    details: Optional[str] = None
    upo_reference: Optional[str] = None
    timestamp: Optional[str] = None


@router.post("/send", response_model=KSeFSendResponse)
async def send_to_ksef(request: KSeFSendRequest):
    """
    Send FA-3 XML to KSeF sandbox for UPO generation demo
    """
    try:
        logger.info("KSeF send requested (mode=%s)", settings.KSEF_MODE)
        submission_id = _client.send(request.xml_content.encode("utf-8"))
        return KSeFSendResponse(
            submission_id=submission_id,
            status="PENDING",
            message="FA-3 XML submitted successfully",
        )
    except Exception as e:
        logger.error(f"KSeF submission error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit to KSeF: {str(e)}"
        )


@router.get("/status", response_model=KSeFStatusResponse)
async def get_ksef_status(submission_id: str):
    """
    Get status of KSeF submission
    """
    try:
        st = _client.status(submission_id)
        return KSeFStatusResponse(
            submission_id=submission_id,
            status=str(st.get("status", "ERROR")),
            details=st.get("details"),
            upo_reference=st.get("upo_reference"),
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        logger.error("KSeF status error: %s", e)
        raise HTTPException(status_code=500, detail="Failed to get status")


async def process_ksef_submission(submission_id: str):
    """Deprecated: kept for compatibility; processing now handled by client."""
    return None


@router.get("/health")
async def ksef_health_check():
    """
    Health check for KSeF integration
    """
    return {
        "status": "healthy",
        "service": "ksef",
        "environment": settings.KSEF_MODE,
        "active_submissions": None
    }
