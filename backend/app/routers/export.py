from __future__ import annotations

from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Literal, Any, Dict
from io import BytesIO

from app.services.exporters.fakturownia_csv import export_fakturownia_csv
from app.services.exporters.wfirma_csv import export_wfirma_csv
from app.config import settings


router = APIRouter(prefix="/api", tags=["export"])


class ExportRequest(BaseModel):
    target: Literal["fakturownia", "wfirma"]
    invoice: Dict[str, Any]


@router.post("/export")
async def export_invoice(req: ExportRequest, request: Request):
    # Paywall: block on Free plan
    if settings.DEMO_PAYWALL_ENABLED:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED,
                            detail="Free plan: export unavailable. Upgrade to Starter/Growth.")
    try:
        if req.target == "fakturownia":
            csv_text = export_fakturownia_csv(req.invoice)
            filename = "fakturownia.csv"
        else:
            csv_text = export_wfirma_csv(req.invoice)
            filename = "wfirma.csv"

        bio = BytesIO(csv_text.encode("utf-8"))
        headers = {"Content-Disposition": f"attachment; filename={filename}"}
        return StreamingResponse(bio, media_type="text/csv", headers=headers)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


