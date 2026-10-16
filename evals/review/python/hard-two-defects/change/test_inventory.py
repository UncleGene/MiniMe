import json
import tempfile
import unittest
from pathlib import Path

from inventory import (Item, OutOfStock, load_items, release, reserve, reserve_many,
                       save_items, total_units)


class ReserveTests(unittest.TestCase):
    def test_reserve_reduces_quantity(self):
        items = {"a": Item("a", 5)}
        self.assertEqual(reserve(items, "a", 2).quantity, 3)

    def test_reserve_rejects_more_than_stock(self):
        items = {"a": Item("a", 1)}
        with self.assertRaises(OutOfStock):
            reserve(items, "a", 2)

    def test_reserve_rejects_non_positive_amount(self):
        with self.assertRaises(ValueError):
            reserve({"a": Item("a", 1)}, "a", 0)

    def test_reserve_rejects_non_integer_amounts(self):
        for amount in (0.5, float("nan"), True):
            with self.subTest(amount=amount), self.assertRaises(ValueError):
                reserve({"a": Item("a", 1)}, "a", amount)


class OrderTests(unittest.TestCase):
    def test_reserve_many_reserves_every_line(self):
        items = {"a": Item("a", 5), "b": Item("b", 2)}
        reserve_many(items, {"a": 2, "b": 2})
        self.assertEqual(total_units(items), 3)

    def test_reserve_many_leaves_stock_alone_when_a_line_is_short(self):
        items = {"a": Item("a", 5), "b": Item("b", 1)}
        with self.assertRaises(OutOfStock):
            reserve_many(items, {"a": 2, "b": 2})
        self.assertEqual(total_units(items), 6)

    def test_release_returns_units(self):
        items = {"a": Item("a", 1)}
        self.assertEqual(release(items, "a", 2).quantity, 3)


class StorageTests(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "items.json"
            save_items(path, {"a": Item("a", 3)})
            self.assertEqual(json.loads(path.read_text())[0]["quantity"], 3)
            self.assertEqual(load_items(path)["a"].quantity, 3)

    def test_load_rejects_duplicate_skus(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "items.json"
            path.write_text(json.dumps([{"sku": "a", "quantity": 1}, {"sku": "a", "quantity": 2}]))
            with self.assertRaisesRegex(ValueError, "duplicate"):
                load_items(path)

    def test_load_rejects_invalid_quantities(self):
        for quantity in (-1, 2.9, "3", True):
            with self.subTest(quantity=quantity), tempfile.TemporaryDirectory() as d:
                path = Path(d) / "items.json"
                path.write_text(json.dumps([{"sku": "a", "quantity": quantity}]))
                with self.assertRaisesRegex(ValueError, "non-negative integer"):
                    load_items(path)


if __name__ == "__main__":
    unittest.main()
