"""Pydantic contracts for bill calculation."""

from pydantic import BaseModel, ConfigDict, Field

from .bill import BillExtractionRequest
from .validation import ValidationResponse


class CalculateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bill: BillExtractionRequest
    people: list[str] = Field(min_length=2, max_length=7)
    assignments: dict[str, list[str] | str]


class PersonBreakdownResponse(BaseModel):
    item_shares: dict[str, int]
    subtotal: int
    discount: int
    service_charge: int
    tax: int
    adjustment: int
    total: int


class CalculateResponse(BaseModel):
    people: dict[str, PersonBreakdownResponse]
    bill_total: int
    allocated_total: int
    difference: int
    validation: ValidationResponse
