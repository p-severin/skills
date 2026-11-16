#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "$0")/.." && pwd)
home_dir=${HOME:?HOME is required}

link_one() {
  local dest_root="$1"
  local skill_dir="$2"
  local name target
  name=$(basename "$skill_dir")
  target="$dest_root/$name"
  mkdir -p "$dest_root"
  if [[ -L "$target" || ! -e "$target" ]]; then
    ln -sfn "$skill_dir" "$target"
    return
  fi
  echo "refusing to replace non-symlink: $target" >&2
  exit 1
}

shopt -s nullglob
found=0
for group_dir in "$root"/skills/*/; do
  for skill in "$group_dir"*/; do
    if [[ -f "${skill}SKILL.md" ]]; then
      skill_dir=${skill%/}
      link_one "$home_dir/.claude/skills" "$skill_dir"
      link_one "$home_dir/.agents/skills" "$skill_dir"
      found=$((found + 1))
    fi
  done
done

if [[ "$found" -eq 0 ]]; then
  echo "no skills found under $root" >&2
  exit 1
fi

echo "linked $found skills into $home_dir/.claude/skills and $home_dir/.agents/skills"
