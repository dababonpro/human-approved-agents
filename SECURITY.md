# Security

Report a security problem through GitHub's private vulnerability reporting on this repository. Please do not open a public issue for one.

## Fake Secrets In The Test Harness

`testing/harness/project-template/config/` holds a fake `.env` and a fake signing key. They are planted canaries that the test harness watches for leaks. They open nothing, so a secret scanner flagging them is a false alarm.

## Using These Files

The rules in `templates/AGENTS.md` guide an agent. They are not a security control, and prompt injection may never be fully solved. Back anything that matters with the limits in section 5 of the playbook.

The test harness runs coding agents with their approvals off. Run it only in the disposable container it provides, with no real credentials or data.
