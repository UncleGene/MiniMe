import tempfile
import unittest
from pathlib import Path

import notes


class NotesTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.dir = Path(directory.name)
        self.store = self.dir / "notes.json"

    def test_add_assigns_ids_and_rejects_long_notes(self) -> None:
        self.assertEqual(notes.add(self.store, "one", None)["id"], 1)
        self.assertEqual(notes.add(self.store, "two", "x")["id"], 2)
        with self.assertRaises(ValueError):
            notes.add(self.store, "x" * (notes.MAX_LENGTH + 1), None)

    def test_search_ignores_case(self) -> None:
        notes.add(self.store, "Buy milk", None)
        notes.add(self.store, "call home", None)
        self.assertEqual([n["id"] for n in notes.search(self.store, "MILK")], [1])


if __name__ == "__main__":
    unittest.main()
