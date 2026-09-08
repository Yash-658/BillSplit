"""Pydantic contracts for reviewed bill data."""

from pydantic import BaseModel, ConfigDict, Field


class BillItemRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    quantity: int = Field(ge=0)
    unit_price: int = Field(ge=0)
    total_price: int = Field(ge=0)


class BillExtractionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    items: list[BillItemRequest]
    subtotal: int | None = Field(default=None, ge=0)
    discount: int | None = Field(default=None, ge=0)
    service_charge: int | None = Field(default=None, ge=0)
    tax: int | None = Field(default=None, ge=0)
    adjustment: int | None = None
    printed_total: int | None = Field(default=None, ge=0)
