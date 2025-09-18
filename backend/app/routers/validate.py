"""XML validation router for FA-3 compliance"""

from fastapi import APIRouter, UploadFile, HTTPException, status
import sys
from pathlib import Path

# Add polcomply to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "polcomply"))
from validators.xsd import XSDValidator
from validators.paths import resolve_fa3_schema
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/validate", tags=["validate"])


@router.post("/xml")
async def validate_xml(file: UploadFile):
    """
    Validate XML file against FA-3 schema
    
    This endpoint provides free XML validation for FA-3 compliance.
    Perfect for businesses that need to ensure their invoices meet
    Polish e-invoicing requirements.
    """
    if not file.filename.endswith('.xml'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only XML files are accepted"
        )
    
    # Auto-resolve FA-3 schema
    schema_path = resolve_fa3_schema()
    if schema_path is None:
        logger.error("FA-3 schema not found")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="FA-3 schema not found"
        )
    
    try:
        # Initialize validator
        validator = XSDValidator(schema_path)
        
        # Read uploaded file
        xml_content = await file.read()
        
        # Validate XML
        errors = validator.validate(xml_content)
        
        # Format response
        is_valid = len(errors) == 0
        
        return {
            "ok": is_valid,
            "filename": file.filename,
            "errors": [
                {
                    "line": e.line,
                    "column": e.column,
                    "code": e.code,
                    "message": e.message,
                    "severity": getattr(e, 'severity', 'error')
                }
                for e in errors
            ],
            "summary": {
                "total_errors": len(errors),
                "is_compliant": is_valid,
                "schema_version": "FA-3"
            }
        }
        
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    schema_path = resolve_fa3_schema()
    return {
        "status": "healthy",
        "service": "FA-3 XML Validator",
        "schema_available": schema_path is not None and schema_path.exists()
    }
