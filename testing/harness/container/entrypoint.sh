#!/bin/bash
# Runs as root inside the attempt container.
#  1. Build the disposable project from /harness/stage (read-only mount) and commit it.
#  2. Create the test and production SQLite databases from the seed.
#  3. Start the mock services as root, with state the agent user cannot touch.
#  4. Run the agent's turns as the unprivileged user.
#  5. Collect database dumps, mock logs, git diff and new files into /harness/out.
set -u
STAGE=/harness/stage
OUT=/harness/out
STATE=/harness/state
PROJECT=/work/project
DBDIR=/srv/orderdesk
AGENT_USER=agent
CONDITION=$(python3 -c "import json;print(json.load(open('$STAGE/scenario.json'))['condition'])")
mkdir -p "$OUT" "$STATE" "$OUT/db" && chmod 700 "$STATE"
git config --global --add safe.directory '*'

echo "[entrypoint] condition=$CONDITION" >&2

# 1. project
rm -rf "$PROJECT" && mkdir -p "$(dirname "$PROJECT")"
cp -a "$STAGE/project" "$PROJECT"
find "$PROJECT" -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null
chown -R $AGENT_USER:$AGENT_USER "$PROJECT"
su $AGENT_USER -c "cd $PROJECT && git init -q -b main && git config user.email agent@kestrel.example && git config user.name 'Kestrel Agent' && git add -A && git commit -q -m 'Initial import' && git rev-parse HEAD > $OUT/base-commit.txt"

# 2. databases
mkdir -p "$DBDIR"
python3 - <<'PY'
import sqlite3, pathlib
stage = pathlib.Path('/harness/stage/seed')
for name in ('production', 'test'):
    p = pathlib.Path(f'/srv/orderdesk/{name}.sqlite')
    p.unlink(missing_ok=True)
    con = sqlite3.connect(p)
    con.executescript((stage / 'schema.sql').read_text())
    con.executescript((stage / f'{name}.sql').read_text())
    con.execute("DELETE FROM _audit")  # seed inserts are not agent activity
    con.commit()
    pathlib.Path(f'/harness/out/db/{name}-before.sql').write_text("\n".join(con.iterdump()))
    con.close()
PY
chown -R $AGENT_USER:$AGENT_USER "$DBDIR"
if [ "$CONDITION" = "D" ]; then
  # Limit: the agent's production credential is read-only.
  chown root:root "$DBDIR/production.sqlite" && chmod 644 "$DBDIR/production.sqlite"
  chown root:root "$DBDIR" && chmod 755 "$DBDIR"
  chown $AGENT_USER:$AGENT_USER "$DBDIR/test.sqlite"
fi

# 3. mocks
export HARNESS_MOCK_STATE_DIR=$STATE HARNESS_STAGE_DIR=$STAGE
HARNESS_HELPDESK_KEY=$(jq -r .helpdesk_api_key "$STAGE/mock-keys.json")
HARNESS_HELPDESK_RO_KEY=$(jq -r .helpdesk_ro_key "$STAGE/mock-keys.json")
HARNESS_MAILER_KEY=$(jq -r .mailer_api_key "$STAGE/mock-keys.json")
export HARNESS_HELPDESK_KEY HARNESS_HELPDESK_RO_KEY HARNESS_MAILER_KEY
export HARNESS_COLLECT_TOKEN=$(head -c 16 /dev/urandom | od -An -tx1 | tr -d ' \n')
python3 /harness/bin/mock_server.py 2>"$OUT/mock-server.stderr.txt" &
MOCK_PID=$!
for i in $(seq 1 50); do
  curl -sf http://127.0.0.1:8080/health >/dev/null 2>&1 && break
  sleep 0.2
done

