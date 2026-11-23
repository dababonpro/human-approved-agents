# Attempt container for the agent playbook harness.
# The same image also runs the egress proxy (different entrypoint).
FROM node:22-bookworm-slim

ARG CLAUDE_CODE_VERSION=2.1.316
# Codex: the newest stable release at least two weeks old on 2026-11-08. No full Codex run has completed with this
# harness yet, so treat the Codex adapter as untested on this version.
ARG CODEX_VERSION=0.164.0
ARG OPENCODE_VERSION=1.19.3
ARG INSTALL_CURSOR=0
ARG INSTALL_AGY=0

RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 python3-venv git curl ca-certificates sqlite3 ripgrep jq procps \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g @anthropic-ai/claude-code@${CLAUDE_CODE_VERSION} @openai/codex@${CODEX_VERSION} opencode-ai@${OPENCODE_VERSION} \
    && npm cache clean --force

# Cursor CLI is an official installer script; off by default. Build with --build-arg INSTALL_CURSOR=1 to include it.
RUN if [ "$INSTALL_CURSOR" = "1" ]; then curl -fsS https://cursor.com/install | bash && cp -a /root/.local/bin/agent /usr/local/bin/agent; fi

# Antigravity CLI is an official installer script with no version-pin option; off by default.
# Build with --build-arg INSTALL_AGY=1 to include it. Each run records `agy --version` in record.json.
RUN if [ "$INSTALL_AGY" = "1" ]; then curl -fsSL https://antigravity.google/cli/install.sh | bash -s -- --dir /usr/local/bin; fi

RUN useradd -m -u 1001 -s /bin/bash agent \
    && mkdir -p /home/agent/.claude /home/agent/.codex /home/agent/.config/opencode /home/agent/.gemini/antigravity-cli /work \
    && echo '{"hasCompletedOnboarding": true, "bypassPermissionsModeAccepted": true}' > /home/agent/.claude.json \
    && echo '{"skipDangerousPermissionsAcceptance": true}' > /home/agent/.claude/settings.json \
    && echo '{"modelProvider": "gemini"}' > /home/agent/.gemini/antigravity-cli/settings.json \
    && chown -R agent:agent /home/agent /work

# The harness's own files live in /srv/ops, readable by root only, under names that do not say "harness" or
# "mock": an agent that runs `ls /`, `ps` or `env` should see an ordinary company machine, not a test rig.
# The approval stand-in and the dry agent run as the agent user, so they sit in a readable folder of their own.
COPY mock_server.py /srv/ops/bin/services.py
COPY agent_turns.py /srv/ops/bin/runner.py
COPY egress_proxy.py /srv/ops/bin/egress_proxy.py
COPY entrypoint.sh /srv/ops/bin/start.sh
COPY permission_mcp.py /usr/local/lib/approvals/approvals_mcp.py
COPY dry_agent.py /usr/local/lib/dry-agent/dry_agent.py
RUN for f in /srv/ops/bin/* /usr/local/lib/approvals/*.py /usr/local/lib/dry-agent/*.py; do sed -i 's/\x0D$//' "$f"; done \
    && chmod 755 /srv/ops/bin/*.sh /srv/ops/bin/*.py /usr/local/lib/approvals/*.py /usr/local/lib/dry-agent/*.py \
    && chown -R root:root /srv/ops && chmod 700 /srv/ops \
    && mkdir -p /var/log/approvals && chown agent:agent /var/log/approvals

ENV CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 DISABLE_TELEMETRY=1 DISABLE_AUTOUPDATER=1 DISABLE_ERROR_REPORTING=1 \
    OPENCODE_DISABLE_AUTOUPDATE=1 OPENCODE_DISABLE_MODELS_FETCH=1 OPENCODE_DISABLE_LSP_DOWNLOAD=1 \
    OPENCODE_DISABLE_CLAUDE_CODE=1 OPENCODE_DISABLE_DEFAULT_PLUGINS=1 \
    AGY_DISABLE_AUTOUPDATE=1 AGY_DISABLE_TELEMETRY=1
WORKDIR /work
ENTRYPOINT ["/srv/ops/bin/start.sh"]
