# Card rules

Read this file before writing cards. The steps that produce the source text and the `.apkg` stay in `SKILL.md`.

## Contents

- Card types
- Wording styles
- Fields
- JSON shape
- Quality rules
- Depth

## Card types

| Type | Tier | Purpose |
| --- | --- | --- |
| Atomic | Foundational | One fact or definition. Question shape: what is X? |
| Conceptual | Intermediate | Why or how something works. Question shape: why does X happen? |
| Comparison | Intermediate | Distinguish exactly two similar concepts. Never compare three or more on one card. Split that into pairs. |
| Reverse | Any | The same fact in the other direction. Active asks what X does. Passive asks what achieves Y. |
| Application | Advanced | A realistic situation. Question shape: how would you use X to do this? |
| Synthesis | Advanced | A choice. Question shape: when would you choose X over Y? |

## Wording styles

`style` is the learning style of the wording. It is not a visual theme. Do not generate Anki CSS, note templates, fonts, colors, or deck styling unless the user asks for a different card look.

| Style | Use when | Shape |
| --- | --- | --- |
| `minimal` | Default for atomic and reverse facts | Direct recall, shortest wording that still answers |
| `contrastive` | Two concepts are easy to confuse | Names both concepts and tests the difference |
| `scenario` | Application or synthesis card | A concrete situation, and the learner chooses an action |
| `consequence` | A failure mode or a surprising outcome matters | Question shape: what happens if X fails? |
| `mnemonic` | An abstract concept is hard to picture | Include a `mnemonic` field |

Default to `minimal`. Use `contrastive` when two cards could be confused. Use `scenario` only when the question contains enough context to answer without guessing.

## Fields

| Field | Required | Role |
| --- | --- | --- |
| `id` | yes | Sequential, in learning-path order |
| `tier` | yes | `foundational`, `intermediate`, or `advanced` |
| `type` | yes | `atomic`, `conceptual`, `comparison`, `reverse`, `application`, or `synthesis` |
| `style` | yes | `minimal`, `contrastive`, `scenario`, `consequence`, or `mnemonic` |
| `priority` | yes | `P1` must-know, `P2` should-know, or `P3` nice-to-know |
| `question` | yes | The question |
| `answer` | yes | 5 to 15 words, hard max about 20 words. A list of distinct items is HTML: `"<ul><li>item1</li><li>item2</li></ul>"`. A comma-separated phrase that reads as one unit stays one phrase. |
| `explanation` | no | 1 to 3 sentences of context, mechanism, or a common trap |
| `context` | when needed | A topic tag when the question is ambiguous without it, such as `[Networking]` |
| `source_detail` | when needed | A section or heading when the source has that structure |
| `mnemonic` | when needed | An image, analogy, or memory hook for an abstract concept |
| `related` | no | Ids of cards that are pairs, prerequisites, comparisons, or easy to confuse |

## JSON shape

```json
{
  "topic": "Topic name derived from content",
  "source": "file path | URL | pasted text",
  "language": "pl",
  "cards": [
    {
      "id": 1,
      "tier": "foundational",
      "type": "atomic",
      "style": "minimal",
      "priority": "P1",
      "question": "What is [concept]?",
      "answer": "Concise definition.",
      "explanation": "Optional elaboration of the answer.",
      "context": "[Topic area]",
      "source_detail": "Section 2.1",
      "mnemonic": "Think of X as...",
      "related": [2, 5]
    }
  ],
  "stats": {
    "total": 15,
    "by_tier": { "foundational": 6, "intermediate": 5, "advanced": 4 },
    "by_priority": { "P1": 7, "P2": 5, "P3": 3 }
  }
}
```

`source` is a file path, a URL, or the words `pasted text`.

## Quality rules

Always apply these rules.

1. One fact per card. If the answer contains "and", a list, or more than one sentence, split it. If you need more than about 20 words, the card tests too much.
2. Split a concept that has several parts. "X has 3 parts: A, B, and C" becomes one card per part, plus an optional card for the count. A three-way comparison becomes one card per item plus pairwise cards.
3. Before you keep a card, ask whether the answer holds two facts that could be tested apart. If it does, split it.
4. Strip filler from the answer. Prefer a fragment. Write "CSS's conflict-resolution mechanism." Do not write "The cascade is the mechanism CSS uses to resolve conflicts."
5. When two concepts are easy to confuse, add a distinguishing context, a contrast, or an explicit comparison card.
6. For a key fact, add the reverse card when the selected depth asks for it. Same fact, other direction.
7. Use surprising facts, real consequences ("What happens if X fails?"), and dramatic examples. Engage emotions - a card that makes you feel something is easier to remember.
8. Foundational cards come before cards that depend on them. The sequence should teach someone who is new to the source.

Apply these when they fit the card.

9. For an abstract concept, add `mnemonic`.
10. Add `explanation` on foundational and conceptual cards when the answer alone is opaque. Skip it when the answer is enough, including most reverse and application cards.
11. Add `context` when the question is ambiguous without the topic.
12. Add `source_detail` when the source has a clear section or heading.

Use these rarely.

13. For a fact that goes stale (a version, a statistic, a policy), start the answer with "As of [year]:".
14. Ask for recall. Do not write a multiple-choice question.

## Depth

The user sets depth with `--depth low`, `--depth medium`, or `--depth high`. The default is medium.

| Depth | Coverage | Reverse cards |
| --- | --- | --- |
| low | P1 concepts only | Only the most critical P1 facts |
| medium | P1 and P2 concepts, plus comparison cards where confusion is likely | P1 facts |
| high | All priorities, more than one angle on each P1 fact, mnemonics for abstract concepts, and thorough contrast cards | P1 and P2 facts |

Let the source and the depth set the count. Depth does not map to a fixed range. A small topic at medium depth might be 8 cards. A dense topic at medium depth might be 40.
