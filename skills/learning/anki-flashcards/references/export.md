# Export

`scripts/json_to_apkg.py` writes an Anki `.apkg` with `genanki`. Run it from the skill directory, as `SKILL.md` describes.

## Identifiers

The note GUID is `genanki.guid_for` of the question text. A card with no question uses `card_<id>` instead. The same question keeps the same GUID, so a re-import updates the note.

The model id is the first 8 hex digits of the MD5 of `model_glass_v5_` plus the deck name, read as an integer. The deck id uses the same truncation on `deck_` plus the deck name.

The deck name is `--deck` when that flag is set. Otherwise it is the JSON `topic`, or `Flashcards` when `topic` is missing.

The output path is `--output` when that flag is set. Otherwise it is the JSON path with the extension replaced by `.apkg`.

An empty `cards` list exits with status 1 and writes no package.

## Note fields

| Field | Source |
| --- | --- |
| Question | `question`, with backtick spans turned into `<code>` |
| Answer | `answer`, with the same code conversion |
| Meta | `context`, with surrounding `[]` and spaces removed |
| Extra | `mnemonic`, with the same code conversion |
| Explanation | `explanation`, with the same code conversion |

## Tags

The script adds a tag for each present value.

- `tier::<tier>`
- `type::<type>`
- `priority::<priority>`
- `topic::<topic>`

Spaces in the topic become underscores. `&` becomes `and`.

## Template files

| File | Role |
| --- | --- |
| `assets/front.html` | Question side. Shows `Meta` and `Question`. |
| `assets/back.html` | Answer side. Shows `Meta`, `Question`, `Answer`, `Explanation`, and `Extra`. |
| `assets/card.css` | Card CSS, including the glass layout. |

Leave these files unchanged unless the user asks for a different card look.
