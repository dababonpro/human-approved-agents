# The Human-Approved Agent Playbook

A working starter for technical leaders who want AI agents doing real work without losing control of what they do.

Public edition 1.0, prepared 4 November 2026 by DababonPro IT Solutions.

## Who This Is For

This playbook is for a team of 5 to 50 people with no governance committee and no platform budget. You might be a CTO, an engineering lead, or the person who was told to "sort out AI". Your people already use coding or office agents, or they are about to.

It is not legal advice, and following it does not make you compliant with any law or framework. See `framework-mapping.md` for how it relates to published frameworks, and `evidence.md` for how strong the evidence is behind each default.

**Not covered here:** multi-agent systems, agents that control a desktop or browser, agents that talk to customers on their own, and agents that screen, rank or decide about people or affect vulnerable groups. Those need more than this playbook, including a fairness review. Start with IMDA's framework for agents.

**A stricter position exists.** National cyber security agencies advise using agents only for low-risk, non-sensitive work. This playbook allows more, under the conditions in section 4, and says so there.

## The Idea In One Page

Most AI policies govern what people may do with AI. An agent is different, because it acts. It runs commands, changes records and sends messages, sometimes many times a minute.

This playbook gives you three layers. Each one catches what the layer above misses.

1. **Rules the agent reads.** Plain text files such as `AGENTS.md` shape what the agent tries to do. They are cheap and useful, and they can fail. A model can forget them, misread them, or be talked out of them.
2. **Limits the agent cannot cross.** Permissions, sandboxes, read-only keys and branch protection stop an action even when the rules fail.
3. **People who check.** Approvals, reviews and sampled audits catch what the limits allow.

Never rely on the first layer for anything you could not afford to lose.

Seven rules hold the whole thing up:

1. **Every agent has a named human owner.** If nobody owns it, it does not run.
2. **Permission follows risk.** What the action can do, how far the damage spreads, and whether you can undo it decide how much control it needs.
3. **Limits come first.** Block the dangerous thing in the system, then use approvals for what remains.
4. **The agent shows the work before it acts.** A real preview comes first for anything that matters.
5. **Success is checked, not reported.** "Done" means someone or something looked at the result.
6. **You can stop it.** Every agent has a stop method, and someone has tried it.
7. **It must earn its place.** If it does not move a measure you care about, change it or remove it.

## Start Here: Your First Day

Adopt this on one lower-risk project. Keep the agent reading and drafting only, and use a test environment.

**The quick way.** Paste this into your agent in that project:

> Set up the Human-Approved Agent Playbook in this project. Get it from https://github.com/dababonpro/human-approved-agents (clone it into a temporary folder outside this project), copy its skills into this project, and follow its setup-playbook skill: ask me a few questions, draft the agent rules, inventory, risk card, approval matrix and incident runbook from my answers, and show me the drafts before writing anything. Then tell me the two limits I need to turn on myself and how to test stopping the agent.

It asks a few questions, drafts the files below from your answers, and writes nothing until you approve. Two steps stay with you whichever way you set up: put the two real limits in place, and try the stop method.

**By hand.** The same work, file by file:

| Time | Do this | File |
|---|---|---|
| 45 minutes | Name an owner, list the agents, fill in one risk card, send the vendor questions | `agent-inventory.md`, `risk-card.md`, section 12 |
| 30 minutes | Agree which actions need approval | `approval-matrix.md` |
| 45 minutes | Put two real limits in place: a read-only key and branch protection, if you have admin rights. Otherwise book the person who does | Section 5 |
| 30 minutes | Fill in the agent rules and add the skills | `AGENTS.md`, `skills/` |
| 30 minutes | Fill in the runbook and try the stop method | `incident-runbook.md` |
| 1 hour | Run one task in test, and see where the rules fail | Testing part of `pre-launch-checklist.md` |

After the first day, the agent works on one project under these rules. Keep it there until it has handled real work for a few weeks. Then widen it one step at a time: another project, another person, or access to another system. Widening sooner makes problems harder to spot and trace. Section 15 explains when to take each step.

## 1. Decide Whether To Use An Agent

Start with the job, not the tool.

- Could the step simply be removed?
- Could a script or a person do this adequately? A script does the same thing every time, so prefer one when the task has fixed steps.
- Who could be harmed if it goes wrong, how many people, and how badly?
- How likely is that? A frequent small error and a rare severe one need different handling.
- Does it touch personal data, money, production, or anything regulated?
- Does it read content from outside your team, such as web pages, emails or tickets?

