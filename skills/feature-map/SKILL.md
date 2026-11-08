---
name: feature-map
description: "Procedure for keeping a repo's important features from regressing, by recording what must stay true for each feature, which code it lives in, and what proves it, then checking every change against that map. Use it when setting up regression protection, when a task or PR might break existing behaviour, when an agent will change code in a repo with a features.toml, when asked for a feature map, behaviour inventory or regression guard, or when a bug has come back. Also use it before calling a change verified in such a repo."
---

# Feature map

Tests that pass show the checked behaviour still works. They do not show which behaviour matters, or whether this change touched it. A feature map records both in a file the repo owns. It also flags a deleted, skipped or edited test for a person. It does not judge a test edit, and its skip patterns are a tripwire, not a defence.

Each entry says what must stay true, where the code lives, and what proves it. A script then matches a change to its features, runs their proof, and fails on gaps. No feature map replaces reading the code. It catches broken promises, not poor design.

## 1. Check it fits

Use it on a repo that changes often and has behaviour someone would be hurt to lose. Skip it for throwaway code. Do not map everything. A full map goes stale, and a stale map is ignored.

## 2. Create the map

1. List the 5 to 10 flows that would hurt most if they broke. Ask the owner. Look at incidents, repeat bugs and the fixes in git history, because a bug that came back once tends to come back again.
2. Copy `references/features.template.toml` to `features.toml` at the repo root.
3. Write each `must_stay_true` line as behaviour a user or system would notice, not as code. Good: "A failed write is reported as a failure." Poor: "`save()` calls `commit()`."
4. Point `code` at the files that can break the feature, including config and infrastructure. A policy file can break a form without touching its code.
5. Point `proof` at commands that check those promises, and that a person could run. End each proof with a count of tests run, and do not pipe it, because a pipe can hide its exit code.
6. Set `mapped_paths` to the folders of the flows you mapped, and start narrow. Everything outside them is visibly out of scope. Use `ignore` for exceptions inside those folders. After adoption, adding to `ignore` needs a person.

## 3. Prove the proof

Do this before you trust the map.

1. **Run every proof on clean code.** Each must pass. A proof that already fails tells you nothing, so fix it or replace it. A proof that only passes on one machine or operating system is a fault in the proof.
2. **Break each feature on purpose.** In a throwaway branch or worktree, undo a real fix or break the behaviour, then confirm the check fails and names the cause. If it still passes, the proof is decoration, however green it looks. A proof you have never seen fail has not proved anything.
3. **Check for promises with no proof.** Read each `must_stay_true` line against the proof. Mark any line nothing checks, then write a check or tell the owner.

## 4. Check each change

`--run` executes shell commands from `features.toml`, so never run it on an untrusted branch on a machine holding credentials.

Run from the repo root, using the path of this skill's folder:

```bash
python <skill>/scripts/check_feature_map.py --base origin/main --worktree --run
```

| Result | Meaning | What to do |
|---|---|---|
| `UNMAPPED` | A changed file belongs to no feature | Add it to a feature. Adding it to `ignore` needs human approval |
| `PROOF-FAILED` | A touched feature's proof failed | Fix the code. Do not change the test until you know which is wrong |
| `NO-PROOF`, `NO-PROMISE` | A touched feature is incomplete | Complete the entry |
| `TEST-REMOVED` | A test was deleted or moved | Needs human approval |
| `TEST-WEAKENED` | A skip or focus marker was added | Remove it, or get human approval |
| `TEST-EDITED` | An existing test line was changed or removed | Needs human approval. Proofs do not run. Adding new tests, or removing a skip marker, is fine |
| `MAP-WEAKENED` | A promise, code path, proof, feature or setting was changed or removed, a proof was added, or `ignore` grew | Needs human approval. The proofs do not run, so a changed proof cannot vouch for itself |
| `STALE-MAP` | A code path matches no file. A folder must be written with `/**` | Fix the map |
| Exit 2, `ERROR` | The map or git could not be read | Fix the error. This is not a pass |

Report which features were touched, their promises, which proofs ran, and the result. Read the count of tests run and skipped in each proof's last line. Zero run is a failure, whatever the exit code. If you did not use `--run`, say the change is unverified.

"Needs human approval" means stop and ask. In CI, that approval is a required code-owner review. Open a pull request that names the weakening, and do not try to clear the check another way.

**What it cannot see.** It does not follow dependencies between features, or see changes outside `mapped_paths`, such as dependency files, CI or cloud settings. Run every proof on a schedule and after those changes.

## Rules

- **An agent never weakens the map to get a pass.** Removing a promise, narrowing a code path, changing or adding a proof, changing settings, or skipping, editing or deleting a test all need a person. Adding a promise, a code path or a new test is fine. A new proof needs a person because it runs unreviewed. Passing tests can be reached by removing what they check, so the check treats that as the failure.
- **Change a promise on purpose, never by accident.** If the requested work really changes the behaviour, say which promise changes and get approval first.
- **Add a promise when you fix a regression.** Each repeat bug adds one line and one proof. That is how the map grows, rather than by a big documentation effort.
- **Enforce it in CI, not only locally.** Run the check on every pull request and make it required. Protect `features.toml`, the tests and the check itself with required code-owner review. See `references/ci.md`. Without that, a person can see these changes only if they look.
- **Only CI passes `--promises-approved`,** behind required code-owner review. An agent passing it locally proves nothing.
- **Keep some checks out of reach.** Where you can, keep a few black-box checks outside the repo, or in a path the agent cannot edit, and run them against the running system.
- **Treat a green result as evidence, not proof.** It covers the promises written down, and nothing else. Keep reading the diff.

## Common failures

| Failure | Why it happens | Fix |
|---|---|---|
| The map goes stale | It is treated as documentation | Fail on unmapped files, and keep it small |
| Everything is mapped to one huge feature | The check is easy to satisfy that way | Split it. Each feature should run a focused proof |
| Proofs are too slow | Every feature runs the full suite | Point each feature at its own tests |
| Proofs pass but the feature is broken | The proof checks code shape, not behaviour | Break the feature on purpose (step 3) |
| Infrastructure breaks a feature | Config is not listed under `code` | Add policy, routing and deployment files |

This method has had one small pilot and one agent trial, so test it on your own repo. Known limits: `references/known-limits.md`.

---

*Part of the Human-Approved Agent Playbook by DababonPro IT Solutions. Copyright (c) 2026 DababonPro IT Solutions. Licensed under the MIT licence; the full text is in the `LICENSE` file in this folder.*
