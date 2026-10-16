"""Stock reports: reorder suggestions, valuation, low-stock lists and CSV export."""
from __future__ import annotations

import csv
import io
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from inventory import Item

CENT = Decimal("0.01")


@dataclass(frozen=True)
class ReorderRule:
    """Reorder when stock is at or below `point`, up to `target` units."""

    point: int
    target: int

    def __post_init__(self) -> None:
        if type(self.point) is not int or type(self.target) is not int:
            raise ValueError("reorder point and target must be integers")
        if self.point < 0:
            raise ValueError("reorder point must not be negative")
        if self.target <= self.point:
            raise ValueError("reorder target must exceed the reorder point")


@dataclass(frozen=True)
class Suggestion:
    sku: str
    on_hand: int
    order: int


@dataclass(frozen=True)
class Valuation:
    units: int
    value: Decimal
    missing_prices: tuple[str, ...]


def needs_reorder(item: Item, rule: ReorderRule) -> bool:
    """Return True when the item is at or below its reorder point."""
    return item.quantity <= rule.point


def suggestions(items: Mapping[str, Item], rules: Mapping[str, ReorderRule]) -> list[Suggestion]:
    """Suggest an order for every item at or below its reorder point.

    Items without a rule are never reordered. The result is sorted by SKU so
    reports are stable between runs.
    """
    result = []
    for sku in sorted(items):
        rule = rules.get(sku)
        if rule is None:
            continue
        item = items[sku]
        if needs_reorder(item, rule):
            result.append(Suggestion(sku, item.quantity, rule.target - item.quantity))
    return result


def valuation(items: Mapping[str, Item], prices: Mapping[str, Decimal]) -> Valuation:
    """Total units and stock value; SKUs without a price are listed, not guessed.

    Raises ValueError for a price that is not a finite, non-negative amount.
    """
    units = 0
    value = Decimal("0")
    missing = []
    for sku in sorted(items):
        item = items[sku]
        units += item.quantity
        price = prices.get(sku)
        if price is None:
            missing.append(sku)
            continue
        if not price.is_finite() or price < 0:
            raise ValueError(f"{sku}: price must be a finite, non-negative amount")
        value += price * item.quantity
    return Valuation(units, value.quantize(CENT, rounding=ROUND_HALF_UP), tuple(missing))


def low_stock(items: Iterable[Item], threshold: int) -> list[Item]:
    """Items with fewer than `threshold` units, fewest first, ties by SKU."""
    if threshold < 0:
        raise ValueError("threshold must not be negative")
    return sorted((i for i in items if i.quantity < threshold), key=lambda i: (i.quantity, i.sku))


def page(rows: list[Suggestion], number: int, size: int) -> list[Suggestion]:
    """Return 1-based page `number` of `size` rows; an empty list past the end."""
    if number < 1 or size < 1:
        raise ValueError("page number and size must be positive")
    start = (number - 1) * size
    return rows[start:start + size]


def to_csv(suggested: Iterable[Suggestion]) -> str:
    """Render suggestions as CSV with a header row."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["sku", "on_hand", "order"])
    for suggestion in suggested:
        writer.writerow([suggestion.sku, suggestion.on_hand, suggestion.order])
    return buffer.getvalue()


def parse_rules(text: str) -> dict[str, ReorderRule]:
    """Parse `sku,point,target` lines; blank lines and `#` comments are skipped.

    Raises ValueError naming the line number for a malformed row or a
    duplicate SKU.
    """
    rules: dict[str, ReorderRule] = {}
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 3:
            raise ValueError(f"line {number}: expected sku,point,target")
        sku, point, target = parts
        if sku in rules:
            raise ValueError(f"line {number}: duplicate rule for {sku}")
        try:
            rules[sku] = ReorderRule(int(point), int(target))
        except ValueError as error:
            raise ValueError(f"line {number}: {error}") from error
    return rules


def summary(items: Mapping[str, Item], rules: Mapping[str, ReorderRule],
            prices: Mapping[str, Decimal]) -> str:
    """A short plain-text report for the daily stock email."""
    total = valuation(items, prices)
    suggested = suggestions(items, rules)
    lines = [f"Units on hand: {total.units}", f"Stock value: {total.value}"]
    if total.missing_prices:
        lines.append("No price for: " + ", ".join(total.missing_prices))
    if suggested:
        lines.append(f"Reorder {len(suggested)} SKUs:")
        lines.extend(f"  {s.sku}: order {s.order} (on hand {s.on_hand})" for s in suggested)
    else:
        lines.append("Nothing to reorder.")
    return "\n".join(lines)