Fill in `risk-card.md` for each agent before you set its levels. It is one page. It records the risks, what you will do about each one, what risk remains, and who accepts it. That person should be senior enough to own the outcome, such as a founder or a head of engineering. Write down in one line what level of risk your team will tolerate. No framework sets that for you.

Also note which laws may apply, such as data protection rules, and who checks them.

## 2. Pick One Owner And List Your Agents

Name one person as the agent owner for the team. They keep the inventory, decide disputes and review incidents. This is a part-time duty, not a new job.

Then list what is actually running, including anything this playbook does not cover. Include the coding agent on a developer's laptop, the scheduled job that calls a model, the chatbot in a support tool, and the automation someone built on a free account. The list is usually longer than leaders expect.

For each one, record who owns it, the tool, model and version, what it can read and change, whose identity it uses, what data goes to the vendor, and how to stop it. `agent-inventory.md` has the columns.

Agents built into other people's software, such as a CRM assistant or a chat tool's AI, cannot read your `AGENTS.md` or skills. For these the first layer does not exist. Govern them with the other two: the access you grant the tool (section 5), the vendor questions (section 12), and a person who checks the output (section 7). Record that in the inventory, so nobody assumes the rules apply.

## 3. Set A Level For Each Kind Of Action

Set levels per action, not per agent. One agent can read tickets at level 0 and tag them at level 3. Start low.

| Level | The agent may | Good for |
|---|---|---|
| 0. Read | Read and answer | Reporting, search, explaining code |
| 1. Draft | Prepare work that a person reviews | Code changes, tickets, message drafts |
| 2. Act with approval | Act after a named person approves the preview | Merging, updating records |
| 3. Act within limits | Act alone inside a written, narrow, reversible, logged scope, with a person sampling the results | Tagging, formatting, routine sync with rollback |

There is no level above 3 in this playbook. Agents that choose their own work with nobody supervising are out of scope.

These levels are this playbook's practical vocabulary, informed by similar schemes from AWS and IMDA. No published scheme for agents has been validated by experiment. Treat these levels as a way to discuss oversight, not as a measurement or standard.

Levels 0 and 1 carry less risk, not no risk. A meta-analysis of 18 experiments with non-AI automation suggested that, when a system fails, harm may be more likely once it moves from analysing information to proposing what to do. This is not evidence about AI agents. A reader who trusts a draft and passes it on can still cause harm, so review drafts properly. A wrong answer also causes harm if someone acts on it.

## 4. Decide What Needs Approval

Decide by three questions: what can the action do, how far does the damage spread, and can you undo it? Then write down whether each kind of action is allowed, needs approval, or is blocked.

| What the action does | Default rule |
|---|---|
| Reads non-sensitive data | Allowed, kept in the short-term tool-call record |
| Reads secrets, personal data or restricted systems | Allowed only for a stated reason, and see the session check below |
| Drafts | Allowed, a person reviews it |
| Routine development on a feature branch | Allowed while the session check has not tripped. Do not push unless the branch is named in `AGENTS.md` and has no deploy, preview app or workflow on push. A push that starts a deploy is a deploy. If the session check has tripped, preview and wait |
| Changes internal data, small and easy to undo | Level 3 if written as a standing class, otherwise preview and approval |
| Changes internal data, large or hard to reverse | Approval, with counts and a rollback plan |
| Reaches outside the company | Approval on the exact content, every time |
| Is hard to undo: delete data or logs, deploy, spend money, change permissions | Approval every time, with a rollback plan |
| Anything unusual, out of scope, or with no rule | Stop and ask |

This table is a floor. A sensitive context moves an action up a row. Tagging a medical record is not the same as tagging a support ticket.

Six national cyber security agencies go further than this table. Their 2026 joint guidance, written for government, critical infrastructure and industry, says to use agents only for low-risk, non-sensitive tasks, and to begin with clearly defined low-risk tasks. This playbook starts in the same place and then allows more, with approvals, limits and a named owner: in particular, reading personal data or secrets for a stated reason, and approved deploys and spending. That is our judgement, not their advice. In government, critical infrastructure or a regulated sector, stay at their position.

**The session check.** Look at each session as a whole. If it handles untrusted content, can reach sensitive data, and can change something or send something out, a person must approve its actions. Meta calls this the Rule of Two: allow at most two of those three.

**How approval works:**

