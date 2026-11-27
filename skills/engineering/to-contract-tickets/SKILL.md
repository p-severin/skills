---
name: to-contract-tickets
description: "Use when the user wants a plan, spec, or conversation turned into tracker tickets whose interface, rules, and test names are fixed in a code contract before implementation."
disable-model-invocation: true
metadata:
  version: "1.0.1"
---

# To Contract Tickets

Turn a plan, spec, or conversation into **tracer-bullet** tickets that an
agent implements against a fixed **contract**. Prose leaves room to guess. A
type checker, a lint, or a named test does not. Put every decision that code
can express into code. Prose carries only the goal and the reasons.

## Vocabulary

- **Contract**: the code boundary of one feature. Types, error classes, stub
  signatures, new checks, and the CLI contract when a command changes. One
  contract PR and one contract issue hold it.
- **Mechanism**: what enforces a rule. One of `type`, `lint`, `test`,
  `formal`, or `review`. `review` marks a rule no tool enforces yet.
- **Tracer bullet**: a ticket that cuts a narrow, complete path through every
  layer the change crosses and is verifiable on its own.
- **Frontier**: the tickets whose blockers are all closed.
- **Tracker rules**: the repo's own rules for blocking edges, labels,
  sub-issues, and the verification gate. `AGENTS.md` or `CLAUDE.md` usually
  points to them.

## Ownership

The repo's tracker rules own tracker mechanics. This skill owns the ticket
body: its sections, their order, and their content. When the tracker rules
require an extra section, such as a text `Blocked by`, append it after
`Out of scope`. Reason: each repo keeps its working conventions, and every
ticket in every repo reads the same way.

## Process

### 1. Gather the source

Work from the conversation. When the user passes a spec path, an issue
number, or a URL, read its full body and every comment.

Done when you can state the feature's goal in one sentence and list every
decision already made, each with its source.

### 2. Read the repo's rules

Read each of these that exists:

- the tracker rules and the triage labels;
- the glossary and the ADRs for the area you will touch;
- every project verification skill under `.agents/skills/`,
  `.claude/skills/`, or `.cursor/skills/`: `verify-*` skills with a feature
  map, and formal verification skills with covered code and a run command.

When the repo has no tracker rules, ask the user to choose GitHub Issues or
local files. Write every ticket in the glossary's terms. Reason: the
implementing agent searches the code with those terms.

Done when you can name the tracker, the ready label, the blocking mechanism,
the verification gate, and the verification skill for each area you touch.

### 3. Trace the code and sketch the contract

Trace every module, command, and data shape the feature touches through the
real code. Write the contract in the language of the module it belongs to.
Reason: a contract written against imagined code fixes the wrong rule, and
code fixes a wrong rule harder than prose does.

Sketch two contracts that differ in shape: who owns each piece of state, and
where the module boundaries sit. Pick the one where each piece of state has
one owner, each task has one way to do it, and callers know the least.
Reason: the first shape hides the alternative the user may prefer.

Write contract code by these rules:

- Model data as `Protocol`, frozen `@dataclass`, or pydantic models in
  Python, and as interfaces or types in TypeScript. Make illegal states
  unrepresentable.
- Give every error a caller branches on its own exception class.
- Write stub bodies as `...` in protocols and `raise NotImplementedError` in
  functions. The contract fixes the boundary. The ticket's agent owns the
  inside.
- Write no comments and no docstrings. Names and types carry the meaning.
  Move a rule that needs words into Constraints with a mechanism. Reason: a
  comment is a rule nothing enforces.
- Add a CLI contract only when the feature adds or changes a command. Show
  one invocation, every exit code, and the output format for each code.

```text
$ tool sync --check
exit 0  ok
exit 1  stale: <name> (<source>)
exit 2  unavailable: <source>
```

List the feature-wide rules, each with its mechanism. Add new lint or check
rules to the contract when the stubs already pass them.

Done when every function boundary the feature crosses appears in the contract
and every rule has a mechanism.

### 4. Quiz 1: the contract

Show the user the contract code, the CLI contract, the feature-wide rules
table, and the rejected shape in two lines with the reason you rejected it.
Ask whether the types, the errors, and the command behaviour are right.
Iterate until the user approves the contract explicitly. Reason: every ticket
builds on the contract, so it is the most expensive part to change later.

### 5. Slice into tickets

- Cut each ticket as a tracer bullet through the layers this change crosses.
  Name those layers from the code you traced, for example lock file,
  installer, runtime directories, smoke test.
- Make each ticket verifiable on its own.
- Size each ticket to fit one fresh context window.
- Put prefactoring first, as its own tickets. Make the change easy, then
  make the easy change.
