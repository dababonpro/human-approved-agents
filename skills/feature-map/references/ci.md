# Running The Check In CI

Copy `scripts/check_feature_map.py` into the repo, for example under `tools/`, and record which version you copied. CI needs Python 3.11 or later, and no packages. Then make the check a required status. This setup has not yet been run on GitHub, so try it on a test repository first.

## GitHub Actions

```yaml
name: feature-map
on:
  pull_request:
    branches: [main]
  schedule:
    - cron: "0 3 * * *"

permissions:
  contents: read

jobs:
  check:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@<full commit SHA>
        with:
          fetch-depth: 0
          persist-credentials: false
      - uses: actions/setup-python@<full commit SHA>
        with:
          python-version: "3.12"
      # Add your project's setup here, because proofs run your tests.
      - name: Check the feature map
        shell: bash
        env:
          BASE_SHA: ${{ github.event.pull_request.base.sha }}
        run: |
          # Use the base branch's copy of the check, so a change cannot edit its own judge.
          # On first adoption the base has no script, so copy it from the branch once.
          git show "$BASE_SHA:tools/check_feature_map.py" > "$RUNNER_TEMP/check_feature_map.py" || cp tools/check_feature_map.py "$RUNNER_TEMP/check_feature_map.py"
          python "$RUNNER_TEMP/check_feature_map.py" --base "$BASE_SHA" --run --promises-approved | tee -a "$GITHUB_STEP_SUMMARY"
          exit "${PIPESTATUS[0]}"

  all-proofs:
    # The check does not follow dependencies between features, so run every proof nightly.
    if: github.event_name == 'schedule'
    runs-on: ubuntu-latest
    timeout-minutes: 60
    steps:
      - uses: actions/checkout@<full commit SHA>
        with:
          persist-credentials: false
      # Add your project's setup, then run each proof command from features.toml.
```

Pin actions to a full commit SHA, not a moving tag. Set a job timeout, because a proof's child process can outlive the script's own timeout.

Proofs are commands from the change being tested. Do not run them with `pull_request_target`. `pull_request` withholds secrets only from forks. A branch in your own repository can read every secret a workflow references, and can edit the workflow. So reference no secrets in the job that runs proofs, set `persist-credentials: false` on checkout, do not use self-hosted runners, and require code-owner review on `.github/`.

## Approval

The approval is a required code-owner review of the latest push. CI passes `--promises-approved`, so a weakening shows as a note in the job summary for that reviewer, instead of failing. Turn on all of these:

- Require review from code owners
- Dismiss stale approvals when new commits are pushed
- Require approval of the most recent push
- Do not allow bypassing, including by administrators

If you cannot turn these on, drop `--promises-approved`, so the check keeps failing and a person has to act. Do not use a label as approval. Anyone with write access can add one, which includes any agent that can push a branch.

## Protect The Map

Add a `CODEOWNERS` file:

```text
/features.toml      @your-org/owners
/tools/             @your-org/owners
/tests/             @your-org/owners
/.github/           @your-org/owners
/pytest.ini         @your-org/owners
/conftest.py        @your-org/owners
/jest.config.*      @your-org/owners
```

Own the `CODEOWNERS` file too, which `/.github/` covers if it lives there. Test config files are listed because they can deselect tests with no change to a test file.

This only works if the agent has its own identity and is not a code owner. An agent using a person's token acts as that person. A team of one has no second approver, so changes that weaken the map wait until there is one. Check what your plan allows, as code-owner rules can depend on it. Other platforms need their own version of these settings.