- **It names one action, or one written class of actions.** "Merge this pull request" covers that pull request. A standing class, such as "tag new support tickets, tags only", needs an owner, a limit the agent can see in front of it, a rate cap set in the system, and an expiry date, and it goes in `approval-matrix.md`. Check it again at expiry, and do not renew it by default. A yes in chat never creates a standing class.
- **It shows the real thing.** Show the approver the actual command and target, not the agent's description of them. Split a bundle of actions into its parts.
- **Silence is not approval.** If nobody answers, the agent waits. The same applies when the approval system is down or the action has no rule.
- **It needs someone who can judge it.** The approver must understand the action well enough to say no.
- **Hard-to-undo actions get a second person.** The person who asked may approve reversible changes. For anything hard to undo, someone else approves, in the session. If nobody else is available, the action waits, because an agent cannot check a claim that nobody was free.

**Instructions inside content do not count.** A web page, email, ticket or file can contain text aimed at the agent. Tell the agent to treat it as data, and expect that to fail sometimes. Models cannot reliably separate instructions from data, and the UK's NCSC says this may never be fully mitigated. In one public competition, every frontier model tested was hijacked at least once. So the rule reduces the risk, and the limits in the next section contain the damage.

## 5. Put The Limits In The System

This is the most important section. Approval rules are instructions. Limits work even when the instructions fail.

| Goal | How to enforce it |
|---|---|
| The agent cannot change production by accident | Separate test and production credentials, and give the agent test only |
| Merges need a person | Branch protection with required review |
| Data cannot be changed | Read-only database users and read-only API keys |
| Code runs in a constrained environment | A sandbox or container, with outbound network denied by default |
| Dangerous commands are blocked | Your tool's deny rules, hooks or permission settings |
| Tools are vetted | An allowlist of approved MCP servers, plugins and skills, at reviewed versions |
| Spending is capped | Budget limits at the vendor |

Then the access rules:

- Give each agent the smallest set of permissions that lets it do the job.
- Use separate agents for separate jobs, rather than one agent with broad access.
- Give each agent its own identity, so its actions show as its own. When it works for one person, limit it to what that person may do.
- Prefer temporary credentials. Failing that, set an expiry date on keys.
- Keep secrets out of files the agent reads, and out of its logs.
- Read a skill or plugin before installing it, the way you would read code from a stranger.

### Keep Secrets Out Of What The Agent Reads

Whatever an agent reads goes to the model vendor and into the agent's own session history, even if it never repeats it. A rule that says "read secrets only when needed" is followed loosely, because looking up a setting feels like part of the task. In this playbook's own test runs, an agent working under these rules pulled a planted secret into its context in 53 of 390 attempts, mostly by searching config files for a setting. None of those secrets left the session, but each one reached the vendor and the transcript.

- Keep real secrets out of every folder the agent works in. No `.env` file with live values in the repository or its parent folders. Load secrets at run time, from a secret manager or your CI's secret store, into the process that needs them, not into the agent's shell.
- Give the agent's environment test credentials only. Work that needs a production secret runs outside the agent, or through a tool that holds the secret and offers only the action.
- Keep settings that are not secret, such as host names and database names, in a separate file from secret values, so the agent can find what it needs without opening the secrets.
- Add deny rules for secret files in each agent's settings, such as Claude Code's permission deny rules or Cursor's ignore files. A rule on the tool's own file reads may not stop a shell command such as `cat` or `grep`, so treat these as a second layer, not the fix.
- Treat a live secret that an agent has seen as exposed, and rotate it.

Where a tool cannot enforce a rule, write that down in `approval-matrix.md`, so nobody assumes it is protected.

## 6. Keep A Trail, And Watch It

When something goes wrong, you need to answer four questions: what did the agent do, on whose behalf, who approved it, and what did it change?

Log these for every action that changes something, and every read of sensitive data:

- Time, agent, owner, and what triggered it
- The action, its target and the environment
- Who approved it, if anyone
- The outcome, including failures

Keep logs where the agent cannot edit them, and decide how long to keep them. If a law sets a period, that applies. You usually do not need every conversation forever, but keep the agent's plans, tool calls and the sources it read for a short period, or you cannot trace an injected instruction. Mask secrets and personal data. Most agents also keep their own local history of every session, including the full output of every tool they ran, for example Claude Code under `~/.claude/projects`. That history holds any secret or personal data the agent read, so decide how long to keep it, who can read that machine, and whether it is synced or backed up. Your existing tools, such as git history, pull request reviews and ticket comments, may cover much of this.

A log nobody reads protects no one. Pick two or three signals, decide who sees them and what they do, and set an alert where your tools allow it:

