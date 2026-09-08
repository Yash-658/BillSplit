import pytest

from backend.app.services.calculator import Bill, BillItem, calculate_split


def item(item_id: str, total: int) -> BillItem:
    return BillItem(id=item_id, name=item_id, total_price=total)


def test_single_person_item():
    result = calculate_split(Bill((item("meal", 10000),)), ["Yash"], {"meal": ["Yash"]})
    assert result.people["Yash"].subtotal == 10000
    assert result.people["Yash"].total == 10000
    assert result.difference == 0


def test_shared_item_and_everyone_assignment():
    bill = Bill((item("shared", 10001), item("everyone", 20000)))
    result = calculate_split(
        bill,
        ["Yash", "Rahul", "Aman"],
        {"shared": ["Yash", "Rahul"], "everyone": "everyone"},
    )
    assert [result.people[name].subtotal for name in ["Yash", "Rahul", "Aman"]] == [11668, 11667, 6666]
    assert result.allocated_total == 30001


def test_proportional_tax_service_charge_and_discount():
    bill = Bill(
        (item("yash", 50000), item("rahul", 30000), item("aman", 20000)),
        discount=10000,
        service_charge=10000,
        tax=18000,
    )
    result = calculate_split(
        bill,
        ["Yash", "Rahul", "Aman"],
        {"yash": ["Yash"], "rahul": ["Rahul"], "aman": ["Aman"]},
    )
    assert [(result.people[name].discount, result.people[name].service_charge, result.people[name].tax)
            for name in ["Yash", "Rahul", "Aman"]] == [(5000, 5000, 9000), (3000, 3000, 5400), (2000, 2000, 3600)]
    assert result.allocated_total == result.bill_total == 118000


def test_multiple_taxes_zero_adjustments_and_remainder():
    bill = Bill((item("meal", 10001),), taxes=(1, 2))
    result = calculate_split(bill, ["A", "B"], {"meal": ["A", "B"]})
    assert [result.people[name].total for name in ["A", "B"]] == [5003, 5001]
    assert result.bill_total == result.allocated_total == 10004


def test_rejects_missing_or_invalid_assignments():
    with pytest.raises(ValueError, match="missing assignment"):
        calculate_split(Bill((item("meal", 100),)), ["A"], {})
    with pytest.raises(ValueError, match="invalid assignment"):
        calculate_split(Bill((item("meal", 100),)), ["A"], {"meal": ["B"]})
