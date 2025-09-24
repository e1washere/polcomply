"""User Pydantic schemas"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr = Field(..., description="Email użytkownika")
    password: str = Field(..., min_length=8, description="Hasło (minimum 8 znaków)")
    first_name: str = Field(..., min_length=1, description="Imię")
    last_name: str = Field(..., min_length=1, description="Nazwisko")
    role: str = Field(default="accountant", description="Rola użytkownika")


class UserResponse(BaseModel):
    id: UUID
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
