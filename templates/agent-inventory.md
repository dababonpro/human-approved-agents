# Agent Inventory

*From the Human-Approved Agent Playbook by DababonPro IT Solutions, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Suggested credit if you adapt it: keep this line and note what you changed.*

Team owner: [name]. Senior sponsor: [name]. Last reviewed: [date]. Review this quarterly, and whenever an agent changes.

| Agent | What it does | Can read and change | Human owner | Tool, model, version | Vendor, and data sent to it | Skills and connectors | Identity or key | Key expires | Highest level in use | Risk card | How to stop it |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Example: nightly report | Summarises tickets | Reads tickets, changes nothing | [name] | [tool, model, version] | [vendor, ticket text] | None | Own read-only key | [date] | 0 | [link] | Disable the schedule |
| Example: coding agent | Drafts code changes | Reads the repo, changes branches only | [name] | [tool, model, version] | [vendor, source code] | [list] | Own bot account, or note if it must use a person's login | [date] | 1 | [link] | Close the session, revoke the token |
| | | | | | | | | | | | |

Levels: 0 Read, 1 Draft, 2 Act with approval, 3 Act within limits. Record the level for each kind of action in `approval-matrix.md`.

Check each row:

- Does it have a named owner?
- Does it use its own identity? If a tool forces a person's login, say so here.
- Could it do its job with less access?
- Has anyone tried the stop method?
- Is the tool on your approved list?
