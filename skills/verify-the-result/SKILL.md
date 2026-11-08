---
name: verify-the-result
description: Procedure for confirming that work actually succeeded before calling it done. Use it after any write, data move, deploy, fix or test run, and whenever a tool, script or log reports success.
---

# Verify the result

A success message tells you what a program reported, not what happened. Check the outcome where it lives.

## What to check

| After | Check |
|---|---|
| A database or record write | Read the row back from the system of record |
| A data move | Compare counts on both sides, then spot-check a sample |
| A deploy | Check the live behaviour and the running version |
| A bug fix | Reproduce the failure before you edit, keep that output, then show the same check passing after |
| A test run | Read what ran, including skips and warnings |
| A message or form | Confirm it arrived, if you have a way to see that |

## Rules

- If a step returned no error but also no result, treat it as failed. Swallowed errors look like success.
- Test the code path that matters. A passing test nearby proves nothing about the change.
- Report what you checked and how, so a reader can repeat it.
- Read skipped tests and warnings, not just the pass count. Report each one, with its reason, in your reply.
- If you could not check something, say so plainly. Never write "should work" as if it were a result.
- If the check fails, show the failure. Do not retry until it passes without understanding why it failed.

---

*Part of the Human-Approved Agent Playbook by DababonPro IT Solutions. Copyright (c) 2026 DababonPro IT Solutions. Licensed under the MIT licence; the full text is in the `LICENSE` file in this folder.*
