"""Structured schema returned by Gemini bill extraction."""

from pydantic import BaseModel, Field


class ExtractedNumericField(BaseModel):
    """A nullable paise value with the model's confidence."""

    value: int | None = None
    confidence: float = Field(ge=0, le=1)


class ExtractedItem(BaseModel):
    id: str | None = None
    name: str | None = None
    quantity: int | None = None
    unit_price: ExtractedNumericField
    total_price: ExtractedNumericField
    confidence: float = Field(ge=0, le=1)


class BillExtraction(BaseModel):
    restaurant_name: str | None = None
    currency: str | None = None
    items: list[ExtractedItem]
    subtotal: ExtractedNumericField | None = None
    discount: ExtractedNumericField | None = None
    service_charge: ExtractedNumericField | None = None
    taxes: list[ExtractedNumericField] = Field(default_factory=list)
    adjustment: int | None = None
    printed_total: ExtractedNumericField | None = None
