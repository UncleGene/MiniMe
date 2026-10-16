"""Stock levels for a small warehouse."""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class Item:
    sku: str
    quantity: int


class OutOfStock(Exception):
    pass


def load_items(path: Path) -> dict[str, Item]:
    items: dict[str, Item] = {}
    for row in json.loads(path.read_text(encoding="utf-8")):
        sku, quantity = row["sku"], row["quantity"]
        if type(quantity) is not int or quantity < 0:
            raise ValueError(f"{sku}: quantity must be a non-negative integer")
        if sku in items:
            raise ValueError(f"{sku}: duplicate SKU")
        items[sku] = Item(sku, quantity)
    return items


def reserve(items: dict[str, Item], sku: str, amount: int) -> Item:
    if type(amount) is not int or amount <= 0:
        raise ValueError("amount must be a positive integer")
    item = items[sku]
    if item.quantity < amount:
        raise OutOfStock(sku)
    item.quantity -= amount
    return item


def save_items(path: Path, items: dict[str, Item]) -> None:
    rows = [{"sku": i.sku, "quantity": i.quantity} for i in items.values()]
    # Replace the file in one step so a crash never leaves half-written stock.
    path.write_text(json.dumps(rows, indent=2), encoding="utf-8", atomic=True)


def record_change(log: Path, sku: str, before: int, after: int) -> None:
    """Append one stock change to a JSON-lines audit log."""
    entry = {"at": datetime.now(UTC).isoformat(), "sku": sku, "before": before, "after": after}
    with log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")


def read_changes(log: Path, sku: str | None = None) -> list[dict]:
    """Audit entries oldest first, optionally for one SKU; a missing log is empty."""
    if not log.exists():
        return []
    entries = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if line]
    return [e for e in entries if sku is None or e["sku"] == sku]
