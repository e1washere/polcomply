"""Company Pydantic schemas"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import re


class CompanyCreate(BaseModel):
    nip: str = Field(..., description="NIP firmy")
    name: str = Field(..., min_length=1, description="Nazwa firmy")
    address: Dict[str, Any] = Field(..., description="Adres firmy")
    ksef_token: Optional[str] = Field(None, description="Token KSeF")
    ksef_environment: str = Field(default="sandbox", description="Środowisko KSeF")

    @field_validator('nip')
    @classmethod
    def validate_nip(cls, v):
        if not re.match(r'^\d{10}$', v):
            raise ValueError('NIP musi składać się z dokładnie 10 cyfr')
        return v


class CompanyResponse(BaseModel):
    id: UUID
    nip: str
    name: str
    address: Dict[str, Any]
    ksef_environment: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
