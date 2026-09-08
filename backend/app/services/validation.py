"""Validation for reviewed bill arithmetic.

Validation reports discrepancies without changing any of the reviewed input.
All monetary values are integer paise.
"""

from dataclasses import dataclass
from typing import Optional, Sequence


@dataclass(frozen=True)
class ValidationItem:
    """A reviewed item containing the values needed for arithmetic checks."""

    id: str
    name: str
    quantity: int
    unit_price: int
    total_price: int


@dataclass(frozen=True)
class ValidationBill:
    """A reviewed bill to validate."""

    items: Sequence[ValidationItem]
    subtotal: Optional[int]
    discount: Optional[int] = None
    service_charge: Optional[int] = None
    tax: Optional[int] = None
    printed_total: Optional[int] = None


@dataclass(frozen=True)
class ValidationResult:
    """Structured arithmetic validation output."""

    status: str
    calculated_total: Optional[int]
    printed_total: Optional[int]
    difference: Optional[int]
    messages: list[str]


def _optional_amount(value: Optional[int]) -> int:
    return 0 if value is None else value


def _is_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def validate_bill(bill: ValidationBill) -> ValidationResult:
    """Validate item arithmetic, subtotal arithmetic, and printed total."""

    messages: list[str] = []
    item_total = 0
    has_invalid_item_arithmetic = False

    for item in bill.items:
        if not all(
            _is_integer(value)
            for value in (item.quantity, item.unit_price, item.total_price)
        ):
            messages.append(f"Item '{item.name}' has non-integer monetary or quantity values.")
            continue

        expected_item_total = item.quantity * item.unit_price
        item_total += item.total_price
        if expected_item_total != item.total_price:
            has_invalid_item_arithmetic = True
            messages.append(
                f"Item '{item.name}' total mismatch: expected "
                f"{expected_item_total} paise, found {item.total_price} paise."
            )

    if has_invalid_item_arithmetic:
        messages.append(
            "Item arithmetic is invalid; subtotal validation uses the reviewed "
            "line totals."
        )

    if bill.subtotal is None:
        messages.append("Subtotal is missing.")
        calculated_total = None
    elif not _is_integer(bill.subtotal):
        messages.append("Subtotal must be an integer number of paise.")
        calculated_total = None
    else:
        if item_total != bill.subtotal:
            messages.append(
                f"Subtotal mismatch: expected {item_total} paise from items, "
                f"found {bill.subtotal} paise."
            )
        calculated_total = (
            bill.subtotal
            - _optional_amount(bill.discount)
            + _optional_amount(bill.service_charge)
            + _optional_amount(bill.tax)
        )

    difference = None
    if bill.printed_total is None:
        messages.append("Printed total is missing.")
    elif not _is_integer(bill.printed_total):
        messages.append("Printed total must be an integer number of paise.")
    elif calculated_total is not None:
        difference = bill.printed_total - calculated_total
        if difference != 0:
            messages.append(
                f"Printed total mismatch: calculated {calculated_total} paise, "
                f"printed {bill.printed_total} paise, difference {difference} paise."
            )

    return ValidationResult(
        status="valid" if not messages else "warning",
        calculated_total=calculated_total,
        printed_total=bill.printed_total,
        difference=difference,
        messages=messages,
    )
