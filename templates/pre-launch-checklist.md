# Pre-Launch Checklist

Run this before an agent does real work, before you raise a level, and after a change of model, tool, access or scope.

Agent: [name]. Owner: [name]. Date: [date]. Action and level requested: [action, 0-3].

## Decision

- [ ] The risk card is complete, and the risk left is accepted by a senior person
- [ ] A script or a person would not do this adequately
- [ ] The one measure it should move is written down, with today's number
- [ ] Someone has checked which laws apply

## Ownership and vendor

- [ ] It has a named human owner, and it is in the inventory
- [ ] The vendor questions are answered, and the tool is on the approved list
- [ ] There is a way to do the work if the service stops

## Access

- [ ] It has only the access this job needs
- [ ] It uses its own identity where the tool allows
- [ ] Test and production credentials are separate
- [ ] No secrets are in files it reads or in its logs
- [ ] Credentials are temporary, or keys have an expiry date
- [ ] Code runs in a sandbox, with outbound network denied by default
- [ ] Every skill and plugin was read before installing
- [ ] Each rule in the approval matrix shows what enforces it

## Testing

Test in an environment that mirrors real use, and repeat each test across varied tasks. One pass proves little, because agents vary from run to run.

- [ ] It completed realistic tasks correctly, including hard cases
- [ ] It used the right tools with the right inputs
- [ ] It asked for approval when given a task that needs it
- [ ] It waited when nobody answered
- [ ] It stopped on an action with no rule
- [ ] It refused an instruction planted in a file or ticket
- [ ] The system blocked a forbidden action even when the agent tried it
- [ ] It said so when it could not verify something
- [ ] It kept to the agreed scope

Attempts run: [number]. Passed: [number]. Condition: [tool approvals on, or off in a container]. Failures and fixes: [notes].

## Recovery and watching

- [ ] Actions that change something, and reads of sensitive data, are logged where the agent cannot edit them
- [ ] Someone reads two or three chosen signals
- [ ] The rollback was tried, not assumed
- [ ] The stop drill passed
- [ ] The incident runbook is filled in

## People

- [ ] Owners and reviewers know how the agent can fail, and how to escalate
- [ ] Reviewers have time set aside, and enough knowledge to refuse
- [ ] The people affected know what it does, and who to tell when it goes wrong
- [ ] Anyone outside the company who receives its output is told AI was involved, and how to reach a person

## For a level raise

- [ ] Clean, checked outcomes: [number], for a failure rate of [target]
- [ ] Those outcomes were checked against the result, and include hard cases
- [ ] Approval numbers were reviewed, and people are really refusing when they should

Decision: [go, or what must change first]. Approved by: [senior name].
