# Usage

## Adding notes

    notes add "buy milk" --tag errands

Prints the new note's id. Notes longer than 280 characters are rejected.

## Searching

    notes search milk

Matching ignores case, so `Milk` and `MILK` find the same notes.

## Exporting

    notes export --out notes.md

Writes one Markdown list item per note and prints how many were exported.
