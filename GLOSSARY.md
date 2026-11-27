# Glossary

## skills-ref

`skills-ref` is a program run from the terminal. It checks whether each skill
directory and its `SKILL.md` follow the Agent Skills format.

This repository runs `skills-ref` during validation. The program checks the
file structure and metadata, but it does not test the skill's behavior.

## User-invoked skill

A user-invoked skill runs only after the user selects it by name or from a
skill picker. After selection, the agent performs the skill automatically.

## Model-invoked skill

A model-invoked skill may run after the agent selects it from the task context.
The user does not need to name the skill.
