"""KSeF sandbox integration for UPO demo"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ksef", tags=["ksef"])

# In-memory storage for demo purposes
submissions: Dict[str, Dict[str, Any]] = {}


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
    timestamp: str


@router.post("/send", response_model=KSeFSendResponse)
async def send_to_ksef(request: KSeFSendRequest):
    """
    Send FA-3 XML to KSeF sandbox for UPO generation demo
    """
    try:
        # Generate unique submission ID
        submission_id = str(uuid.uuid4())
        
        # Simulate KSeF processing
        logger.info(f"KSeF submission {submission_id} for NIP {request.nip}")
        
        # Store submission for status tracking
        submissions[submission_id] = {
            "nip": request.nip,
            "xml_content": request.xml_content,
            "environment": request.environment,
            "status": "PENDING",
            "created_at": datetime.now().isoformat(),
            "upo_reference": None,
            "details": None
        }
        
        # Simulate async processing - in real implementation this would be a background task
        # For demo, we'll set status to UPO after a short delay
        import asyncio
        asyncio.create_task(process_ksef_submission(submission_id))
        
        return KSeFSendResponse(
            submission_id=submission_id,
            status="PENDING",
            message="FA-3 XML submitted to KSeF sandbox successfully"
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
    if submission_id not in submissions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found"
        )
    
    submission = submissions[submission_id]
    
    return KSeFStatusResponse(
        submission_id=submission_id,
        status=submission["status"],
        details=submission.get("details"),
        upo_reference=submission.get("upo_reference"),
        timestamp=submission["created_at"]
    )


async def process_ksef_submission(submission_id: str):
    """
    Simulate KSeF processing - in real implementation this would call actual KSeF API
    """
    await asyncio.sleep(2)  # Simulate processing time
    
    if submission_id in submissions:
        submissions[submission_id]["status"] = "UPO"
        submissions[submission_id]["upo_reference"] = f"UPO-{submission_id[:8].upper()}"
        submissions[submission_id]["details"] = "FA-3 XML successfully processed by KSeF sandbox"
        
        logger.info(f"KSeF submission {submission_id} completed with UPO")


@router.get("/health")
async def ksef_health_check():
    """
    Health check for KSeF integration
    """
    return {
        "status": "healthy",
        "service": "ksef-sandbox",
        "environment": "demo",
        "active_submissions": len(submissions)
    }
