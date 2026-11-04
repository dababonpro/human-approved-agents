# Attempt container for the agent playbook harness.
# The same image also runs the egress proxy (different entrypoint).
FROM node:22-bookworm-slim

ARG CLAUDE_CODE_VERSION=2.1.316
ARG CODEX_VERSION=0.166.0-alpha.5.1
ARG OPENCODE_VERSION=1.19.3
ARG INSTALL_CURSOR=0

RUN apt-get update && apt-get install -y --no-install-recommends \
      python3 python3-venv git curl ca-certificates sqlite3 ripgrep jq procps \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g @anthropic-ai/claude-code@${CLAUDE_CODE_VERSION} @openai/codex@${CODEX_VERSION} opencode-ai@${OPENCODE_VERSION} \
    && npm cache clean --force

# Cursor CLI is an official installer script; off by default. Build with --build-arg INSTALL_CURSOR=1 to include it.
RUN if [ "$INSTALL_CURSOR" = "1" ]; then curl -fsS https://cursor.com/install | bash && cp -a /root/.local/bin/agent /usr/local/bin/agent; fi

RUN useradd -m -u 1001 -s /bin/bash agent \
    && mkdir -p /home/agent/.claude /home/agent/.codex /home/agent/.config/opencode /work \
    && echo '{"hasCompletedOnboarding": true, "bypassPermissionsModeAccepted": true}' > /home/agent/.claude.json \
    && echo '{"skipDangerousPermissionsAcceptance": true}' > /home/agent/.claude/settings.json \
    && chown -R agent:agent /home/agent /work

COPY mock_server.py permission_mcp.py egress_proxy.py agent_turns.py dry_agent.py /harness/bin/
COPY entrypoint.sh /harness/bin/entrypoint.sh
RUN for f in /harness/bin/*; do sed -i 's/\x0D$//' "$f"; done && chmod +x /harness/bin/*.sh /harness/bin/*.py

ENV CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 DISABLE_TELEMETRY=1 DISABLE_AUTOUPDATER=1 DISABLE_ERROR_REPORTING=1 \
    OPENCODE_DISABLE_AUTOUPDATE=1 OPENCODE_DISABLE_MODELS_FETCH=1 OPENCODE_DISABLE_LSP_DOWNLOAD=1 \
    OPENCODE_DISABLE_CLAUDE_CODE=1 OPENCODE_DISABLE_DEFAULT_PLUGINS=1
WORKDIR /work
ENTRYPOINT ["/harness/bin/entrypoint.sh"]
