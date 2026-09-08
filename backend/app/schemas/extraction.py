"""Structured schema returned by Gemini bill extraction."""

from pydantic import BaseModel, Field


class ExtractedNumericField(BaseModel):
    """A nullable paise value with the model's confidence."""

    value: int | None = None
    confidence: float = Field(ge=0, le=1)


class ExtractedTextField(BaseModel):
    """A nullable extracted text value with field-specific confidence."""

    value: str | None = None
    confidence: float = Field(ge=0, le=1)


class ExtractedItem(BaseModel):
    id: str | None = None
    name: ExtractedTextField
    quantity: ExtractedNumericField
    unit_price: ExtractedNumericField
    total_price: ExtractedNumericField
    confidence: float = Field(ge=0, le=1)


class BillExtraction(BaseModel):
    restaurant_name: ExtractedTextField | None = None
    currency: ExtractedTextField | None = None
    items: list[ExtractedItem]
    subtotal: ExtractedNumericField | None = None
    discount: ExtractedNumericField | None = None
    service_charge: ExtractedNumericField | None = None
    taxes: list[ExtractedNumericField] = Field(default_factory=list)
    adjustment: ExtractedNumericField | None = None
    printed_total: ExtractedNumericField | None = None
