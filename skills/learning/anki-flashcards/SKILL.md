---
name: anki-flashcards
description: "Use when the user wants flashcards from text, a file, or a URL, or wants those cards as an Anki .apkg deck."
disable-model-invocation: true
metadata:
  version: "1.0.0"
---

# Anki flashcards

Write one fact per card, then build an Anki `.apkg` when the user wants a deck. Formulation rules live in [card rules](references/card-rules.md). The converter lives in [export](references/export.md).

## Pick the input

Text, a file, or a URL means write cards. JSON that already has a `cards` list means export. A source plus a request for an Anki deck means write the cards, then export.

Do not depend on a named host tool to ask a question. Use the question tool this agent already has. Fetch a file or a URL only with `scripts/fetch_text.py`.

## Set the language

Default to Polish (`pl`). An explicit language, or `--lang`, wins. Use `--lang source` only when the user wants the source language.

Write `question`, `answer`, `explanation`, and `mnemonic` in the selected language. `topic` and `context` may stay English so filters stay stable. Keep `source_detail` in the source heading's own wording.

The samples in [examples](references/examples.md) use English placeholders. The card fields still follow the selected language.

## Generate cards

### Read the source

1. A file path starts with `/`, `./`, `~`, or a file extension. Run `python3 scripts/fetch_text.py PATH` and use stdout. The script reads text and HTML. For a PDF it uses `pdftotext` or `pypdf` when one of those is available.
2. A URL starts with `http://` or `https://`. Run `python3 scripts/fetch_text.py URL` and use stdout. Do not fetch the page another way.
3. Any other input is raw text. Use it as the source.
4. JSON with a `cards` list skips this section. Export that file.

For a PDF longer than 10 pages, ask which pages to keep, then drop the other pages from the extracted text. The script has no page argument.

### Show a learning path when the source is large

For a short, unambiguous source that will likely produce 10 cards or fewer, skip the outline and write the cards.

For a URL, a PDF, long text, an unclear scope, or a set likely to pass 10 cards, show this outline and wait.

```text
## Learning Path

Found N concepts, ordered from basics to advanced:

1. **[Concept A]** (P1) - X cards
   - atomic: definition of A
   - reverse: what produces A

2. **[Concept B]** (P1) - X cards
   Similar to Concept A. The cards name the difference.
   - comparison: B vs A

**Depth: medium | Language: pl | ~N cards (P1: X, P2: Y, P3: Z)**

Proceed? Or adjust?
```

Ask for approval, including a language change. A full sample is in [examples](references/examples.md). That file calls the outline Phase 1 and the JSON Phase 2.

Depth is `--depth low`, `--depth medium`, or `--depth high`. The default is medium. What each depth includes is in [card rules](references/card-rules.md).

### Write the JSON

Read [card rules](references/card-rules.md) before you write a card. Read [examples](references/examples.md) when one answer might hold two facts, when the cards drift, or when the user asks for an example.

Number `id` from basics to advanced. Every card needs a non-empty `answer`. If you filled a missing answer, add this line after the JSON.

```text
Fixed N cards missing answers before output.
```

## Export a deck

Export when the user asks for Anki, an `.apkg`, a deck, or an import.

1. Confirm `cards` is a non-empty list and each card has `question` and `answer`.
2. Run `scripts/json_to_apkg.py` from this skill directory.
3. If `genanki` is missing, install it in the active Python environment only after the project context is clear.
4. Convert the file.

```bash
python3 scripts/json_to_apkg.py input.json
python3 scripts/json_to_apkg.py input.json --deck "Deck Name" --output output.apkg
```

5. Report the `.apkg` path, the deck name, the card count, and any warning the script prints.

The script derives a stable GUID from the question text, so a later import updates that card instead of adding a second copy. Tags, note fields, and the template files are in [export](references/export.md).

## Boundaries

- Do not invent cards when the JSON is empty or malformed. Ask whether to generate them from the source.
- Do not hand-edit the `.apkg`. Change the JSON or `scripts/json_to_apkg.py`.
- Do not edit `assets/` unless the user asks for a different card look.
- The card `style` field is a wording style. It is not CSS.
