from backend.app.services.validation import (
    ValidationBill,
    ValidationItem,
    validate_bill,
)


def bill(
    *,
    items=(ValidationItem("meal", "Meal", 2, 5000, 10000),),
    subtotal=10000,
    discount=None,
    service_charge=None,
    tax=None,
    printed_total=10000,
):
    return ValidationBill(
        items=items,
        subtotal=subtotal,
        discount=discount,
        service_charge=service_charge,
        tax=tax,
        printed_total=printed_total,
    )


def test_valid_bill():
    result = validate_bill(bill())
    assert result.status == "valid"
    assert result.calculated_total == 10000
    assert result.printed_total == 10000
    assert result.difference == 0
    assert result.messages == []


def test_item_quantity_price_mismatch():
    result = validate_bill(
        bill(items=(ValidationItem("meal", "Meal", 3, 5000, 10000),))
    )
    assert result.status == "warning"
    assert any("total mismatch" in message for message in result.messages)


def test_subtotal_mismatch():
    result = validate_bill(bill(subtotal=9000, printed_total=9000))
    assert result.status == "warning"
    assert any("Subtotal mismatch" in message for message in result.messages)


def test_incorrect_printed_total():
    result = validate_bill(bill(printed_total=12500))
    assert result.status == "warning"
    assert result.calculated_total == 10000
    assert result.difference == 2500
    assert any("Printed total mismatch" in message for message in result.messages)


def test_correct_printed_total():
    result = validate_bill(bill(printed_total=10000))
    assert result.difference == 0
    assert result.status == "valid"


def test_discount_is_included():
    result = validate_bill(bill(discount=1000, printed_total=9000))
    assert result.calculated_total == 9000
    assert result.status == "valid"


def test_service_charge_is_included():
    result = validate_bill(bill(service_charge=1000, printed_total=11000))
    assert result.calculated_total == 11000
    assert result.status == "valid"


def test_tax_is_included():
    result = validate_bill(bill(tax=1800, printed_total=11800))
    assert result.calculated_total == 11800
    assert result.status == "valid"


def test_missing_optional_values_default_safely():
    result = validate_bill(
        ValidationBill(
            items=(ValidationItem("meal", "Meal", 1, 10000, 10000),),
            subtotal=10000,
        )
    )
    assert result.calculated_total == 10000
    assert result.printed_total is None
    assert result.difference is None
    assert result.status == "warning"
    assert any("Printed total is missing" in message for message in result.messages)