- Sequence a wide refactor as a **parallel change**. A wide refactor is one
  mechanical change whose blast radius breaks call sites across the codebase
  at once. Add the new form beside the old one in one ticket. Migrate call
  sites in batches sized by blast radius, one ticket per batch, each blocked
  by the first ticket. Remove the old form in a last ticket blocked by every
  batch. CI stays green between batches because the old form still exists.

Every ticket is blocked by the contract issue. Add an edge between two
tickets only when one genuinely gates the other.

Done when exactly one ticket implements each contract symbol and exactly one
ticket owns each user-visible behaviour.

### 6. Quiz 2: the breakdown

Show a numbered list. For each ticket show the title, its blockers, its Goal,
and the contract symbols it implements. Ask whether the granularity fits,
whether each edge gates real work, and which tickets to merge or split.
Iterate until the user approves the breakdown explicitly.

### 7. Publish

Read [references/example.md](references/example.md) before you write the
first body. For local files, follow
[references/local-files.md](references/local-files.md) instead of this step.

On GitHub, publish in this order:

1. Create the contract issue from the contract template. Make it a sub-issue
   of the source issue when one exists.
2. Commit the contract code and new checks on `contract/<feature-slug>`. Run
   the repo checks locally. Open a PR whose body says
   `Closes #<contract issue>`. When the contract has no code, skip the PR and
   close the contract issue after step 3, because Quiz 1 approved it.
3. Create the tickets in dependency order, blockers first. Set native
   blocking edges to the contract issue and to each blocking ticket. Make
   each ticket a sub-issue of the source issue, or of the contract issue when
   there is no source. Apply the repo's ready label, `ready-for-agent` by
   default, to tickets only.

Leave the source issue open and unchanged. Watch the contract PR's CI and fix
the PR until it passes. Reason: a red contract blocks every ticket.

Done when the contract PR is green, every ticket has all six sections, and
every edge points to a real issue. Report the links and the frontier.

## Ticket body

Title every ticket with the behaviour it delivers. Write in English.

````markdown
## Goal

<One sentence: the behaviour a user of this surface observes when done.>

## Context

**Problem.** <One or two sentences: what is missing today and why it matters.>

**Decisions.**

- <Decision> (source: user, YYYY-MM-DD | ADR-NNNN | #NN)

Feature-wide context: #<contract issue>

## Interface

Implements from #<contract PR>:

- `<Type>`
- `<function>`

<CLI contract, only when this ticket owns the command.>

The contract is fixed. If it blocks the Goal, stop, describe the conflict in
a comment on this issue, and wait for the user's decision.

## How to verify

```python
def test_<behaviour>(): ...
```

```gherkin
Given <state>
When <action>
Then <observable effect>
```

Drive <feature> with `<verify skill>`. <The repo's verification gate.>

## Constraints

| Rule | Mechanism |
| --- | --- |
| <Rule> | type: `<Type>` |

## Out of scope

- <Item>: #<ticket>
- <Item>: not planned
````

Fill each section by these rules:

- **Goal** is one sentence about observable behaviour. The user is whoever
  touches the surface: an end user, a CLI caller, or a library caller.
  Reason: people and agents scan it first, and the tests carry the detail.
- **Context** holds only this ticket's decisions. Feature-wide decisions live
  in the contract issue. Reason: one source of truth per decision.
- **Interface** names contract symbols and never copies their code. Reason: a
  copy drifts from the PR.
- **How to verify** gives every test a name and an empty body in the repo's
  test language, followed by its gherkin block. The implementing agent writes
  the bodies under these exact names. Name each test after a behaviour. Every
  `Then` is an observable effect: a return value, an error class, an exit
  code, output, or state a user can read back. Include the failure path for
  each rule the ticket enforces. Point to the feature map entry of the
  verification skill when one covers the area.
- **Constraints** gives every rule a mechanism. A ticket that adds a
  user-visible feature carries the rule that the verification skill's
  feature map lists that feature. When the area has no verification skill and
  the ticket needs one, propose a separate ticket that runs
  `create-verification-skill` or `create-formal-verification-skill` and
  blocks this ticket.
- **Out of scope** points each item to the ticket that owns it or marks it
  `not planned`. Reason: the agent then leaves that work alone.

Name symbols, commands, and tests. Leave out file paths and line numbers,
because they go stale before the ticket starts.

## Contract issue body

Use the same headings as a ticket, scoped to the whole feature:

- **Goal**: the feature's observable behaviour in one sentence.
- **Context**: the problem and every feature-wide decision with its source.
- **Interface**: the link to the contract PR, every contract symbol, and the
  CLI contract.
- **How to verify**: the contract PR passes the repo checks.
- **Constraints**: the feature-wide rules table.
- **Out of scope**: what the whole feature leaves out.
