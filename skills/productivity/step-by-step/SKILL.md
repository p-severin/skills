---
name: step-by-step
description: "Use when a task has two or more open decisions, trade-offs, or recommendations to walk through with the user, or when the user asks to go step by step."
metadata:
  version: "1.0.0"
---

# Step-by-Step Decisions

## Goal

Prevent walls of text by walking the user through two or more open decisions or recommendations one item at a time in plain language, using interactive choice prompts, until every item is resolved.

## Workflow

1. **Build and order the queue**
   - Resolve factual lookups from the codebase or environment yourself before asking the user.
   - List every remaining open decision or recommendation internally and place blocking decisions first (earlier choices often retire downstream questions and shorten the session).
   - **Done when**: every queued item requires user choice and items are ordered from highest impact to lowest.

2. **Ask one decision per turn**
   - Call the environment's interactive question tool (`AskUserQuestion`, `ask_question`, or equivalent) with **strictly 1 question per call**—batching multiple questions recreates the overload this skill prevents.
   - When the environment has no interactive question tool, send 1 short numbered question in plain text and wait for the reply.
   - Match the user's language and place all prompt content inside the tool call (with no separate chat preamble before it) within these bounds:
     - **Progress**: state queue position (`Decision 2/5`, or `Decision 2/~5` when downstream items depend on earlier answers).
     - **Explanation**: write 1–3 short sentences stating what is being decided and why it matters. Explain any unavoidable technical term in plain words on first use.
     - **Options**: provide 2–4 concrete approaches, put the recommended choice first prefixed with `(Recommended)`, and give a 1-sentence reason why.
   - **Done when**: the user selects an option, gives a custom answer, or skips the item.

3. **Handle interruptions and prune the queue**
   - If the user asks what a term or option means, answer in 1–3 plain sentences and re-ask the same decision without advancing the counter.
   - If the user asks to accept all remaining recommendations, apply the recommended default to every remaining item and move to Step 4.
   - After each answer, remove any queued item made moot by that choice and update the remaining count before asking the next item.
   - Repeat Steps 2–3 until the queue is empty.
   - **Done when**: zero unresolved items remain in the queue.

4. **Verify and summarize**
   - Check every criterion below before writing the summary:
     - Every queued decision or recommendation is resolved or explicitly skipped by the user.
     - Every turn asked strictly 1 question.
     - Every prompt included a progress indicator, 1–3 plain-language sentences, and 2–4 options with `(Recommended)` first.
   - If any decision was skipped silently or left ambiguous, return to Step 2 and resolve it first.
   - Output the settled decisions using the summary template below (1 line per decision), then proceed with the task.
   - **Done when**: every check passes, every settled decision appears in the summary, and execution continues.

## Example

One interactive step (the plain-text fallback uses the same fields):

```text
Decision 1/3: Where should we store user preferences?
Right now settings reset on every reload. Storing them locally keeps setup instant; a database syncs across devices.

- (Recommended) Browser local storage — zero backend changes and instant save on one device.
- Database table — syncs across devices, but requires a new API endpoint and migration.
- URL query parameters — shareable links, but cluttered URLs and no persistence across sessions.
```

Final summary after the last decision:

```text
Settled decisions:
1. Preference storage: Browser local storage
2. Theme default: Follow OS setting
3. Reset control: Single button in Settings
```

## Gotchas

- **Multi-question tool arrays**: interactive question tools accept a `questions` array; pass an array of length 1 on every call so the user decides one item at a time.
- **Jargon inside option labels**: simplifying the explanation while packing option labels with unexplained acronyms still breaks clarity; phrase option labels around concrete outcomes and keep labels short so tool UIs stay readable.
- **Single-decision requests**: when the user invokes this skill with only 1 open decision, ask it directly with 2–4 options and omit the `1/1` counter.
- **Silent assumptions**: include every choice that affects the outcome in the queue, and apply remaining recommendations automatically only after an explicit fast-forward from the user.
