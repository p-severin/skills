# Repository Conventions (`p-severin/skills`)

Load this reference only when creating or refining a skill inside this repository (detected by `scripts/check-repo.py` at the repository root).

## Layout

- Place every skill at `skills/<group>/<skill>/`, where `<group>` is one of: `scraping`, `engineering`, `learning`, `productivity`.
- Allowed root files inside a skill directory: `SKILL.md` and `CHANGELOG.md` only.
- Allowed subdirectories inside a skill directory: `references/`, `scripts/`, `assets/`, and `agents/` (flat—no nested subdirectories inside them). `agents/` may contain only `openai.yaml`.
- Write skill content in English.

## Frontmatter and Versioning

- `name`: must match the skill directory name (`[a-z0-9-]+`).
- `description`: must start with `Use when` (enforced by `scripts/check-repo.py`). Keep `user-invoked` descriptions to one short human-facing sentence after `Use when`.
- `disable-model-invocation: true`: single source of truth for `user-invoked` skills. Omit it for `model-invoked` skills.
- `agents/openai.yaml`: derived from `SKILL.md` for Codex (`policy.allow_implicit_invocation: false` for `user-invoked` skills, omitted for `model-invoked` skills). Run `python3 scripts/check-repo.py --sync-codex` after changing `disable-model-invocation`.
- `metadata.version`: quoted semver string (for example, `"1.0.0"`) matching the top `## x.y.z` heading in `<skill>/CHANGELOG.md`.

## Cross-Skill Links

- Skills in the same group may link shared files with relative paths (`../<sibling>/references/<file>.md`).
- `scripts/check-repo.py` validates every relative markdown link, heading fragment (`#slug`), and inline-code `.md` path starting with `../` or `references/`.

## Required Catalog Updates

When adding, renaming, or removing a skill:

1. Register the skill name in `GROUPS` in `scripts/check-repo.py`.
2. Add or update its row under the matching group table in `README.md`, copying `description` verbatim from `SKILL.md`.
3. Add a new version entry at the top of the root `CHANGELOG.md` with the updated total skill count.
4. Keep every file in the repository at or below 5,000 tokens and `SKILL.md` under 500 lines.

## Script Portability and Validation

- Shell and skill scripts must work on macOS bash 3.2 and BSD utilities (no `declare -A`, `mapfile`, `readarray`, bash 4 case operators, `readlink -f`, GNU-only `sed -i` without suffix, `find -printf`, or `grep -P`).
- Validate everything before finishing:
  ```bash
  python3 scripts/check-repo.py
  ```
  Run `uvx pre-commit run --all-files` when `skills-ref` is not directly on `PATH`.
