import json
import tempfile
import unittest
from pathlib import Path

from inventory import MAX_ORDER, Item, OutOfStock, load_items, reserve, save_items


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

    def test_reserve_rejects_orders_over_the_limit(self):
        with self.assertRaises(Exception):
            reserve({"a": Item("a", 5)}, "a", MAX_ORDER + 1)


class StorageTests(unittest.TestCase):
    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "items.json"
            save_items(path, {"a": Item("a", 3)})
            self.assertEqual(json.loads(path.read_text())[0]["quantity"], 3)
            self.assertEqual(load_items(path)["a"].quantity, 3)


if __name__ == "__main__":
    unittest.main()
