"""Stock levels for a small warehouse."""
from __future__ import annotations

import functools
import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Item:
    sku: str
    quantity: int


class OutOfStock(Exception):
    pass


@functools.cache
def load_items(path: Path) -> dict[str, Item]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {row["sku"]: Item(row["sku"], int(row["quantity"])) for row in data}


def reserve(items: dict[str, Item], sku: str, amount: int) -> Item:
    if amount <= 0:
        raise ValueError("amount must be positive")
    item = items[sku]
    if item.quantity < amount:
        raise OutOfStock(sku)
    item.quantity -= amount
    return item


def reserve_many(items: dict[str, Item], order: Mapping[str, int]) -> list[Item]:
    """Reserve every line of an order, or none of them if any line fails."""
    for sku, amount in order.items():
        if items[sku].quantity < amount:
            raise OutOfStock(sku)
    return [reserve(items, sku, amount) for sku, amount in order.items()]


def release(items: dict[str, Item], sku: str, amount: int) -> Item:
    """Return reserved units to stock, for a cancelled order."""
    if amount <= 0:
        raise ValueError("amount must be positive")
    item = items[sku]
    item.quantity += amount
    return item


def total_units(items: Mapping[str, Item]) -> int:
    return sum(item.quantity for item in items.values())


def save_items(path: Path, items: dict[str, Item]) -> None:
    rows = [{"sku": i.sku, "quantity": i.quantity} for i in items.values()]
    path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
