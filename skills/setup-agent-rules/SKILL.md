---
name: setup-agent-rules
description: Set up the Human-Approved Agent Playbook's agent rules (AGENTS.md) in the current project for the person, by reading the project, asking them a few short questions, filling the template from their answers, and writing the file only after they approve it. Use it when someone asks to set up, install, add or adopt the agent rules, an AGENTS.md, or the human-approved agent playbook in a project.
---

# Set up the agent rules

The person should not have to edit the template by hand. Read what the project already shows, ask only what it cannot tell you, and write the file after they approve it.

## Steps

1. **Get the template.** Use `templates/AGENTS.md` two folders above this skill's folder, which is there when the skill comes with the playbook. If it is missing, fetch `https://raw.githubusercontent.com/dababonpro/human-approved-agents/main/templates/AGENTS.md`. If you can do neither, stop and say so. Never write the rules from memory.
2. **Check the project root.** If an `AGENTS.md` already exists, do not replace it. Say so, and ask whether to stop, write the new rules to `AGENTS.playbook.md` for the person to merge, or replace the old file. Note whether a `CLAUDE.md` or `CLAUDE.local.md` exists.
3. **Read the project to suggest answers.** Read only. Useful places: the README, `package.json` scripts, `Makefile`, `pyproject.toml`, CI workflows, deploy settings and config file names. For a config or `.env` file, read the setting names only and hide the values. Never print a secret value.
4. **Ask once, briefly.** Send one message with these questions, and put your suggestion from step 3 beside each one so the person can just say "yes":
   - Who owns these rules, and who approves risky actions? Deleting, deploying, changing permissions or spending money needs approval from someone other than the person who asked.
   - What does the project do, in one sentence?
   - How do you run the tests?
   - What is the test environment, and what counts as production?
   - What must the agent never touch?
   - Which branches may the agent push to, if any? Suggest "none".
   - Where does your team keep notes?

   Tell them that any question they skip stays as a `[bracket]` in the file, to fill in later.
5. **Fill the template.** Replace only the `[brackets]` the person answered, with their words. Keep every other line exactly as it is, including the credit line and the rules. Leave `[none yet]` under Standing classes: those are added later, with the approval matrix.
6. **Preview, then wait.** Show the filled "About this project" section, the owner and approver line and the push line, name the file you will write, and list any brackets left open. Write nothing until the person says yes.
7. **Write the file.** Write `AGENTS.md` at the project root, or the file they chose in step 2. Then:
   - If a `CLAUDE.md` exists and does not already contain `@AGENTS.md`, Claude Code will not read the new file. Show the one line you would add at the top, `@AGENTS.md`, and add it only after a yes.
   - If a `CLAUDE.local.md` exists, say that it stops Claude Code reading `AGENTS.md` directly, so the `@AGENTS.md` line is needed.
8. **Check and report.** Read the file back. Report the path, any `[brackets]` still open, and whether `CLAUDE.md` was changed. Do not commit or push.

## After setup

Suggest one test in a test environment: ask the agent to change several records, for example "mark every open order as shipped". It should show exactly what it will change and wait for approval.

Say plainly that these rules are a first layer, and an agent can still ignore them. Real limits come next: a read-only key for production and branch protection. Section 5 of the playbook and its first-day guide cover them.

## Rules

- Do not invent an answer the person did not give or confirm. A suggestion stays a suggestion until they accept it.
- Do not change any other file in the project, except the one `CLAUDE.md` line after a yes.
- If the person asks for something the template forbids, such as letting the agent deploy without approval, write the template's rule and tell them where to change it themselves.

---

*Part of the Human-Approved Agent Playbook by DababonPro IT Solutions. Copyright (c) 2026 DababonPro IT Solutions. Licensed under the MIT licence; the full text is in the `LICENSE` file in this folder.*
