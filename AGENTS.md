# Agent Rules For This Repository

This repository publishes guidance that people may rely on, so accuracy matters more than speed.

## Before you finish

Run these from the repository root:

```bash
python -m unittest discover -s skills/feature-map/scripts -p "test_*.py"
python tools/check_links.py
python tools/scan_private.py
```

If `features.toml` exists on the base branch, also run:

```bash
python skills/feature-map/scripts/check_feature_map.py --base origin/main --worktree --run
```

## Rules

- Do not state a fact without a source you have read. Link it, and say what kind of evidence it is.
- Do not raise a verdict in `playbook/evidence.md` without new evidence.
- Do not write "tested on", "safe", "secure", "compliant" or "aligned". Published results go in `testing/results/` and are dated.
- Do not weaken `features.toml`, a test or a check to get a pass. Ask a person.
- Do not add real company names, people, customer data or secrets.
- Keep section numbers in `playbook/playbook.md` stable, because other files cite them.
- Do not push, publish or release. A person does that.
