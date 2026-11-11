# Changelog

## 1.1.1, 11 November 2026

No change to the guide, the skills or the harness.

- The plugin version is 1.1.1. Release 1.1.0 still carried plugin version 1.0.0, and its changelog heading still said "unreleased"

## 1.1.0, 11 November 2026

A placebo comparison, and the harness changes that made it possible.

- A placebo comparison in `testing/results/2026-11-11-placebo-comparison.md`: 780 attempts over no rules file, the playbook files and two placebo rules files, with its limits. The README reports it
- Harness conditions P and G stage a placebo rules file, and the scorer records a `system_verdict` beside `verdict`
- `harness.batch` plans a shuffled round, fills one slot per complete attempt and continues after a stop
- The test plan says to publish both verdicts when comparing rules files. It first said to compare on system checks only, which hid failures where the report is the behaviour under test
- A `setup-playbook` skill and a one-prompt setup in the README
- The quick start says the rules are a first layer, not a guarantee
- The guide names the real skills and examples folders
- `testing/results/README.md` lists the dated records

## 1.0.0, 8 November 2026

Public edition 1.0.

- Evaluation results for Claude Code, with their limits, in `testing/results/2026-11-05-claude-code.md`
- Agent rules for problem reports, unlisted dependencies, secrets, and checking notes against the system of record
- The skills install as a Claude Code plugin from this repository
- A `setup-agent-rules` skill that writes `AGENTS.md` from a few questions
- A five-minute quick start, a hero image and issue templates
- A Leader's Brief, and a Start here by role table in the README

## 0.7.0, unreleased

First public draft.

- Playbook, evidence grading and framework mapping
- Templates for agent rules, inventory, approval, risk, incidents and launch checks
- Skills: `preview-then-execute`, `verify-the-result`, `session-handover`, `feature-map`
- Test plan and harness, with 26 scenarios. No results published yet
