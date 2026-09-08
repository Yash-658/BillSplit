"""Pydantic contracts for validation responses."""

from pydantic import BaseModel


class ValidationResponse(BaseModel):
    status: str
    calculated_total: int | None
    printed_total: int | None
    difference: int | None
    messages: list[str]
