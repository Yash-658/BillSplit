"""Bill validation and calculation endpoints."""

from fastapi import APIRouter, HTTPException

from backend.app.schemas.bill import BillExtractionRequest
from backend.app.schemas.split import (
    CalculateRequest,
    CalculateResponse,
    PersonBreakdownResponse,
)
from backend.app.schemas.validation import ValidationResponse
from backend.app.services.calculator import Bill, BillItem, calculate_split
from backend.app.services.validation import (
    ValidationBill,
    ValidationItem,
    validate_bill,
)

router = APIRouter()


def _validation_bill(request: BillExtractionRequest) -> ValidationBill:
    return ValidationBill(
        items=[
            ValidationItem(
                id=item.id,
                name=item.name,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price,
            )
            for item in request.items
        ],
        subtotal=request.subtotal,
        discount=request.discount,
        service_charge=request.service_charge,
        tax=request.tax,
        printed_total=request.printed_total,
    )


def _calculator_bill(request: BillExtractionRequest) -> Bill:
    if request.subtotal is None:
        raise ValueError("subtotal is required for calculation")
    return Bill(
        items=tuple(
            BillItem(id=item.id, name=item.name, total_price=item.total_price)
            for item in request.items
        ),
        discount=request.discount or 0,
        service_charge=request.service_charge or 0,
        tax=request.tax or 0,
    )


def _blocking_validation_messages(messages: list[str]) -> list[str]:
    """Keep printed-total discrepancies as warnings for calculation."""

    return [
        message
        for message in messages
        if not message.startswith("Printed total mismatch:")
        and message != "Printed total is missing."
    ]


@router.post("/validate", response_model=ValidationResponse)
def validate_endpoint(request: BillExtractionRequest) -> ValidationResponse:
    result = validate_bill(_validation_bill(request))
    return ValidationResponse(
        status=result.status,
        calculated_total=result.calculated_total,
        printed_total=result.printed_total,
        difference=result.difference,
        messages=result.messages,
    )


@router.post("/calculate", response_model=CalculateResponse)
def calculate_endpoint(request: CalculateRequest) -> CalculateResponse:
    validation = validate_bill(_validation_bill(request.bill))
    blocking_messages = _blocking_validation_messages(validation.messages)
    if blocking_messages:
        raise HTTPException(status_code=422, detail=blocking_messages)

    try:
        result = calculate_split(
            _calculator_bill(request.bill),
            request.people,
            request.assignments,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    people = {
        name: PersonBreakdownResponse(
            item_shares=breakdown.item_shares,
            subtotal=breakdown.subtotal,
            discount=breakdown.discount,
            service_charge=breakdown.service_charge,
            tax=breakdown.tax,
            total=breakdown.total,
        )
        for name, breakdown in result.people.items()
    }
    return CalculateResponse(
        people=people,
        bill_total=result.bill_total,
        allocated_total=result.allocated_total,
        difference=result.difference,
        validation=ValidationResponse(
            status=validation.status,
            calculated_total=validation.calculated_total,
            printed_total=validation.printed_total,
            difference=validation.difference,
            messages=validation.messages,
        ),
    )
