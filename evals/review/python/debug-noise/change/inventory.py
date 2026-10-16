"""Stock levels for a small warehouse."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Item:
    sku: str
    quantity: int


class OutOfStock(Exception):
    pass


def load_items(path: Path) -> dict[str, Item]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {row["sku"]: Item(row["sku"], int(row["quantity"])) for row in data}


def reserve(items: dict[str, Item], sku: str, amount: int) -> Item:
    if amount <= 0:
        raise ValueError("amount must be positive")
    item = items[sku]
    if item.quantity < amount:
        raise OutOfStock(sku)
    # Subtract the amount from the quantity
    item.quantity -= amount
    print("DEBUG reserve", sku, item.quantity)
    return item


def save_items(path: Path, items: dict[str, Item]) -> None:
    rows = [{"sku": i.sku, "quantity": i.quantity} for i in items.values()]
    path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
