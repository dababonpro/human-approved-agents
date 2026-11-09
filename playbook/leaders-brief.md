# A Leader's Brief

*From the Human-Approved Agent Playbook by DababonPro IT Solutions, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).*

For founders, managers and sponsors who decide whether a team uses AI agents. It covers the decisions that are yours to make. Your technical lead uses the [full playbook](playbook.md) and the [templates](../templates/) to carry them out.

This is practical guidance. It is not legal advice, and following it does not make you compliant with any law or framework.

## Why Agents Need A Decision From You

Most AI policies cover what people may do with AI. An agent is different, because it acts: it runs commands, changes records and sends messages, sometimes many times a minute. When it gets something wrong, the mistake is already done. Someone has to decide in advance what it may do alone, and who answers for it.

## Five Decisions That Are Yours

1. **Who owns each agent.** Every agent has one named person who answers for it. If nobody owns it, it does not run. *Record: [agent inventory](../templates/agent-inventory.md).*
2. **How much risk you accept.** Write one line on the risk your team will tolerate, and name who accepts what remains for each agent. That person should be senior enough to own the outcome. *Record: [risk card](../templates/risk-card.md).*
3. **What needs a person's yes.** Decide which actions always need approval. At a minimum: deleting data, deploying, changing permissions, spending money, and sending anything outside the company. *Record: [approval matrix](../templates/approval-matrix.md).*
4. **What it must improve.** Name the one measure the agent should move, record today's number, and set a date to check it. If it does not move, change the agent or remove it. *Guide: [section 10](playbook.md#10-measure-whether-it-helped).*
5. **Which tools are allowed.** Keep a short list of approved tools, and ask vendors how they handle your data before anyone connects one. *Guide: [section 12](playbook.md#12-check-your-vendors).*

## Questions To Ask Your Team

- Can you list every agent we use, and who owns each one?
- What can each one do without asking a person?
- If an agent ignores its instructions, what stops it? Rules it reads are not enough; ask which limits are built into the systems themselves.
- When did someone last try stopping it?
- When an agent reports "done", who or what checks that it really is?
- Which number has it moved since we started?

A team that can answer these in a few minutes is in control. Missing answers are the work.

## Start Small

Begin with one lower-risk project, with the agent reading and drafting only, in a test environment. The technical lead needs about four hours for the [first day](playbook.md#start-here-your-first-day). Then:

| Days | Goal | What you will see |
|---|---|---|
| 1 to 30 | One project, low levels | A baseline number and the first filled-in templates |
| 31 to 60 | Prove the controls work | A stop drill, approval numbers, and fixes to the rules that failed |
| 61 to 90 | Decide with evidence | A comparison with the baseline, and a decision to stop, continue or expand |

Expand only after the pilot has survived real work. Spreading it across the company first teaches you nothing.

## What The Evidence Does And Does Not Say

- There is no proven standard for how much freedom to give an AI agent. Least privilege and the ability to stop a system rest on established standards. Most of the rest is reasoned guidance or this playbook's judgement, and [the evidence page](evidence.md) says which is which.
- National cyber security agencies advise using agents only for low-risk, non-sensitive work. This playbook allows more, with approvals and limits, and says so.
- The playbook's own tests ran one coding agent in one mock project. Automated checks found far fewer risky actions with the playbook's files than without them. The rules and scoring were tuned along the way, most passes still await a person's review, and a later check of the flagged attempts found one that failed its review question. Treat the results as a reason to run your own pilot, not as proof that it will work for your team. The [dated record](../testing/results/2026-11-05-claude-code.md) has the details.

## Not Covered

Agents that talk to customers on their own, agents that control a desktop or browser, multi-agent systems, and agents that screen, rank or decide about people. These need more than this playbook.
