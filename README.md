# The Human-Approved Agent Playbook

A free playbook, templates and agent skills for small teams putting AI agents to work with clear human ownership and controls.

**Public edition 1.0, prepared 5 November 2026.** This is practical guidance, not a certification or a determination that a law or framework has been met. The evaluation record is limited to the described setup, dates and attempts; many entries remain pending human review. It is not legal advice, and using it does not make you compliant with any law or framework.

## Start here

1. Read [The Idea In One Page](playbook/playbook.md#the-idea-in-one-page).
2. Follow [Start Here: Your First Day](playbook/playbook.md#start-here-your-first-day) on one lower-risk project.
3. Adapt the [templates](templates/) and [skills](skills/) to your environment.

## What's included

| Path | Contents |
|---|---|
| [`playbook/`](playbook/) | Main guide, evidence notes and framework mapping |
| [`templates/`](templates/) | Agent rules, inventory, approval matrix, risk card, incident runbook and launch checklist |
| [`skills/`](skills/) | `preview-then-execute`, `verify-the-result`, `session-handover` and `feature-map` |
| [`testing/`](testing/) | Evaluation method and dated result record |

Each skill is a folder with a `SKILL.md`. Read a skill before you install it, the way you would read code from a stranger. Copy the folder to wherever your agent loads skills, such as `.agents/skills/` or `.claude/skills/`.

## How far to trust this

Most of this is guidance and judgement, not proven standard, and [`playbook/evidence.md`](playbook/evidence.md) says which is which. National cyber security agencies advise using agents only for low-risk, non-sensitive work. This playbook allows more, under stated conditions, and says so.

## Evaluation status

The dated record describes a Claude Code run in a disposable mock project. The full B/C runs predate one rule added on 4 November; a 50-attempt targeted follow-up covers that rule but is not a full rerun. All 50 follow-up records remain pending human review. The holdout, Codex full run, outside-authored scenarios and independent repeat were not completed. See the [method and limits](testing/test-plan.md) and [dated record](testing/results/2026-11-05-claude-code.md). No broad effectiveness or reliability claim is made.

## How to cite

> DababonPro IT Solutions. *The Human-Approved Agent Playbook*, public edition 1.0. 2026. Licensed under CC BY 4.0 (guide and templates) and MIT (skills and code).

Each template carries a suggested credit line, and each skill folder carries its own MIT licence file. The licences' own terms are what apply: CC BY 4.0 asks for appropriate credit, a link to the licence and an indication of changes, in any reasonable manner, and MIT asks that its copyright and permission notice stay with copies or substantial portions.

## Licence

Copyright DababonPro IT Solutions, 2026.

- `playbook/`, `templates/`, `testing/test-plan.md` and `testing/results/`: [CC BY 4.0](LICENSE-docs). Credit the author, link to the licence and note changes.
- `skills/`, `testing/harness/`, scripts and the evaluation harness: [MIT](LICENSE).

Published by [DababonPro IT Solutions](https://dababon.pro).

This playbook is independent. It is not affiliated with or endorsed by Anthropic, OpenAI, Anysphere, GitHub, Google or any other vendor whose tools it mentions. Product names belong to their owners.
