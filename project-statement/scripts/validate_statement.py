"""Validate a project statement mapping.

scripts/render.py imports validate and _is_todo from this module.
"""

from __future__ import annotations

import re

VALID_PROJECT_TYPES = {"data-science", "software"}
VALID_ON_DVC = {"tracked", "untracked", "abandoned"}
VALID_FOLDER_LOCATIONS = {"gdrive", "nas"}
VALID_DATASET_LOCATIONS = {"nas", "gdrive", "other"}
YYYY_MM_RE = re.compile(r"^\d{4}-\d{2}$")


def _is_todo(value) -> bool:
    return isinstance(value, str) and value.strip().lower().startswith("todo:")


class ValidationError(Exception):
    pass


def _require(cond: bool, msg: str, errors: list[str]) -> None:
    if not cond:
        errors.append(msg)


def validate(data: dict) -> list[str]:
    errors: list[str] = []

    _require(isinstance(data, dict), "top-level must be a mapping", errors)
    if errors:
        return errors

    name = data.get("name")
    _require(isinstance(name, str) and name.strip(), "`name` is required (non-empty string)", errors)

    ptype = data.get("project_type")
    _require(
        ptype in VALID_PROJECT_TYPES,
        f"`project_type` must be one of {sorted(VALID_PROJECT_TYPES)}",
        errors,
    )
    is_ds = ptype == "data-science"

    goal = data.get("goal")
    _require(isinstance(goal, str) and goal.strip(), "`goal` is required (non-empty string)", errors)

    dod = data.get("definition_of_done") or []
    _require(
        isinstance(dod, list) and len(dod) >= 1 and all(isinstance(x, str) and x.strip() for x in dod),
        "`definition_of_done` must be a list with >= 1 non-empty string",
        errors,
    )

    team = data.get("team") or []
    _require(isinstance(team, list) and len(team) >= 1, "`team` must be a list with >= 1 entry", errors)
    if isinstance(team, list):
        for i, m in enumerate(team):
            prefix = f"team[{i}]"
            if not isinstance(m, dict):
                errors.append(f"{prefix} must be a mapping")
                continue
            for k in ("name", "role", "joined"):
                v = m.get(k)
                _require(isinstance(v, str) and v.strip(), f"{prefix}.{k} required", errors)
            joined = m.get("joined", "")
            if isinstance(joined, str) and not _is_todo(joined):
                _require(
                    YYYY_MM_RE.match(joined) is not None,
                    f"{prefix}.joined must be YYYY-MM (got {joined!r})",
                    errors,
                )
            left = m.get("left")
            if isinstance(left, str) and left.strip() and not _is_todo(left):
                _require(
                    YYYY_MM_RE.match(left) is not None,
                    f"{prefix}.left must be YYYY-MM (got {left!r})",
                    errors,
                )

    constraints = data.get("constraints") or {}
    _require(isinstance(constraints, dict), "`constraints` must be a mapping", errors)
    if isinstance(constraints, dict):
        has_any = any(
            isinstance(v, list) and len(v) > 0
            for k, v in constraints.items()
            if k in CONSTRAINT_CATEGORY_ORDER
        )
        _require(has_any, "`constraints` must have at least one non-empty category", errors)
        for k in constraints:
            if k not in CONSTRAINT_CATEGORY_ORDER:
                errors.append(
                    f"`constraints.{k}` is not in the closed vocabulary "
                    f"{CONSTRAINT_CATEGORY_ORDER}"
                )

    repos = data.get("repositories") or []
    _require(
        isinstance(repos, list) and len(repos) >= 1,
        "`repositories` must be a list with >= 1 entry",
        errors,
    )
    if isinstance(repos, list):
        primary_count = sum(1 for r in repos if isinstance(r, dict) and r.get("primary") is True)
        _require(
            primary_count == 1,
            f"exactly one repository must have primary: true (found {primary_count})",
            errors,
        )
        for i, r in enumerate(repos):
            prefix = f"repositories[{i}]"
            if not isinstance(r, dict):
                errors.append(f"{prefix} must be a mapping")
                continue
            for k in ("name", "url", "description"):
                v = r.get(k)
                _require(isinstance(v, str) and v.strip(), f"{prefix}.{k} required", errors)

    tools = data.get("tools") or []
    if tools:
        _require(isinstance(tools, list), "`tools` must be a list", errors)
        for i, t in enumerate(tools):
            prefix = f"tools[{i}]"
            if not isinstance(t, dict):
                errors.append(f"{prefix} must be a mapping")
                continue
            _require(
                isinstance(t.get("name"), str) and t["name"].strip(),
                f"{prefix}.name required",
                errors,
            )
            # `url` is optional — some tools (e.g. Slack) have no useful link.
            url = t.get("url")
            if url is not None:
                _require(
                    isinstance(url, str) and url.strip(),
                    f"{prefix}.url must be a non-empty string when present",
                    errors,
                )

    folders = data.get("folders") or []
    if folders:
        _require(isinstance(folders, list), "`folders` must be a list", errors)
        for i, f in enumerate(folders):
            prefix = f"folders[{i}]"
            if not isinstance(f, dict):
                errors.append(f"{prefix} must be a mapping")
                continue
            loc = f.get("location")
            _require(
                loc in VALID_FOLDER_LOCATIONS,
                f"{prefix}.location must be one of {sorted(VALID_FOLDER_LOCATIONS)}",
                errors,
            )
            for k in ("purpose", "url"):
                v = f.get(k)
                _require(isinstance(v, str) and v.strip(), f"{prefix}.{k} required", errors)

    if is_ds:
        datasets = data.get("datasets") or []
        _require(
            isinstance(datasets, list) and len(datasets) >= 1,
            "DS projects require `datasets` with >= 1 entry (TODO entry allowed)",
            errors,
        )
        if isinstance(datasets, list):
            for i, d in enumerate(datasets):
                prefix = f"datasets[{i}]"
                if not isinstance(d, dict):
                    errors.append(f"{prefix} must be a mapping")
                    continue
                for k in ("name", "purpose", "url", "license"):
                    v = d.get(k)
                    _require(isinstance(v, str) and v.strip(), f"{prefix}.{k} required", errors)
                loc = d.get("location")
                _require(
                    loc in VALID_DATASET_LOCATIONS,
                    f"{prefix}.location must be one of {sorted(VALID_DATASET_LOCATIONS)}",
                    errors,
                )
                on_dvc = d.get("on_DVC")
                _require(
                    on_dvc in VALID_ON_DVC,
                    f"{prefix}.on_DVC must be one of {sorted(VALID_ON_DVC)}",
                    errors,
                )
        explog = data.get("experiment_log")
        _require(
            isinstance(explog, str) and explog.strip(),
            "DS projects require `experiment_log` (Google Sheet URL or TODO sentinel)",
            errors,
        )

    return errors
