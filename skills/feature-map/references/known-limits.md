# Known Limits

An honest list of what the check does not catch, so nobody mistakes a green result for proof.

- **Cleverly hidden skips.** Skip patterns are a tripwire. An aliased skip, or a marker in an unusual form, can get through. Extend `skip_patterns` for your language.
- **Test config.** A change to `pytest.ini`, `conftest.py` or similar can deselect tests with no change to a test file. Protect those files with code owners.
- **Weak tests from the start.** The check only sees changes. A new test that asserts nothing passes. That is why you break each feature on purpose, and repeat that on a schedule.
- **Dependencies between features.** A change to one feature can break another that does not list that file. Run every proof on a schedule.
- **Outside `mapped_paths`.** Dependency files, CI, feature flags, cloud settings and third-party APIs are invisible to it.
- **Untracked test files.** With `--worktree`, a skip marker in a new untracked test is not read. CI sees it after commit.
- **Timeouts.** A proof's child process can outlive the script's timeout, so set a job timeout in CI.
- **The check script itself.** A change can edit it, which is why CI runs the base branch's copy, and code owners protect it.
- **Noise.** Any edited test line needs a person. That is deliberate, and it costs reviewer time.
