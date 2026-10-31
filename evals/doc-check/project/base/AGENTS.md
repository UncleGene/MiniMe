# notes agent guide

- Code is in `notes.py` and tests are in `test_notes.py`.
- Run `scripts/check` before every commit.
- The store is a JSON list of `{id, text, tag}` objects. Keep it readable by
  older versions: never rename or remove a field.
