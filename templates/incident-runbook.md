# Agent Incident Runbook

Fill this in before you need it. Keep it where people can find it during a bad day.

Agent owner: [name, contact]. Backup: [name, contact]. Security or data contact: [name, contact]. Vendor support: [contact].

## What counts as an incident

- Harm or possible harm to data, money, people or service
- An agent acting outside its limits or instructions
- A leaked secret or personal data
- A vendor outage or security incident affecting your work

Severity: **Low** is contained with no harm. **Medium** needs repair or affects a person. **High** affects customers, personal data, money or production. Log near misses as well.

## 1. Notice

- Signals we watch: [denied calls, failures, unusual access, cost]
- Who sees them: [name]

## 2. Stop

Do this first, once you have checked whether stopping halfway leaves a batch half-done.

- Revoke the key: [where and how]
- Disable the schedule: [where and how]
- Turn off the integration: [where and how]

## 3. Contain

- What did the agent change? Check [audit log, git history, tickets].
- Is anything downstream using the bad output? Pause it.
- Keep the logs. Do not clean anything up yet.
- Was personal data, a secret or a customer affected? Tell [contact], and check your legal duties to report it.
- Rotate any secret the agent may have exposed.

## 4. Repair

- Roll back: [how]
- Check the repair the same way you would check any change: look at the result.
- Tell the people affected, in plain words.
- If the vendor is down, switch to the manual method: [how]

## 5. Learn

Write this within a week, and add it to the incident log. Do not name someone to blame. Name the rule, limit or check that was missing.

| Question | Answer |
|---|---|
| What happened, and how severe was it? | |
| When did it start, and when did we notice? | |
| What did it affect? | |
| Why did it happen? | |
| Which rule, limit or check changes now? | |
| Does the risk card or level change? | |
| Who owns that change, and by when? | |

## Stop drill

Run this before go-live, after any change to access or tools, and on your own schedule: [how often].

- [ ] Someone other than the owner stopped the agent using this page
- [ ] It stopped within [target time]
- [ ] It could be restarted safely
- [ ] This page was corrected where it was wrong

Last drill: [date, who, time taken].

## Retiring an agent

- [ ] Revoke keys and accounts
- [ ] Remove schedules, hooks and integrations
- [ ] Decide what happens to stored memory, notes and logs
- [ ] Check what depended on it, upstream and downstream
- [ ] Tell its users, and say what replaces it
- [ ] Update the inventory and close the risk card
