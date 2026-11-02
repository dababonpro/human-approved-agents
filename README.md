# The Human-Approved Agent Playbook

A free playbook, templates and agent skills for small teams adopting AI agents safely.

This is for teams of 5 to 50 people with no governance committee and no platform budget. It gives you three layers: rules the agent reads, limits it cannot cross, and people who check.

**Status: draft 0.7.** The agent files have not finished testing, so this repository makes no "tested on" claim yet. It is not legal advice, and using it does not make you compliant with any law or framework.

## Start Here

1. Read [The Idea In One Page](playbook/playbook.md#the-idea-in-one-page).
2. Follow [Start Here: Your First Day](playbook/playbook.md#start-here-your-first-day) on one lower-risk project.
3. Copy the [templates](templates/) and [skills](skills/) into that project, and edit them to fit.

## What's Inside

| Path | What it is |
|---|---|
| [`playbook/playbook.md`](playbook/playbook.md) | The guide for the technical leader |
| [`playbook/evidence.md`](playbook/evidence.md) | How strong the evidence is behind each default |
| [`playbook/framework-mapping.md`](playbook/framework-mapping.md) | How it relates to IMDA, NIST and ASEAN |
| [`templates/`](templates/) | Agent rules, inventory, approval matrix, risk card, runbook and checklist |
| [`templates/examples/`](templates/examples/) | The risk card and rules filled in for an imaginary team |
| [`skills/`](skills/) | Agent skills: `preview-then-execute`, `verify-the-result`, `session-handover`, `feature-map` |
| [`testing/`](testing/) | How the agent files are tested, and the test harness |

## Skills

Each skill is a folder with a `SKILL.md`. Read a skill before you install it, the way you would read code from a stranger. Copy the folder to wherever your agent loads skills, such as `.agents/skills/` or `.claude/skills/`.

`feature-map` stops important behaviour regressing. It records what must stay true for each feature, then checks every change against that record.

## How Far To Trust This

Most of this is guidance and judgement, not proven standard, and [`playbook/evidence.md`](playbook/evidence.md) says which is which. National cyber security agencies advise using agents only for low-risk, non-sensitive work. This playbook allows more, under stated conditions, and says so.

## Licence

Copyright DababonPro IT Solutions, 2026.

- The guide in `playbook/` and the files in `templates/` and `testing/test-plan.md`: [CC BY 4.0](LICENSE-docs). You may copy and adapt them if you give credit, link to the licence, and say whether you changed them.
- Skills, scripts and the test harness: [MIT](LICENSE).

Published by [DababonPro IT Solutions](https://dababon.pro).
