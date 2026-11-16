# Skills

This repository is the catalog of agent skills. Each skill lives at `skills/<group>/<skill>/`. Install one skill with the skills CLI.

```bash
npx skills add p-severin/skills --skill <name>
```

`scripts/link-skills.sh` links every skill into `~/.claude/skills` and `~/.agents/skills`.

## Scraping

| Skill | Version | When to use |
| --- | --- | --- |
| [web-scraping-scout](skills/scraping/web-scraping-scout/SKILL.md) | 1.0.1 | Use when the user wants a site scouted before a scraper is built or redesigned, or the scrape request is still unclear. |
| [web-scraping-simple](skills/scraping/web-scraping-simple/SKILL.md) | 1.0.0 | Use when the user wants a small standalone Python scraping proof after a scout. |
| [web-scraping-pipeline-design](skills/scraping/web-scraping-pipeline-design/SKILL.md) | 1.0.1 | Use when the user wants a production scraping pipeline designed after scouting and before implementation. |
| [web-scraping-ops](skills/scraping/web-scraping-ops/SKILL.md) | 1.0.0 | Use when a scraper already exists and the user wants a failing run diagnosed or a run audited before the data is trusted. |
| [web-scraping-references](skills/scraping/web-scraping-references/SKILL.md) | 1.0.1 | Use when another scraping skill points at a shared reference, or when a scraping workflow needs one shared reference loaded. |
| [scrapy-build](skills/scraping/scrapy-build/SKILL.md) | 1.0.1 | Use when the user wants a Scrapy project created, a domain or spider added, or page objects written. |
| [scrapy-deploy](skills/scraping/scrapy-deploy/SKILL.md) | 1.0.1 | Use when the user wants an existing Scrapy project deployed or scheduled. |
| [crawlee-build](skills/scraping/crawlee-build/SKILL.md) | 1.0.0 | Use when the user asks for a Crawlee-python crawler, or a production design has approved Crawlee for a browser-heavy target. |

## Engineering

| Skill | Version | When to use |
| --- | --- | --- |
| [hook-setup](skills/engineering/hook-setup/SKILL.md) | 1.0.1 | Use when the user wants Python or JS/TS pre-commit hooks set up or repaired. |
| [show-the-change](skills/engineering/show-the-change/SKILL.md) | 1.0.0 | Use when proposing a change in code, UI, configuration, architecture, data, or process, or when a result is hard to picture. |
| [project-statement](skills/engineering/project-statement/SKILL.md) | 1.0.0 | Use when the user wants a project statement created or updated. |
| [mlflow-analyzer](skills/engineering/mlflow-analyzer/SKILL.md) | 1.0.0 | Use when the user wants traditional MLflow experiment runs ranked or compared. |
| [write-digica-readme](skills/engineering/write-digica-readme/SKILL.md) | 1.0.0 | Use when the user wants a Digica README written or audited. |

## Learning

| Skill | Version | When to use |
| --- | --- | --- |
| [generate-flashcards](skills/learning/generate-flashcards/SKILL.md) | 1.0.0 | Use when the user wants flashcards from text, a file, or a URL. |
| [anki-export](skills/learning/anki-export/SKILL.md) | 1.0.0 | Use when the user wants flashcard JSON turned into an Anki .apkg deck. |
| [kolbs-reflection](skills/learning/kolbs-reflection/SKILL.md) | 1.0.0 | Use when the user asks for a Kolb cycle reflection or a socratic pass through Experience, Reflection, Abstraction, and Experiment. |

## Productivity

| Skill | Version | When to use |
| --- | --- | --- |
| [obsidian-notes](skills/productivity/obsidian-notes/SKILL.md) | 1.0.0 | Use when the user wants notes found, created, edited, summarized, or organized in an Obsidian vault. |
| [plain-talk](skills/productivity/plain-talk/SKILL.md) | 1.0.0 | Use when writing any reply, explanation, question, progress update, summary, recommendation, warning, or error for a person. |
