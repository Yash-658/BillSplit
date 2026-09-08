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


def test_positive_adjustment_is_allocated_and_reconciled():
    bill = Bill((item("meal", 10001),), adjustment=3)
    result = calculate_split(bill, ["A", "B"], {"meal": ["A", "B"]})
    assert [result.people[name].adjustment for name in ["A", "B"]] == [2, 1]
    assert result.bill_total == result.allocated_total == 10004


def test_negative_adjustment_is_allocated_and_reconciled():
    bill = Bill((item("meal", 10001),), adjustment=-3)
    result = calculate_split(bill, ["A", "B"], {"meal": ["A", "B"]})
    assert [result.people[name].adjustment for name in ["A", "B"]] == [-2, -1]
    assert result.bill_total == result.allocated_total == 9998


def test_missing_adjustment_defaults_to_zero():
    bill = Bill((item("meal", 10000),))
    result = calculate_split(bill, ["A", "B"], {"meal": ["A", "B"]})
    assert [result.people[name].adjustment for name in ["A", "B"]] == [0, 0]
    assert result.bill_total == result.allocated_total == 10000


def test_rejects_missing_or_invalid_assignments():
    with pytest.raises(ValueError, match="missing assignment"):
        calculate_split(Bill((item("meal", 100),)), ["A"], {})
    with pytest.raises(ValueError, match="invalid assignment"):
        calculate_split(Bill((item("meal", 100),)), ["A"], {"meal": ["B"]})


def test_discount_equal_to_total_consumption():
    bill = Bill((item("meal", 10001),), discount=10001)
    result = calculate_split(bill, ["A", "B"], {"meal": ["A", "B"]})
    assert [result.people[name].discount for name in ["A", "B"]] == [5001, 5000]
    assert result.allocated_total == result.bill_total == 0


def test_discount_greater_than_total_consumption_is_rejected():
    bill = Bill((item("meal", 100),), discount=101)
    with pytest.raises(ValueError, match="discount cannot exceed total pre-discount item consumption"):
        calculate_split(bill, ["A"], {"meal": ["A"]})


def test_uneven_three_person_remainder_allocation():
    bill = Bill((item("meal", 10001),))
    result = calculate_split(bill, ["A", "B", "C"], {"meal": ["A", "B", "C"]})
    assert [result.people[name].subtotal for name in ["A", "B", "C"]] == [3334, 3334, 3333]
    assert result.allocated_total == result.bill_total == 10001


def test_positive_adjustments_with_zero_consumption_are_rejected():
    bill = Bill((), discount=1, service_charge=1, tax=1)
    with pytest.raises(ValueError, match="without item consumption"):
        calculate_split(bill, ["A"], {})


def test_duplicate_people_are_rejected():
    with pytest.raises(ValueError, match="unique name"):
        calculate_split(Bill((item("meal", 100),)), ["A", "A"], {"meal": ["A"]})


def test_duplicate_item_ids_are_rejected():
    bill = Bill((item("meal", 100), item("meal", 200)))
    with pytest.raises(ValueError, match="duplicate item id"):
        calculate_split(bill, ["A"], {"meal": ["A"]})
