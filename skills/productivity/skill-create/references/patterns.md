# Optional Skill Patterns (P1 / P2)

Load this reference when deciding whether a skill benefits from deterministic scripts, checklists, plan-validate-execute, or a router skill. Apply a pattern only when the task concretely earns it.

## Deterministic Scripts in `scripts/` (P1)

Bundle an executable script when:

- Execution traces show the agent repeatedly reinventing parsing, validation, formatting, or calculations.
- The skill has objective checks that a script can verify faster and more reliably than LLM judgment (schema checks, link checks, structural lint, diff checks).

Script rules:

- Make every script non-interactive, deterministic, and callable with explicit CLI arguments.
- Print actionable error messages (exact file, line, field, and expected value) so the agent can self-correct in a validation loop.
- Prefer Python 3 standard library only so the script runs cleanly without extra installation steps.
- Keep shell and Python scripts portable across Linux and macOS (POSIX/bash 3.2, BSD tools).

## Checklists for Multi-Step Workflows (P2)

Use an explicit markdown checklist (`- [ ] Step 1: ...`) when a workflow has four or more dependent stages with strict ordering or validation gates, so the agent tracks progress without skipping stages.

## Plan-Validate-Execute (P2)

Use this pattern for batch, stateful, or destructive operations (bulk edits, form filling, migrations):

1. Inspect the target and emit a structured intermediate plan (for example, JSON mapping source keys to intended changes).
2. Run a deterministic validation script checking the plan against the source of truth.
3. Revise the plan until validation exits `0`.
4. Execute the mutation script from the validated plan only.

## Router Skills (P2)

Create a router skill only after the number of `user-invoked` skills in one domain exceeds what the user reliably remembers.

- Make the router itself `user-invoked` (`disable-model-invocation: true`) so it adds zero context load.
- List each sibling skill and the exact condition for choosing it.
- Remember that a router can only recommend `user-invoked` siblings—the human invokes them directly.
