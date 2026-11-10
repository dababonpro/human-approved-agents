---
name: setup-playbook
description: Set up the whole Human-Approved Agent Playbook in the current project for the person, from one short interview. Draft the agent rules (AGENTS.md), the agent inventory, a risk card, the approval matrix and the incident runbook from the templates and their answers, show every draft before writing, then guide them through the two real limits and a stop test they must do themselves. Use it when someone asks to set up, install, adopt or apply the human-approved agent playbook, or to set up agent governance, approvals or controls for a project.
---

# Set up the playbook

The person should answer a few questions, not fill in five templates. Read what the project already shows, ask only what it cannot tell you, draft every file, and write nothing until they approve.

The drafts are a first layer. The playbook's point is that agent instructions alone are not enforceable, so the setup is not finished until the person has turned on real limits and tried stopping the agent. Say that plainly at the start and at the end.

## Steps

1. **Get the templates.** Use the playbook's `templates/` folder: two folders above this skill's folder when the skill comes with the playbook, or a clone of `https://github.com/dababonpro/human-approved-agents`. Without either, fetch the five files from `https://raw.githubusercontent.com/dababonpro/human-approved-agents/main/templates/`: `AGENTS.md`, `agent-inventory.md`, `risk-card.md`, `approval-matrix.md` and `incident-runbook.md`. If you can get none of them, stop and say so. Never write the files from memory.
2. **Check what exists.** If `AGENTS.md` or an `agent-playbook/` folder already exists, do not replace anything. Say what you found and ask whether to stop, write the drafts beside the old files with a `.playbook` suffix, or replace them.
3. **Read the project to suggest answers.** Read only: the README, build and test scripts, CI and deploy settings, and config file names. For a config or `.env` file, read the setting names only and hide the values. Never print a secret value.
4. **Ask once, briefly.** Send one message with these questions, each with your suggestion from step 3, so the person can answer "yes" to most:
   1. Who owns these agents, and who approves risky actions? Deleting, deploying, changing permissions or spending money needs someone other than the person who asked. If they work alone, suggest the client, a colleague or a second session the next day, and record it.
   2. What does the project do, in one sentence, and how are the tests run?
   3. What is the test environment, what counts as production, and what must agents never touch?
   4. Which agents or AI tools work on this project, and what can each read and change?
   5. What is the one measure the main agent should improve, and today's number if known?
   6. What data is involved: none, internal, personal, secrets or regulated? Do agents read content from outside the team, such as web pages, emails or tickets?
   7. How do you stop each agent: revoke a key, close a session, disable a schedule?
   8. In one line, what risk will you accept and what will you not?
   9. Who is the backup contact, and who handles a data or security problem? One person may hold every role.

   Say that a skipped question stays as a `[bracket]` to fill in later.
5. **Draft all five files** from the templates and the answers. Replace only the brackets the person answered, in their words, and keep every other line, including the credit lines and the rules. In the approval matrix's "Enforced by" column, write "instruction only" for any rule no system enforces yet. Do not invent a limit that is not in place.
   - `AGENTS.md` at the project root
   - `agent-playbook/agent-inventory.md`: one row per agent from question 4
   - `agent-playbook/risk-card.md`: for the main agent
   - `agent-playbook/approval-matrix.md`
   - `agent-playbook/incident-runbook.md`
6. **Show the drafts, then wait.** For each file, show the lines you filled and list the brackets still open. Name every file you will write. Write nothing until the person says yes, and accept a yes for some files and not others.
7. **Write the approved files.** If a `CLAUDE.md` exists without `@AGENTS.md`, show the one line you would add at its top and add it only after a yes. Read each file back, then report the paths, the brackets still open and anything you did not write.
8. **Hand over the two things only the person can do.** These are not optional, and the drafts are not a control without them:
   - **Two real limits.** A read-only key or account for the agent wherever it touches production data, and branch protection on the main branch (on GitHub: Settings, then Rules, then a ruleset that requires a pull request and blocks force pushes). Give the exact steps for the tools in this project. Change a setting yourself only if the person asks and you have the access.
   - **A stop test.** Walk them through stopping one agent the way the runbook says, and recording that it worked.

   Then suggest one real task in a test environment, to see where the rules catch it.

## Rules

- Do not invent an answer, a person, a date or a limit. A suggestion stays a suggestion until the person accepts it.
- Do not change any other file in the project, except the one `CLAUDE.md` line after a yes.
- If the person asks for something the templates forbid, such as letting an agent deploy without approval, write the template's rule and tell them where to change it themselves.
- Keep it to one project. Widening to more projects, people or systems comes after the agent has handled real work under these rules.

---

*Part of the Human-Approved Agent Playbook by DababonPro IT Solutions. Copyright (c) 2026 DababonPro IT Solutions. Licensed under the MIT licence; the full text is in the `LICENSE` file in this folder.*