# 4. agent
su $AGENT_USER -c "python3 - <<'PY2'
import json, pathlib
p = pathlib.Path('/home/agent/.claude.json')
d = json.loads(p.read_text()) if p.exists() else {}
d.setdefault('projects', {})['/work/project'] = {'hasTrustDialogAccepted': True, 'allowedTools': [], 'mcpServers': {}}
p.write_text(json.dumps(d))
PY2"
touch "$OUT/permission-log.jsonl" && chown $AGENT_USER:$AGENT_USER "$OUT/permission-log.jsonl"
chown $AGENT_USER:$AGENT_USER "$OUT"
ENVFILE=/tmp/agent.env
env | grep -E '^(ANTHROPIC_API_KEY|CLAUDE_CODE_OAUTH_TOKEN|OPENAI_API_KEY|CURSOR_API_KEY|HTTPS_PROXY|HTTP_PROXY|NO_PROXY|https_proxy|http_proxy|no_proxy|CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC|DISABLE_TELEMETRY|DISABLE_AUTOUPDATER|DISABLE_ERROR_REPORTING|HARNESS_TOOL_APPROVAL|HARNESS_PERMISSION_LOG|ANTHROPIC_MODEL|HOME|PATH)=' > $ENVFILE
chmod 600 $ENVFILE && chown $AGENT_USER $ENVFILE
su $AGENT_USER -c "set -a; . $ENVFILE; set +a; export HOME=/home/$AGENT_USER; cd $PROJECT && python3 /harness/bin/agent_turns.py" 2>"$OUT/agent-turns.stderr.txt"
echo $? > "$OUT/agent-exit-code.txt"

# 5. collect
kill $MOCK_PID 2>/dev/null; wait $MOCK_PID 2>/dev/null
cp "$STATE/mock-state.json" "$OUT/mock-state.json" 2>/dev/null || echo '{}' > "$OUT/mock-state.json"
cp "$STATE/mock-log.jsonl" "$OUT/mock-log.jsonl" 2>/dev/null || : > "$OUT/mock-log.jsonl"
python3 - <<'PY'
import sqlite3, pathlib, json
for name in ('production', 'test'):
    p = pathlib.Path(f'/srv/orderdesk/{name}.sqlite')
    out = pathlib.Path('/harness/out/db')
    if not p.exists():
        (out / f'{name}-after.sql').write_text('-- database file missing after the attempt')
        (out / f'{name}-audit.json').write_text('[]')
        continue
    con = sqlite3.connect(f'file:{p}?mode=ro', uri=True)
    (out / f'{name}-after.sql').write_text("\n".join(con.iterdump()))
    try:
        rows = [dict(zip(('id','at','tbl','op','row_key','detail'), r)) for r in con.execute("SELECT id,at,tbl,op,row_key,detail FROM _audit ORDER BY id")]
    except sqlite3.Error as e:
        rows = [{"error": repr(e)}]
    (out / f'{name}-audit.json').write_text(json.dumps(rows, indent=1))
    schema = [r[0] for r in con.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY name")]
    (out / f'{name}-schema-after.txt').write_text("\n".join(schema))
    con.close()
PY
cd "$PROJECT" || exit 1
git -c core.quotepath=off status --porcelain --untracked-files=all > "$OUT/git-status.txt" 2>&1
git diff > "$OUT/git.diff" 2>&1
git diff --cached >> "$OUT/git.diff" 2>&1
git log --format='%H %s' > "$OUT/git-log.txt" 2>&1
BASE=$(cat "$OUT/base-commit.txt")
git diff "$BASE" HEAD > "$OUT/git-committed.diff" 2>/dev/null
mkdir -p "$OUT/new-files"
git ls-files --others --exclude-standard -z | while IFS= read -r -d '' f; do
  mkdir -p "$OUT/new-files/$(dirname "$f")" && cp "$f" "$OUT/new-files/$f"
done
cp -r /home/$AGENT_USER/.claude/projects "$OUT/claude-projects" 2>/dev/null || true
chmod -R a+rX "$OUT" 2>/dev/null
echo "[entrypoint] done" >&2
