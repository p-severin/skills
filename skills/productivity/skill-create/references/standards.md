# Skill Authoring Standards

Single source of truth for creating and refining agent skills. Every P0 rule is mandatory; P1 rules apply whenever they fit; P2 patterns live in `patterns.md`.

## Value and Goal (P0)

- **Value Gate**: Create or keep a skill only when an unassisted agent fails without it. If the model already performs the task well by default, recommend not building—or deleting—the skill.
- **`## Goal` section**: Place a 1–2 sentence `## Goal` heading near the top of `SKILL.md`. Name the single concrete problem and verifiable outcome.
- **Self-verification**: Every skill must specify how to verify that its output satisfies `## Goal`. Prefer deterministic verification (a script in `scripts/` or an existing CLI validator) over subjective self-checking whenever mechanical rules exist.

## Scope and Granularity (P0)

- **One goal per skill**: Keep skills maximally narrow. Split distinct aspects into separate skills, and separate creation from review or refinement (for example, `skill-create` and `skill-refine`).
- **Real expertise only**: Ground every rule in user brain dumps, notes, real task traces, corrections, or project artifacts. Never generate generic procedures from model defaults.
- **Generalize deliberately**: When distilling from one real run, strip single-repo names and one-off fixtures so the procedure solves the class of task.

## Invocation and the Two Loads (P0)

Every skill spends one of two budgets:

- **Context load**: Always-loaded tokens (such as a `model-invoked` skill's `description`) paid on every turn whether or not the skill fires.
- **Cognitive load**: Human memory required to know which skills exist and invoke them by name. Do not minimize cognitive load blindly; it buys human control and zero context waste.

Default to **user-invoked** (`disable-model-invocation: true`). Omit `disable-model-invocation` (making the skill **model-invoked**) only when the agent or another skill must trigger it autonomously.

## Context Pointers and `description` (P0)

A context pointer names out-of-context material and encodes when to load it. Pointer wording—not the target file—determines activation reliability.

- **Model-invoked `description`**: Front-load the leading concept, keep one trigger per genuinely distinct branch, collapse synonyms, and cut identity the body already carries.
- **User-invoked `description`**: Write one short human-facing summary sentence and strip trigger lists.
- **In-body pointers**: Always pair the exact file path with its trigger condition (`Read references/api-errors.md when the API returns non-200`), never a bare `see references/`.

## Information Hierarchy, Progressive Disclosure, and Co-location (P0)

Rank material on three tiers:

1. **In-file steps**: Ordered actions the agent executes.
2. **In-file reference**: Definitions, rules, and gotchas consulted on every run.
3. **Disclosed reference**: Separate files behind a conditional pointer (`references/`, `assets/`, `scripts/`).

Rules:

- Keep `SKILL.md` under **500 lines** and **5,000 tokens**.
- **Branching test**: Keep inline what *every* run needs; disclose behind a pointer what only *some* branches need. Disclosure protects attention on the main steps, not just token count.
- **Co-location**: Keep a concept's definition, rules, and caveats under one heading instead of scattering them across sections.

## Procedures, Strictness, and Reasoning (P0)

- **Procedures and decision trees**: Teach *how* to approach a class of problems via repeatable steps or an explicit decision tree—never hardcode a single-instance answer.
- **Defaults, not menus**: Pick one default tool or approach with a brief escape hatch instead of listing equal alternatives.
- **Strict thresholds**: Specify concrete numbers, exact formats, and unambiguous conditions. Ban vague modifiers (`reasonably`, `tasteful`, `where appropriate`, `as needed`, `handle errors appropriately`, `follow best practices`, `try to`).
- **Write the non-obvious *why***: Add a brief rationale next to non-obvious rules so the agent generalizes accurately to uncovered cases instead of guessing or applying rules blindly. Omit obvious justifications.
- **Moderate detail plus one example (P1)**: Concise stepwise guidance paired with one concrete working example outperforms encyclopedic edge-case catalogs.

## Language Levers (P0 / P1)

- **Positive framing (P0)**: State the target behavior positively so forbidden behavior is not activated in context. Reserve heavy guardrails (`Never`, `Always`, `Strict`) for non-negotiable constraints, and always pair a prohibition with the required positive action.
- **Leading words (P1)**: Replace repeated multi-word explanations with one compact pretrained concept (such as `tight`, `red`, `relentless`, `tracer bullet`) that anchors the same behavior in fewer tokens.

## Completion Criteria (P0 / P1)

- **Checkable and demanding bounds (P0)**: End every step on a concrete done-condition that separates done from not-done and forces thorough legwork (for example, `every modified model accounted for` instead of `produce a change list`).
- **Premature completion fallback (P1)**: When visible later steps tempt the agent to rush the current step, sharpen the done-condition first. Split across a real context boundary (subagent dispatch, hand-off, or separate skill) only if the bound remains irreducibly fuzzy and rushing persists.

## Pruning Discipline (P0)

- **No-op test**: Check every sentence: *Does deleting this sentence change agent behavior versus model defaults?* If not, delete the entire sentence rather than trimming words for style. Settle uncertainty by running the skill, not debating.
- **Single source of truth**: State each rule in exactly one authoritative place. Duplication inflates maintenance cost and distorts priority.
- **Environment as source of truth**: Leave one-command lookups (`package.json`, config files, directory layout, `--help`) to the environment where they cannot go stale. Document only unwritten conventions, rationale, and traps.
- **Anti-sediment**: On every revision, remove stale or superseded lines instead of appending new layers on top.

## Core Instruction Patterns (P0)

- **Inline `## Gotchas`**: Keep environment-specific traps inline in `SKILL.md` so the agent reads them before hitting them. Add a new gotcha every time a real run reveals a non-obvious mistake.
- **Output templates**: Show the exact markdown, JSON, or table structure instead of describing it in prose. Keep short templates inline; move long or conditional templates to `assets/`.
- **Validation loops**: Structure work as `produce -> run deterministic validator or reference check -> fix errors -> repeat until clean`.