- Repeated failures or denied tool calls
- Access outside the agent's normal scope
- A sudden rise in actions or cost

For level 3 actions, a named person samples the results on a set schedule. We suggest weekly for a small team. No source sets a frequency, so set one by volume and keep it.

## 7. Check The Result, Not The Report

In our experience this is the failure teams meet first, and it is the most useful habit in this playbook.

An agent's confident summary is not evidence. Agents can misreport what they did, and may behave differently under test than in real use. They can say a task succeeded when a step silently failed, when a test was skipped, or when they changed something near the target and not the target itself. Ordinary software fails the same way. A job can report "saved" because an error was swallowed further down, and the agent reporting it will believe it.

Build the check into the work:

- After a write, read the data back from where it landed.
- After a deploy, check the live result, not the build log.
- After a test run, look at what actually ran, including anything skipped.
- Compare counts on both sides of a data move.
- When an agent says it could not verify something, treat the work as unverified.

Reward the agent for saying "I could not confirm this". An honest gap costs a minute, and a false "done" can cost a week.

| Pattern | What it looks like | The fix |
|---|---|---|
| False success | The job reports inserted, but nothing reached the database | Fail loudly when a write returns no result, then read it back |
| Wrong environment | A change meant for test reaches production | Separate credentials, and name the target before acting |
| Stale context | The agent acts on a note that has gone out of date | Check the live system before acting on memory |
| Scope creep | A small fix turns into a wide rewrite | Agree the scope first, and review the diff |
| Approval drift | One yes gets treated as a standing yes | Approval covers one named action or a written class |

## 8. Keep Approvals Real

An approval only protects you if someone reads it. People who see many prompts stop paying close attention, and research on automation bias suggests training alone does not fix that. Anthropic reported in March 2026 that Claude Code users accepted 93% of permission prompts, and Microsoft's AI red team reports getting past human approval through consent fatigue in its red-team engagements.

- **Ask less often.** Limit access first, so the agent cannot do the dangerous thing unprompted. Then keep prompts for what matters.
- **Keep requests short,** and make the risk obvious.
- **Slow down the top row.** Ask for a written reason on the highest-risk approvals.
- **Look at the numbers monthly.** Check how often approvers change or reject a request, and how fast they answer. If nobody ever says no, the approval may have stopped working. No published threshold exists, so watch for change.
- **Test the reviewers.** Now and then, plant a harmless fault and see if it gets caught.
- **Do not add prompts to fix prompts.** If they arrive faster than someone can read them, tighten the limit instead.

A reviewer who is getting faster may be getting better, or may have stopped looking. Do not treat falling review time as a pure gain.

## 9. Prepare To Stop It

Before an agent goes live, know how to stop it, and test that it works. Repeat the test after any change to its access or tools, and on a schedule your team sets. No standard gives a number, so pick one you will keep. Time the drill, and record what you found.

Define an incident in advance: harm or possible harm to data, money, people or service, an agent acting outside its limits, a leaked secret or personal data, or a vendor failure. Log near misses too.

- **Notice:** Know what signal tells you something is wrong, and who sees it.
- **Stop:** Revoke its key, disable its schedule, or turn off its integration. First ask whether stopping halfway leaves a batch half-finished.
- **Contain:** Check what it changed, and stop anything downstream.
- **Repair:** Roll back, and tell anyone affected.
- **Learn:** Write down what happened in plain words, then change a rule, a limit or a check so it cannot recur the same way.

The runbook also covers a vendor failure, such as an outage or a vendor security incident. Keep a way to do the work by hand.

## 10. Measure Whether It Helped

Adoption is not value. Before you start, write down the one measure this agent should move, and record today's number. Then check it on a fixed date, once there is enough work to compare.

Use numbers from your systems, not impressions. In one controlled trial with early-2025 tools, experienced developers believed AI made them about 20% faster when it made them 19% slower. Published results range from much slower to much faster, depending on the task and tools, so your own number is the only one that applies to you.

Track a speed measure and a stability measure together, because a large survey linked AI use to faster delivery and less stable delivery.

| Track | Examples |
|---|---|
| Speed | Time from ticket to shipped change |
| Stability | Changes that failed or were reworked, defects found after release |
| Cost | Review and correction time, tool cost, rework |
| Risk | Rejected approvals, incidents, near misses, human overrides |

Time logs get unreliable when people run agents in the background, so sample a few real tasks instead of trusting totals. A single number can be gamed, so read these together.

