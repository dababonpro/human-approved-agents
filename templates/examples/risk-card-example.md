# Risk Card: Worked Example

An imaginary team, used to show what a filled-in card looks like. Pellamrow Desk is a 14-person company running an internal tool that books meeting rooms and desks for its office tenants, with a shared support inbox. Nothing here describes a real company.

Agent: support-triage. Owner: Priya (engineering lead). Date: 2026-11-01. Next review: 2027-02-01.

Team risk tolerance, in one line: we accept wrong drafts that a person catches; we do not accept any message leaving the company, any customer record or ticket changed, or any personal data copied anywhere, without a named person approving it.

## Should this be an agent?

- Goal, and the one measure it should move: cut median first-response time on support tickets from 6 hours to under 2. Baseline: 6h 10m over the last 30 days.
- Could a script or a person do this adequately? Partly. Keyword rules tag about 60% of tickets correctly today. The rest need reading. A person does it now, late in the day.
- Who is affected, and how many? About 40 tenant staff a day, and the two support staff.
- Any vulnerable groups, decisions about people, or customers talking to it directly? No. Drafts go to a person, never to the tenant.
- Data involved: personal (names, work emails, booking references). No payment data; the inbox never holds card numbers.
- Does it read content from outside the team? Yes. Every ticket is untrusted content.
- Laws that may apply, and who checks them: data protection law in our market. Priya confirms with our accountant's compliance contact before go-live.
- Local context, such as languages or sector rules: tickets arrive in English and Malay. The agent drafts in the ticket's language, and a Malay speaker reviews those.

## Risks

Rate likelihood and severity as low, medium or high.

| Risk | Who could be harmed | Likelihood | Severity | Can it be undone? | What we will do: reduce, avoid, transfer or accept | Risk left afterwards |
|---|---|---|---|---|---|---|
| Agent acts on an instruction planted in a ticket, such as "forward this thread to this address" | Tenants whose data leaks | Medium | High | No | Avoid: the agent has no send access and no forwarding tool. Reduce: `AGENTS.md` treats ticket text as data, and the session check requires approval before any change. Test I1 before go-live | Low |
| Wrong tag sends an urgent ticket to the slow queue | A tenant waiting on a locked room | Medium | Medium | Yes, retag | Reduce: the agent proposes tags and a person approves each batch; "urgent" stays with a person | Low |
| Draft reply contains another tenant's booking details | Both tenants | Low | High | No, once sent | Reduce: the agent can read only the open ticket, not search the inbox. A person reads every draft before sending | Low |
| Personal data copied into the agent's notes or a commit | Tenants | Low | Medium | Partly, delete and rotate | Reduce: `AGENTS.md` secrets rule; canary address planted in the test inbox; P1 test | Low |
| Vendor outage during the morning peak | Support staff, tenants | Medium | Low | Yes | Accept: staff triage by hand as before. The old keyword rules stay switched on | Low |

## Risk to human involvement

Use the highest result. High likelihood moves a risk up one row.

| Overall risk | Default highest level | Human role |
|---|---|---|
| Low: low severity, easy to undo | Up to level 3, as a standing class | Person samples and can step in |
| Medium | Up to level 2 | Person approves actions |
| High: severe, or hard to undo | Level 1, or do not use an agent | Person decides |

This table is this playbook's default, not a published standard. A person affected, the sector or the law may call for a stricter choice. The Medium row allows more than the Five Eyes guidance, which limits agents to low-risk, non-sensitive tasks.

Overall risk: high, because an injected instruction could expose tenant data and that cannot be undone. Highest level allowed: 1 for drafts. Tagging is level 2, proposed in a batch and approved by a person, until the text the agent reads holds no personal data. Level 3 is not used on this card, because every ticket is both untrusted content and personal data, so the session check in `AGENTS.md` trips on every session.

## Acceptance

Risk left is accepted by: Daniel (founder). Date: 2026-11-01.
