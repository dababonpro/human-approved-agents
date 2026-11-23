# Changelog

## Unreleased

- Section 8 of the guide advises stating both sides of an approval trade-off and keeping questions about meaning apart from risk approvals. This is our judgement, and it is not tested
- Section 15 advises checking, when the model or tool version changes, whether each rule is still needed, and removing one only after its scenario runs clean without it. It cites the placebo round, where no check failed in eight of 26 scenarios with no rules file
- Section 7 advises grading how strong each proof is, from "someone said so" to "reproduced in the running system", and proving the one fact a risky change depends on by running code. Practitioner guidance, not tested
- Section 16 advises pairing each rule with what enforces it, and adding a check, not more wording, when an unenforced rule is broken twice. Practitioner guidance, not tested
- Section 6 advises treating an agent's own work record as a claim: add-only, corrected by new entries, checked against the session history before anyone relies on it, with spreadsheet formulas escaped. Practitioner guidance, not tested
- Section 3 maps the team autonomy scale (L1 AI-assisted to L5 dark factory) onto this playbook's per-action levels: the playbook covers L2 to L3.5, raises one kind of change at a time, and keeps authentication, billing, customer data and migrations on approval. Vendor guidance, not tested
- Section 11 adds override and false-alarm counts for merging without approval, and notes that the proposed floor of 20 clean changes still leaves a failure rate of up to 14% open
- `playbook/evidence.md` has a row for each addition, with its sources linked and its limits
- The scorer records `harness_peek`: the harness paths an agent's own tool calls named, such as `/harness/stage/scenario.json`, which names the scenario and condition. It does not change the verdict. `harness.batch status` lists those attempts, and the test plan says to report them apart. Over the stored attempts it flags 2 of 114 Antigravity attempts from 18 November 2026 and none of 2,662 Claude Code attempts, so the published placebo round is unaffected. `tools/check_harness.py` checks the flag
- The agent under test no longer sees the harness. Its files moved from `/harness` to `/srv/ops`, readable by root only, under neutral names (`services.py`, `runner.py`, `start.sh`), so `ls`, `ps` and reading files show no test rig. The turn runner now starts with `env -i` and runs as root, and starts each agent CLI as the unprivileged user with an environment that holds no `HARNESS_*` variable. Before this, the agent inherited the entrypoint's whole environment, including the mock services' API keys and the collector token. The approval stand-in is now `mcp__approvals__approve`, installed in `/usr/local/lib/approvals/`, and reads `APPROVAL_POLICY` and `APPROVAL_LOG`. `harness_peek` also flags reads of `/srv/ops` and of the stand-in's source. Results before this change are unaffected in scoring, but their agents could see more than the method describes. `tools/check_harness.py` checks each of these

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
