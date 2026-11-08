# Risk Card

*From the Human-Approved Agent Playbook by DababonPro IT Solutions, licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Suggested credit if you adapt it: keep this line and note what you changed.*

One page per agent. Fill it in before you set a level, and update it after an incident or a change.

Agent: [name]. Owner: [name]. Date: [date]. Next review: [date].

Team risk tolerance, in one line: [what you will and will not accept]

## Should this be an agent?

- Goal, and the one measure it should move: [goal, measure, baseline]
- Could a script or a person do this adequately? [yes or no, and why]
- Who is affected, and how many? [staff, customers, public]
- Any vulnerable groups, decisions about people, or customers talking to it directly? [if yes, stop: this playbook does not cover it]
- Data involved: [none, internal, personal, secrets, regulated]
- Does it read content from outside the team? [yes or no]
- Laws that may apply, and who checks them: [for example data protection, name]
- Local context, such as languages or sector rules: [notes]

## Risks

Rate likelihood and severity as low, medium or high.

| Risk | Who could be harmed | Likelihood | Severity | Can it be undone? | What we will do: reduce, avoid, transfer or accept | Risk left afterwards |
|---|---|---|---|---|---|---|
| Example: agent acts on an injected instruction | [who] | [rating] | [rating] | [yes or no] | [limit, review] | [rating] |
| Example: wrong answer is trusted and passed on | [who] | [rating] | [rating] | [yes or no] | [review, sample] | [rating] |
| | | | | | | |

## Risk to human involvement

Use the highest result. High likelihood moves a risk up one row.

| Overall risk | Default highest level | Human role |
|---|---|---|
| Low: low severity, easy to undo | Up to level 3, as a standing class | Person samples and can step in |
| Medium | Up to level 2 | Person approves actions |
| High: severe, or hard to undo | Level 1, or do not use an agent | Person decides |

This table is this playbook's default, not a published standard. A person affected, the sector or the law may call for a stricter choice. The Medium row allows more than the Five Eyes guidance, which limits agents to low-risk, non-sensitive tasks.

Overall risk: [low, medium or high]. Highest level allowed: [0 to 3], because [reason].

## Acceptance

Risk left is accepted by: [senior name]. Date: [date].
