# notes

A small command-line tool that keeps short notes in a JSON file.

## Commands

notes has three commands:

- `notes add <text> [--tag <tag>]` stores a note and prints its id.
- `notes search <term>` prints the notes that contain the term, ignoring case.
- `notes export --out <file>` writes every note to a Markdown list.

Notes are stored in `~/.notes.json`; pass `--store <path>` to use another file.
A note may be at most 500 characters.

## Development

Run `scripts/check` before committing. See [usage](docs/usage.md) for examples.
