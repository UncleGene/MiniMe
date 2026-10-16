"""Stock levels for a small warehouse."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Item:
    sku: str
    quantity: int


MAX_ORDER = 1000


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
    if amount > MAX_ORDER:
        raise ValueError(f"orders are limited to {MAX_ORDER} units")
    item = items[sku]
    if item.quantity < amount:
        raise OutOfStock(sku)
    item.quantity -= amount
    return item


def save_items(path: Path, items: dict[str, Item]) -> None:
    rows = [{"sku": i.sku, "quantity": i.quantity} for i in items.values()]
    path.write_text(json.dumps(rows, indent=2), encoding="utf-8")
