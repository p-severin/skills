# Publishing to local files

Use this file when the tracker is local files. It replaces step 7 of the
skill. Every body section and every rule for filling it stays the same.

## Layout

Write one file per issue under `.scratch/<feature-slug>/issues/`:

- `00-contract.md` holds the contract issue body.
- `NN-<ticket-slug>.md` holds one ticket each, numbered from `01` in
  dependency order, blockers first.

Write one ticket per file. Reason: an agent claims and closes one file
without touching the others.

## Front matter

Start every file with YAML front matter. Scripts and agents read the edges
and the status from it, so the body carries no `Blocked by` section.

```yaml
---
id: "03"
title: Reject stale lock entries before install
status: ready-for-agent
blocked_by: ["00", "02"]
parent: "#38"
contract_branch: contract/skill-staging
---
```

- `status` is `ready-for-agent`, `in-progress`, or `done`.
- `blocked_by` lists file ids. Every ticket lists `"00"`.
- `parent` is the source reference, or `null` when there is no source.
- `contract_branch` names the branch that holds the contract code.

`00-contract.md` uses the same fields with `blocked_by: []`.

## Contract code

1. Commit the contract code and new checks on `contract/<feature-slug>`.
2. Run the repo checks on that branch until they pass.
3. Tell the user to merge the branch. Set `status: done` in
   `00-contract.md` after the merge.

When the contract has no code, set `status: done` in `00-contract.md` right
after you write it, because Quiz 1 approved it.

## Frontier

A ticket is on the frontier when every id in its `blocked_by` has
`status: done`. Work the frontier in id order.

Done when every file has valid front matter, every `blocked_by` id exists,
and the repo checks pass on the contract branch. Report the file list and the
frontier.
