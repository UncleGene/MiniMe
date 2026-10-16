import unittest
from decimal import Decimal

from inventory import Item
from reports import (ReorderRule, Suggestion, low_stock, needs_reorder, page, parse_rules,
                     suggestions, summary, to_csv, valuation)


class ReorderTests(unittest.TestCase):
    def test_rule_rejects_target_at_or_below_point(self):
        with self.assertRaises(ValueError):
            ReorderRule(point=5, target=5)

    def test_reorder_at_the_point(self):
        self.assertTrue(needs_reorder(Item("a", 5), ReorderRule(point=5, target=20)))
        self.assertFalse(needs_reorder(Item("a", 6), ReorderRule(point=5, target=20)))

    def test_suggestions_fill_to_target_and_skip_items_without_rules(self):
        items = {"b": Item("b", 2), "a": Item("a", 0), "c": Item("c", 1)}
        rules = {"a": ReorderRule(1, 10), "b": ReorderRule(3, 8)}
        self.assertEqual(suggestions(items, rules),
                         [Suggestion("a", 0, 10), Suggestion("b", 2, 6)])


class ValuationTests(unittest.TestCase):
    def test_value_rounds_to_cents_and_lists_missing_prices(self):
        items = {"a": Item("a", 3), "b": Item("b", 1)}
        result = valuation(items, {"a": Decimal("0.335")})
        self.assertEqual(result.units, 4)
        self.assertEqual(result.value, Decimal("1.01"))
        self.assertEqual(result.missing_prices, ("b",))


class ListingTests(unittest.TestCase):
    def test_low_stock_is_strictly_below_threshold_fewest_first(self):
        items = [Item("b", 1), Item("a", 1), Item("c", 3), Item("d", 0)]
        self.assertEqual([i.sku for i in low_stock(items, 3)], ["d", "a", "b"])

    def test_page_bounds(self):
        rows = [Suggestion(str(n), 0, 1) for n in range(5)]
        self.assertEqual([r.sku for r in page(rows, 2, 2)], ["2", "3"])
        self.assertEqual([r.sku for r in page(rows, 3, 2)], ["4"])
        self.assertEqual(page(rows, 4, 2), [])
        with self.assertRaises(ValueError):
            page(rows, 0, 2)

    def test_csv_has_header_and_rows(self):
        self.assertEqual(to_csv([Suggestion("a", 0, 10)]), "sku,on_hand,order\na,0,10\n")


class ParseRulesTests(unittest.TestCase):
    def test_parses_and_skips_comments(self):
        rules = parse_rules("# sku,point,target\n\na, 2, 10\n")
        self.assertEqual(rules, {"a": ReorderRule(2, 10)})

    def test_errors_name_the_line(self):
        for text, message in (("a,1\n", "line 1"), ("a,1,5\na,2,6\n", "line 2: duplicate"),
                              ("a,x,5\n", "line 1"), ("a,5,5\n", "line 1")):
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, message):
                parse_rules(text)


class SummaryTests(unittest.TestCase):
    def test_summary_lists_reorders(self):
        text = summary({"a": Item("a", 1)}, {"a": ReorderRule(2, 5)}, {"a": Decimal("2")})
        self.assertEqual(text, "Units on hand: 1\nStock value: 2.00\nReorder 1 SKUs:\n"
                               "  a: order 4 (on hand 1)")

    def test_summary_without_reorders(self):
        text = summary({"a": Item("a", 9)}, {}, {})
        self.assertIn("No price for: a", text)
        self.assertTrue(text.endswith("Nothing to reorder."))


if __name__ == "__main__":
    unittest.main()