## 11. Raise Or Lower A Level

Raise a level for one kind of action at a time, when all of these are true:

- **Enough checked outcomes.** Decide the failure rate you can live with, then count outcomes that someone or something checked against the result.
- **A real sample.** Include the hard cases. Routine work does not stand in for them. A person's approval alone does not count, because approval can become a habit: Anthropic reports 93% of Claude Code prompts are accepted.
- **A tested undo.** You have run the rollback at least once.
- **A review.** The owner agrees, records the date and the evidence, and updates the risk card.

| Clean, checked outcomes | Failure rate you still cannot rule out (95% confidence) |
|---|---|
| 10 | 26% |
| 30 | 10% |
| 60 | 5% |
| 100 | 3% |
| 300 | 1% |

Set the number by the damage one failure would do. Treat this as a floor, because real tasks are not fully independent. Low-volume agents may take months to get there, and that is the correct result. There is no published evidence for any fixed waiting period, so do not use one.

Drop a level after a serious incident. Recheck the level after a change of model, tool, access or scope. Run the checklist again and watch closely for a while after any change. Vendors change models, so assume this will happen.

## 12. Check Your Vendors

If you use someone else's agent, much of the risk sits with the vendor. Before you connect one, find out:

- Does the vendor train on your inputs, and how long is data kept?
- Who owns the generated output, and what is the position on intellectual property?
- Will the vendor tell you about incidents and about model changes?
- Can you get logs, scoped keys and usage limits?
- What performance can you expect, and how will you know if it drops?
- What do your contract terms say about security and data protection?
- What will you do if the service stops?

Keep an approved list of tools. If the answers are poor, limit what data the tool can reach.

## 13. Bring People With You

**The people who work with it.** In our experience, rollouts stall for human reasons: job worries, distrust of the output, a slower process. Say plainly what the goal is, and mean it. Let the people doing the lower-risk work shape the rules. Train owners and reviewers in how the agent fails and how over-trust works. Keep core skills alive, including for junior staff still learning the work. Share mistakes openly, the agent's included. "The AI did it" is never an answer.

**The people it affects.** If customers or the public receive an agent's output, tell them AI was involved, what it can do, and how to reach a person who will review a problem. An internal audit log does not do this job.

## 14. Retire It Properly

Stopping an agent is not retiring it. Keys, memory, schedules and downstream jobs can outlive it. When an agent is no longer needed, work through the retirement section of `incident-runbook.md`: revoke its access, remove schedules and integrations, deal with stored memory and logs, check what depended on it, tell its users, and update the inventory.

## 15. A 30, 60 And 90-Day Rollout

**Days 1 to 30: One project** at levels 0 and 1. Record the baseline, and run the checklist on varied tasks.

**Days 31 to 60: Prove the controls.** Repeat the stop drill, review the trail and the approval numbers, fix the rules that failed. Add users, tools or systems one at a time.

**Days 61 to 90: Decide with evidence.** Compare with the baseline, consider raising one well-understood action, and decide what to stop, continue and expand.

**Every quarter after that:** review rules, levels, measures, risk cards, inventory and vendors, and run a drill.

## 16. Protect The Codebase

The sections above reduce the risk of unwanted agent actions. This one helps you watch code quality over time. It applies if agents change software you must maintain, and you can add it after the first month.

Passing tests show that the checked behaviour works. They say little about whether the code is still easy to change, and the cost of poor design often appears long after the change that caused it. Agents can also reach a pass by weakening a test. One practitioner, Dex Horthy, who sells tools in this space, reports agent-built codebases starting to struggle after three to six months. That evidence is mostly experience, not controlled study, so treat it as a warning, not a measurement.

**Decide before code.** A short plan catches expensive mistakes while they are cheap. How much planning pays back is a judgement. The stages below follow Horthy's.

| Size of change | What to agree first |
|---|---|
| Small and well understood | Nothing extra. Let the agent do it, and review the diff |
| Medium | One short plan: the goal, the approach, the files that change, and how it will be tested |
| Large | Product intent, then system design, then program design: key types, signatures and file changes |

**Build thin slices.** Ask for one small end-to-end piece at a time, each testable by itself. Agents tend to plan layer by layer, which leaves little you can try end to end until late. Review each slice before building on it, so mistakes are easier to find and correct.

