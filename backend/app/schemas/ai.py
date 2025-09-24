"""AI-related schemas"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class AIAnalysisRequest(BaseModel):
    """Request for AI analysis of invoice data"""

    invoice_data: Dict[str, Any]
    analysis_type: str = "compliance_check"  # compliance_check, data_extraction, etc.


class AIAnalysisResponse(BaseModel):
    """Response from AI analysis"""

    analysis_id: str
    status: str  # pending, completed, failed
    results: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    warnings: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None


class AIExtractionRequest(BaseModel):
    """Request for AI data extraction from documents"""

    document_type: str  # invoice, receipt, etc.
    document_data: str  # base64 encoded or text content
    extraction_fields: List[str]


class AIExtractionResponse(BaseModel):
    """Response from AI data extraction"""

    extracted_data: Dict[str, Any]
    confidence_scores: Dict[str, float]
    processing_time: float
    warnings: Optional[List[str]] = None


class AIValidationRequest(BaseModel):
    """Request for AI validation of business data"""

    data_type: str  # invoice, company, etc.
    data: Dict[str, Any]
    validation_rules: Optional[List[str]] = None


class AIValidationResponse(BaseModel):
    """Response from AI validation"""

    is_valid: bool
    validation_score: float
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]


class ComplianceCheckRequest(BaseModel):
    """Request for compliance check"""

    invoice_data: Dict[str, Any]
    check_type: str = "full"


class ComplianceCheckResponse(BaseModel):
    """Response from compliance check"""

    is_compliant: bool
    score: float
    issues: List[str]
    recommendations: List[str]
