#!/usr/bin/env python3
"""notes: keep short notes in a JSON file."""
import argparse
import json
from pathlib import Path

DEFAULT_STORE = Path.home() / ".notes.json"
MAX_LENGTH = 280


def load(store: Path) -> list[dict]:
    if not store.exists():
        return []
    return json.loads(store.read_text(encoding="utf-8"))


def save(store: Path, notes: list[dict]) -> None:
    store.write_text(json.dumps(notes, indent=2), encoding="utf-8")


def add(store: Path, text: str, tag: str | None) -> dict:
    if len(text) > MAX_LENGTH:
        raise ValueError(f"note longer than {MAX_LENGTH} characters")
    notes = load(store)
    note = {"id": len(notes) + 1, "text": text, "tag": tag}
    notes.append(note)
    save(store, notes)
    return note


def search(store: Path, term: str) -> list[dict]:
    return [note for note in load(store) if term.lower() in note["text"].lower()]


def export(store: Path, out: Path) -> int:
    notes = load(store)
    out.write_text("".join(f"- {note['text']}\n" for note in notes), encoding="utf-8")
    return len(notes)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="notes")
    parser.add_argument("--store", type=Path, default=DEFAULT_STORE)
    sub = parser.add_subparsers(dest="command", required=True)
    add_parser = sub.add_parser("add")
    add_parser.add_argument("text")
    add_parser.add_argument("--label", dest="tag")
    search_parser = sub.add_parser("search")
    search_parser.add_argument("term")
    export_parser = sub.add_parser("export")
    export_parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "add":
        print(add(args.store, args.text, args.tag)["id"])
    elif args.command == "search":
        for note in search(args.store, args.term):
            print(f"{note['id']}: {note['text']}")
    else:
        print(f"exported {export(args.store, args.out)} notes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