**Keep the promises in a feature map.** List the 5 to 10 flows that would hurt most if they broke. For each, write what must stay true, which code can break it, and what proves it. A check matches each changed file to the features that list it, runs their proof, and fails on files with no feature. It does not follow dependencies between features, or see changes outside the paths you map, so also run every proof on a schedule and after any dependency or CI change. The `feature-map` skill and script in `skills/feature-map/` do this. Add a line each time you fix a repeat bug, and let the map grow from real failures.

Two habits make a feature map trustworthy:

- **See each proof fail.** Break the feature on purpose in a throwaway branch and confirm the check catches it. A proof you have never seen fail has not proved anything.
- **List everything that can break a feature.** Include config and infrastructure. In our pilot, replaying a past bug, a security policy change broke a contact form while the form's own tests still passed.

**Guard the tests.** Treat deleting, skipping or editing a test, or weakening the map, as a change a person must approve. Protect tests and the map with required code-owner review. This only works if the agent has its own identity, is not a code owner, and nobody can bypass the rule. Own the `CODEOWNERS` file too. A team of one has no second approver, so such changes wait, as in section 4. Where you cannot set this up, write that down in `approval-matrix.md`. Where you can, keep a few black-box checks outside what the agent can edit.

**Put architecture rules in tools.** Enforce which modules may depend on which with an import or dependency checker. When you keep correcting the same pattern, turn it into a lint rule. Record complexity and duplication today, and flag any change that makes them worse for a person to look at. Do not use them as a hard gate. They are easy to game, and their link to maintainability is unproven.

**Keep the worker and the judge apart.** A separate reviewer, human or agent, is easier to make critical than the author is. An agent reviewer still leans generous and needs tuning, so it helps, and it does not replace a person.

**Keep reading the code.** Someone on your team must understand it well enough to fix it when the agent cannot. Automated review can reduce what people have to read, but do not remove them from anything you must maintain.

## What To Do Next

Adopt the files on one project, and change anything that does not fit how your team works. They are meant to be edited. `templates/examples/` shows the risk card and `AGENTS.md` filled in for an imaginary team.

## Appendix: Where The Limit Lives In Each Tool

Section 5 says to block the dangerous thing in the system. This is where each major coding agent keeps that setting, as read in the official docs on 1 November 2026. These move often, so check the linked page before relying on it.

| Agent | Where the limits live | Approvals off, for tests only | Docs |
|---|---|---|---|
| Claude Code | Permission modes and allow, ask and deny rules in settings; hooks that run before a tool call; a sandbox | `--dangerously-skip-permissions` | [Permissions](https://code.claude.com/docs/en/permissions) |
| OpenAI Codex CLI | `--sandbox read-only`, `workspace-write` or `danger-full-access`; `--ask-for-approval` in interactive `codex`; `approval_policy` in `config.toml` or `-c` | `--dangerously-bypass-approvals-and-sandbox`, or in `codex exec`, `-c approval_policy="never" --sandbox danger-full-access`. `codex exec` has no `-a` flag | [Approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security) |
| Cursor | Run Modes: Auto-review (default, a classifier), Allowlist, Run Everything. The docs say Auto-review is not a security boundary | Run Everything mode. `--force` (alias `--yolo`) allows commands unless denied, and lets print mode apply file edits. `--approve-mcps` is separate | [Run Modes](https://cursor.com/docs/agent/security/run-modes), [CLI parameters](https://cursor.com/docs/cli/reference/parameters), [MCP](https://cursor.com/docs/cli/mcp) |
| GitHub Copilot CLI | `--allow-tool` and `--deny-tool` patterns, path and URL checks; `--assisted-approval` is a classifier; the cloud agent is governed by repository settings and branch protection | `--allow-all`. `--allow-all-tools` alone still checks paths and URLs | [CLI reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference), [cloud agent](https://docs.github.com/en/copilot/concepts/copilot-surfaces/copilot-on-github) |
| Google Antigravity CLI | `toolPermission` in `~/.gemini/antigravity-cli/settings.json`: `strict`, `always-proceed`, `proceed-in-sandbox` or `request-review` | `--dangerously-skip-permissions` | [Headless](https://antigravity.google/docs/cli/headless), [CLI reference](https://antigravity.google/docs/cli/reference) |

Each tool also has a middle setting where an automated reviewer judges actions instead of a person: Claude Code's auto mode, Codex's auto review, Cursor's Auto-review, Copilot's assisted approval and Antigravity's auto agent mode. None of them is a limit in the sense of section 5, and none is "approvals off" for a test.

Two limits sit outside every tool and matter more: the credentials you hand the agent, and branch protection on the repository. Set those first.
