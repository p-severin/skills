---
name: skill-create
description: "Use when creating a new agent skill from notes, links, a real task, or project artifacts."
disable-model-invocation: true
metadata:
  version: "1.0.1"
---

# Create Skill

## Goal

Turn concrete domain expertise (brain dumps, notes, links, real task traces, or project artifacts) into a narrow, strict, verified skill that measurably outperforms unassisted agent defaults on one problem.

## Workflow

Follow these steps in order. Do not skip a gate.

### 1. Collect real source material

Refuse generic from-scratch generation. Gather the user's brain dump, notes, links, task conversation, corrections, or project artifacts (runbooks, specs, PR comments, git patches, incident logs). If the user supplies only a topic name with no material or failure examples, ask for real source material or a failed run before drafting.

- **Done when**: every planned rule traces to a user-supplied source, correction, or concrete failure mode.

### 2. Run the Value Gate

Before designing any file, answer: *Would an unassisted agent get this wrong without the skill?*

- If the model already handles the task reliably by default, or the material contains only generic advice, stop and recommend **not creating a skill**.
- If the request covers multiple independent aspects or mixes creation with review/auditing, propose splitting into separate narrow skills (one problem per skill) and confirm which single skill to build first.

- **Done when**: you can state at least one concrete failure mode the skill prevents, and the skill owns exactly one goal.

### 3. Align requirements and architecture (grill-me)

Read `references/standards.md`. Resolve facts from the source material and workspace yourself, then run a short grill-me interview before drafting to close every open user decision (invoke the `grilling` skill if available; otherwise ask one decision at a time with a recommended answer):

- **Goal**: lock a 1–2 sentence `## Goal` naming the exact problem and verifiable outcome.
- **Thresholds and rules**: replace every ambiguous preference in the brain dump with a concrete threshold, default, or decision branch.
- **Invocation**: set `disable-model-invocation: true` by default; omit it only when the agent or another skill must trigger this skill autonomously.
- **Verification**: define how the skill verifies its own output against `## Goal`. Prefer a deterministic validator script in `scripts/` whenever mechanical checks, schema validation, or repeatable transformations exist; otherwise define a checkable validation loop.
- **Disclosure**: apply the branching test—keep inline only what every run needs; place branch-specific reference in `references/`, long templates in `assets/`, and deterministic logic in `scripts/`.
- Read `references/patterns.md` when deciding whether to bundle a script, checklist, plan-validate-execute flow, or router skill.
- Read `references/repo-conventions.md` when creating the skill inside a catalog repository that has `scripts/check-repo.py`.

Skip questions whose answers are already explicit and unambiguous in the user's input. Never draft `SKILL.md` until the user confirms shared understanding of every open decision.

- **Done when**: the user has confirmed `## Goal`, concrete rules/thresholds, invocation mode, verification method, and file layout with zero open decisions left.

### 4. Draft and deliberately generalize

Write `SKILL.md` and any supporting files strictly following `references/standards.md`:

- Start `SKILL.md` with `## Goal`, followed by ordered steps with checkable, demanding completion criteria.
- Generalize purposefully: when extracting from a single chat or repository, strip one-off file paths, names, and data so the procedure solves the whole class of task.
- Replace every vague phrase with concrete numbers, thresholds, or explicit decision trees.
- Explain the short *why* behind non-obvious rules so the agent handles uncovered cases accurately.
- Include an inline `## Gotchas` section for non-obvious traps and a concrete output template when output shape matters.
- Include the skill's own verification step so each execution checks whether it satisfied `## Goal`.

- **Done when**: the draft implements the full `## Goal`, contains an explicit self-verification step, and has zero generic filler.

### 5. Prune and validate

Run the mandatory pruning pass and deterministic validation loop:

1. Apply every pruning rule in `references/standards.md` sentence by sentence: delete whole no-op sentences, remove duplication, strip one-command environment lookups, and verify every pointer states its loading condition.
2. Run the deterministic linter `scripts/lint_skill.py` from this skill's directory:
   ```bash
   python3 scripts/lint_skill.py <path-to-new-skill>
   ```
3. When inside this repository, update catalog files per `references/repo-conventions.md` and run `python3 scripts/check-repo.py`.
4. Fix every `ERROR` and resolve or explicitly justify every `WARN`, then re-run until clean.

- **Done when**: `lint_skill.py` exits `0` with zero unresolved errors, repo checks pass (when applicable), and you hand off the created files plus a concrete prompt for verifying value against a no-skill baseline via `../skill-refine/SKILL.md`.

## Gotchas

- Drafting from a single prompt produces verbose prose that explains basics the model already knows; the pruning pass should delete aggressively rather than reword for style.
- Extracting a skill straight from one solved task overfits to that repository's exact files and schemas; always run an explicit generalization pass.
- A skill without a checkable way to verify `## Goal` cannot prove it beats the unassisted agent; if you cannot define how to verify it, stop at the Value Gate.
- Generic references like `see references/` fail to trigger reliably; every pointer must name the exact file and the exact condition for loading it.

## References

- Read `references/standards.md` before designing or drafting any skill.
- Read `references/patterns.md` when choosing optional patterns (deterministic scripts, checklists, plan-validate-execute, router skills).
- Read `references/repo-conventions.md` when creating a skill inside a repository with `scripts/check-repo.py`.
