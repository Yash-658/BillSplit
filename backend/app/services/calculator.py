"""Deterministic bill splitting using integer paise.

All monetary values accepted by this module are integer paise.  Remainders
are assigned by largest remainder, with the input order as the tie-breaker,
so every allocation is reproducible and reconciles exactly.
"""

from dataclasses import dataclass, field
from typing import Mapping, Sequence


@dataclass(frozen=True)
class BillItem:
    """A reviewed line item, with its total already expressed in paise."""

    id: str
    name: str
    total_price: int


@dataclass(frozen=True)
class Bill:
    """The reviewed monetary values used by the calculator."""

    items: tuple[BillItem, ...]
    discount: int = 0
    service_charge: int = 0
    tax: int = 0
    taxes: tuple[int, ...] = ()
    adjustment: int = 0

    @property
    def total_tax(self) -> int:
        """Return the combined tax, supporting both one and multiple taxes."""

        return self.tax + sum(self.taxes)


@dataclass
class PersonBreakdown:
    """Explainable amounts allocated to one person."""

    item_shares: dict[str, int] = field(default_factory=dict)
    subtotal: int = 0
    discount: int = 0
    service_charge: int = 0
    tax: int = 0
    adjustment: int = 0

    @property
    def total(self) -> int:
        return (
            self.subtotal
            - self.discount
            + self.service_charge
            + self.tax
            + self.adjustment
        )


@dataclass
class SplitResult:
    """The complete per-person calculation and reconciliation totals."""

    people: dict[str, PersonBreakdown]
    bill_total: int

    @property
    def allocated_total(self) -> int:
        return sum(person.total for person in self.people.values())

    @property
    def difference(self) -> int:
        return self.allocated_total - self.bill_total


def _validate_amount(name: str, amount: int) -> None:
    if not isinstance(amount, int) or isinstance(amount, bool) or amount < 0:
        raise ValueError(f"{name} must be a non-negative integer number of paise")


def _allocate(amount: int, weights: Sequence[int], labels: Sequence[str]) -> list[int]:
    """Allocate an amount proportionally, reconciling by largest remainder."""

    _validate_amount("amount", amount)
    if len(weights) != len(labels) or not labels:
        raise ValueError("weights and labels must contain the same non-empty entries")
    if any(not isinstance(weight, int) or weight < 0 for weight in weights):
        raise ValueError("allocation weights must be non-negative integers")

    total_weight = sum(weights)
    if total_weight == 0:
        raise ValueError("cannot allocate a positive amount without a positive basis")

    floors = [(amount * weight) // total_weight for weight in weights]
    remainder = amount - sum(floors)
    order = sorted(
        range(len(weights)),
        key=lambda index: (
            -((amount * weights[index]) % total_weight),
            index,
        ),
    )
    for index in order[:remainder]:
        floors[index] += 1
    return floors


def _allocate_signed(amount: int, weights: Sequence[int], labels: Sequence[str]) -> list[int]:
    """Allocate a signed amount while preserving exact reconciliation."""

    if amount >= 0:
        return _allocate(amount, weights, labels)
    return [-share for share in _allocate(-amount, weights, labels)]


def calculate_split(
    bill: Bill,
    people: Sequence[str],
    assignments: Mapping[str, Sequence[str] | str],
) -> SplitResult:
    """Calculate each person's exact share of a reviewed bill.

    A value of ``"everyone"`` (or a sequence containing it) assigns an item
    to every person.  All other assignment sequences are split equally.
    Discounts, service charge, and all taxes are allocated proportionally to
    each person's pre-adjustment item consumption.
    """

    person_names = list(people)
    if not person_names or len(set(person_names)) != len(person_names):
        raise ValueError("people must contain at least one unique name")
    if any(not isinstance(name, str) or not name for name in person_names):
        raise ValueError("people must contain non-empty names")

    for name in ("discount", "service_charge", "tax"):
        _validate_amount(name, getattr(bill, name))
    if not isinstance(bill.adjustment, int) or isinstance(bill.adjustment, bool):
        raise ValueError("adjustment must be an integer number of paise")
    for index, tax in enumerate(bill.taxes):
        _validate_amount(f"taxes[{index}]", tax)

    result_people = {name: PersonBreakdown() for name in person_names}
    person_set = set(person_names)
    item_ids = set()

    for item in bill.items:
        if item.id in item_ids:
            raise ValueError(f"duplicate item id: {item.id}")
        item_ids.add(item.id)
        _validate_amount(f"item {item.id} total_price", item.total_price)
        if item.id not in assignments:
            raise ValueError(f"missing assignment for item {item.id}")

        assigned = assignments[item.id]
        assigned_names = [assigned] if isinstance(assigned, str) else list(assigned)
        if not assigned_names or "everyone" in assigned_names:
            assigned_names = person_names if "everyone" in assigned_names else assigned_names
        if (
            not assigned_names
            or len(set(assigned_names)) != len(assigned_names)
            or any(name not in person_set for name in assigned_names)
        ):
            raise ValueError(f"invalid assignment for item {item.id}")

        shares = _allocate(item.total_price, [1] * len(assigned_names), assigned_names)
        for name, share in zip(assigned_names, shares):
            result_people[name].item_shares[item.id] = share
            result_people[name].subtotal += share

    if set(assignments) != item_ids:
        raise ValueError("assignments must contain exactly the bill item ids")

    consumption = [result_people[name].subtotal for name in person_names]
    total_consumption = sum(consumption)
    adjustments = [bill.discount, bill.service_charge, bill.total_tax, bill.adjustment]
    if total_consumption == 0 and any(adjustments):
        raise ValueError("cannot allocate bill adjustments without item consumption")
    if bill.discount > total_consumption:
        raise ValueError("discount cannot exceed total pre-discount item consumption")

    discount_shares = _allocate(bill.discount, consumption, person_names) if bill.discount else [0] * len(person_names)
    service_shares = _allocate(bill.service_charge, consumption, person_names) if bill.service_charge else [0] * len(person_names)
    tax_shares = _allocate(bill.total_tax, consumption, person_names) if bill.total_tax else [0] * len(person_names)
    adjustment_shares = (
        _allocate_signed(bill.adjustment, consumption, person_names)
        if bill.adjustment
        else [0] * len(person_names)
    )

    for index, name in enumerate(person_names):
        person = result_people[name]
        person.discount = discount_shares[index]
        person.service_charge = service_shares[index]
        person.tax = tax_shares[index]
        person.adjustment = adjustment_shares[index]

    bill_total = (
        total_consumption
        - bill.discount
        + bill.service_charge
        + bill.total_tax
        + bill.adjustment
    )
    return SplitResult(people=result_people, bill_total=bill_total)
