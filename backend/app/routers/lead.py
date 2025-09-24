"""Lead capture endpoints"""

import csv
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Form

router = APIRouter(prefix="/api", tags=["lead"])


LEADS_DIR = Path(__file__).resolve().parents[2] / "out"
LEADS_FILE = LEADS_DIR / "leads.csv"


@router.post("/lead")
async def create_lead(
    firstName: str = Form(...),
    lastName: str = Form(""),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    company: str = Form(...),
    companySize: Optional[str] = Form(None),
    marketing: Optional[bool] = Form(False),
) -> dict:
    LEADS_DIR.mkdir(parents=True, exist_ok=True)
    is_new = not LEADS_FILE.exists()
    with LEADS_FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(
                [
                    "ts",
                    "firstName",
                    "lastName",
                    "email",
                    "phone",
                    "company",
                    "companySize",
                    "marketing",
                ]
            )
        writer.writerow(
            [
                datetime.utcnow().isoformat(),
                firstName,
                lastName,
                email,
                phone or "",
                company,
                companySize or "",
                str(bool(marketing)).lower(),
            ]
        )

    return {"ok": True}
