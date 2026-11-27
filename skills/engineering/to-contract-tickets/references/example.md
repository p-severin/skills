# Example: one feature, one contract, one ticket

Copy the shape and the level of precision. The feature, names, and numbers
are illustrative.

Feature: a Python CLI, `skillsync`, installs agent skills listed in a lock
file. A skill removed upstream makes the install fail halfway and leaves the
runtime directory half updated.

## Contract PR #41: code

```python
SkillName = NewType("SkillName", str)
Source = NewType("Source", str)
StagedSkills = NewType("StagedSkills", Path)


@dataclass(frozen=True)
class LockEntry:
    name: SkillName
    source: Source
    skill_path: PurePosixPath


@dataclass(frozen=True)
class StaleEntry:
    entry: LockEntry


@dataclass
class UpstreamUnavailable(Exception):
    source: Source


def stage(lock: Sequence[LockEntry], staging_root: Path) -> StagedSkills | list[StaleEntry]:
    raise NotImplementedError


def install(staged: StagedSkills, runtime_root: Path) -> None:
    raise NotImplementedError
```

The PR also adds one lint rule: the `skillsync.staging` module may not import
`skillsync.runtime`. The stubs already pass it.

## Contract issue #40

````markdown
## Goal

`skillsync install` changes the runtime directory only after every locked
skill is fetched.

## Context

**Problem.** An upstream repo removed a skill. The install copied half the
skills into the runtime directory, then failed, and agents loaded a mixed
set.

**Decisions.**

- Staging is the validation. One fetch both proves and supplies the skills
  (source: user, 2026-11-27).
- A stale entry fails the install. The tool never drops the entry silently
  (source: ADR-0007).

## Interface

Contract: #41

- `LockEntry`, `StaleEntry`, `UpstreamUnavailable`, `StagedSkills`
- `stage`, `install`

```text
$ skillsync install
exit 0  installed: <count>
exit 1  stale: <name> (<source>: <skill_path>)
exit 2  unavailable: <source>
```

## How to verify

#41 passes the repo checks.

## Constraints

| Rule | Mechanism |
| --- | --- |
| Install accepts only staged skills | type: `StagedSkills` |
| Staging never touches the runtime directory | lint: `staging-imports-runtime` |
| A failed install leaves the runtime directory unchanged | test: `test_failed_install_leaves_runtime_unchanged` |

## Out of scope

- Detecting renamed skills: not planned
- Pinning skills to commits: not planned
````

## Ticket #43: Reject stale lock entries before install

Blocked by #40 and #42 (native edges). Sub-issue of #38.

````markdown
## Goal

`skillsync install` exits with code 1 and names every stale entry when a
locked skill no longer exists upstream.

## Context

**Problem.** Today the install reports the first missing skill only, after
it has already copied others.

**Decisions.**

- Report every stale entry in one run, sorted by name (source: user,
  2026-11-27).

Feature-wide context: #40

## Interface

Implements from #41:

- `stage`
- `StaleEntry`

```text
$ skillsync install
exit 1  stale: <name> (<source>: <skill_path>)
```

The contract is fixed. If it blocks the Goal, stop, describe the conflict in
a comment on this issue, and wait for the user's decision.

## How to verify

```python
def test_install_names_every_stale_entry(): ...
```

```gherkin
Given lock entries "ghost" and "zombie" missing upstream
And lock entry "plain-talk" present upstream
When the user runs "skillsync install"
Then the exit code is 1
And stderr lists "ghost" and then "zombie", one per line
```

```python
def test_failed_install_leaves_runtime_unchanged(): ...
```

```gherkin
Given lock entry "ghost" missing upstream
And a runtime directory with installed skills
When the user runs "skillsync install"
Then the runtime directory is byte-identical to before
```

Drive "Install skills" with `verify-skillsync`.

## Constraints

| Rule | Mechanism |
| --- | --- |
| Stale entries are reported in name order | test: `test_install_names_every_stale_entry` |
| The runtime directory changes only after staging succeeds | type: `StagedSkills` |

## Out of scope

- Network retries for an unavailable source: #44
- Removing stale entries from the lock: not planned
````

