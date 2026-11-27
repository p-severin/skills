---
name: skill-refine
description: "Use when auditing, testing, or improving an existing agent skill from feedback, traces, or a no-skill baseline."
disable-model-invocation: true
metadata:
  version: "1.0.1"
---

# Refine Skill

## Goal

Verify whether an existing skill measurably achieves its `## Goal` better than an unassisted agent, diagnose every defect or wasted token, and refine—or retire—the skill with user approval.

## Critical Stance

Challenge the status quo—including `## Goal`, scope, invocation mode, deterministic tooling, or the skill's existence—whenever you identify a concretely superior alternative. Never challenge for its own sake: state both the observed defect and the better alternative, and wait for user approval before changing `## Goal`, splitting, or deleting the skill.

## Workflow

Select Mode A when the user supplies feedback, a trace, or an existing skill to audit. Select Mode B when the user wants to test a skill on real prompts or verify that it adds value over no skill.

### 1. Inspect target and run deterministic lint

Read `../skill-create/references/standards.md` and every file inside the target skill directory. Run `../skill-create/scripts/lint_skill.py` before judging prose subjectively:

```bash
python3 ../skill-create/scripts/lint_skill.py <target-skill-dir>
```

- **Done when**: you have the exact `lint_skill.py` output, the skill's `## Goal`, and an inventory of all files in the target skill.

### 2. Gather behavioral evidence

- **Mode A (Feedback / Audit)**: Record every user complaint and its stated reason. When an execution trace or session history is available, read the full trace—not just the final output—to spot wasted tool calls, hesitation, misapplied rules, or premature completion.
- **Mode B (Baseline Value Test)**: Run two fresh, isolated subagents (or clean sequential contexts if subagents are unavailable) on the exact same real user prompt:
  1. **Baseline run**: raw prompt with no skill loaded.
  2. **Skill run**: same prompt with the target skill loaded.
  Inspect both outputs and both execution traces. Present the comparison using `## Comparison Format` below, then ask the user what they dislike and why.

- **Done when**: every complaint, trace defect, or baseline delta is documented as concrete evidence.

### 3. Diagnose value, goal, and root failure modes

Evaluate the skill against `../skill-create/references/standards.md`:

- **Value Gate**: Check whether the skill measurably beats the no-skill baseline on `## Goal`. If the baseline matches or beats the skill, recommend **deleting or merging** the skill rather than patching it.
- **Goal and architecture challenge**: Check whether `## Goal` hides multiple aspects, mixes creation with review, lacks self-verification, or relies on LLM prose where a deterministic script in `scripts/` would be more reliable. When a stronger alternative exists, propose it explicitly.
- **Root-cause mapping**: Map every evidence item and lint finding to a concrete failure mode: vague threshold, missing non-obvious *why*, missing inline gotcha, weak completion criterion, premature completion, poor pointer wording, missing progressive disclosure, duplication, environment cache, no-op sentence, sediment, or missing deterministic script.

- **Done when**: every proposed change links 1-to-1 to concrete evidence, a lint finding, or a standards violation—zero speculative rewrites.

### 4. Grill on open decisions and apply approved edits

Present all proposed changes using `## Review Format` below. Before editing, run a short grill-me interview on every open decision—unclear user requirements, conflicting priorities, proposed `## Goal` changes, scope splits, invocation changes, new deterministic scripts, or retiring the skill (invoke the `grilling` skill if available; otherwise ask one decision at a time with a recommended answer). Skip the interview only for unambiguous mechanical fixes (such as a broken link) with no trade-offs. Never alter `## Goal`, split, or delete a skill without explicit user confirmation.

Apply approved edits cleanly:

- Turn every recurring real-run mistake into an inline `## Gotchas` item.
- Move repeated deterministic parsing, validation, or formatting into `scripts/` (read `../skill-create/references/patterns.md` first).
- Delete entire no-op and sediment sentences instead of shortening prose for style.
- Keep single source of truth across all files.

- **Done when**: every open decision is explicitly confirmed by the user and every approved edit is applied with zero introduced duplication.

### 5. Re-verify until clean

1. Re-run `../skill-create/scripts/lint_skill.py <target-skill-dir>`.
2. When working inside a repository with `scripts/check-repo.py`, read `../skill-create/references/repo-conventions.md`, update catalog/version files if required, and run `python3 scripts/check-repo.py`.
3. When changes addressed a real failure or Mode B test, re-run the failing prompt in a fresh subagent and verify the defect no longer reproduces without regressions.
4. Repeat steps 3–5 until deterministic checks exit `0` and the user confirms the result meets `## Goal`.

- **Done when**: deterministic validators exit `0` and the target failure no longer reproduces.

## Comparison Format

Always use this markdown table in Mode B:

| Dimension | Baseline (no skill) | With skill | Verdict |
| --- | --- | --- | --- |
| Meets `## Goal` | Concrete result | Concrete result | Better / Same / Worse |
| Trace efficiency (detours, retries) | Observed steps | Observed steps | Better / Same / Worse |
| Concrete defects | Observed defects | Observed defects | Better / Same / Worse |

## Review Format

Always use this markdown table when proposing edits:

| Location | Defect / Evidence | Proposed Change | Why |
| --- | --- | --- | --- |
| `SKILL.md:42` | Concrete defect or lint finding | Exact edit or deletion | Specific behavioral improvement |

## Gotchas

- Judging only the final output hides wasted steps, retries, and hesitation caused by vague instructions or bloated context; inspect execution traces too.
- Fixing mistakes by appending new rules without pruning builds sediment that dilutes attention; delete or tighten existing lines before adding new ones.
- Testing a skill only in isolation hides zero-value skills; run a no-skill baseline whenever added value is uncertain.
- Challenging `## Goal` without a concrete superior alternative wastes user time; name both the defect and the replacement.

## References

- Read `../skill-create/references/standards.md` before auditing or editing any skill.
- Read `../skill-create/references/patterns.md` when introducing a deterministic script, checklist, plan-validate-execute flow, or router skill.
- Read `../skill-create/references/repo-conventions.md` when refining a skill inside a repository with `scripts/check-repo.py`.
