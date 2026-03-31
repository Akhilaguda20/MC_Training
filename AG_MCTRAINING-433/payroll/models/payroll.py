from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, field_validator


class PayrollCreateRequest(BaseModel):
    payrollId: Optional[str] = None
    userId: str
    baseSalary: Decimal
    bonus: Optional[Decimal] = Decimal("0")
    deductions: Optional[Decimal] = Decimal("0")
    currency: Optional[str] = "USD"
    effectiveDate: str  # ISO-8601 date string, e.g. "2026-01-01"

    @field_validator("baseSalary", "bonus", "deductions", mode="before")
    @classmethod
    def coerce_to_decimal(cls, v):
        if v is None:
            return Decimal("0")
        return Decimal(str(v))


class PayrollUpdateRequest(BaseModel):
    baseSalary: Optional[Decimal] = None
    bonus: Optional[Decimal] = None
    deductions: Optional[Decimal] = None
    currency: Optional[str] = None
    effectiveDate: Optional[str] = None

    @field_validator("baseSalary", "bonus", "deductions", mode="before")
    @classmethod
    def coerce_to_decimal(cls, v):
        if v is None:
            return None
        return Decimal(str(v))
