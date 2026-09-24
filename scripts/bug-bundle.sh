#!/usr/bin/env bash
# Gather a sanitized bug report bundle for Claude Code / Anthropic.
#
# Usage:
#   bug-bundle.sh <session-id-or-jsonl-path> [output-dir]
#
# Produces:
#   <output-dir>/claude-bug-<timestamp>/
#     environment.txt    — CLI version, OS, shell, model
#     settings.json      — global settings (not the project's local one)
#     hooks.json         — extracted from settings
#     session.jsonl      — copy of the offending session log
#     session-timing.txt — output of session-timing.py on it
#     trend.txt          — output of session-trend.py for context
#     processes.txt      — current ps state (in case of live hang)
#     README.md          — what's in the bundle and how to interpret

set -euo pipefail

INPUT="${1:?usage: bug-bundle.sh <session-id-or-jsonl-path> [output-dir]}"
OUT_BASE="${2:-$HOME/Desktop}"
TS=$(date +%Y%m%d-%H%M%S)
OUT="$OUT_BASE/claude-bug-$TS"
mkdir -p "$OUT"

# Resolve input to a JSONL path. Use -print -quit to avoid SIGPIPE under pipefail.
if [[ -f "$INPUT" ]]; then
    SESSION_PATH="$INPUT"
else
    SESSION_PATH=$(find "$HOME/.claude/projects" -name "${INPUT}*.jsonl" -print -quit)
fi
[[ -z "${SESSION_PATH:-}" ]] && { echo "session not found: $INPUT" >&2; exit 1; }

cp "$SESSION_PATH" "$OUT/session.jsonl"
cp "$HOME/.claude/settings.json" "$OUT/settings.json" 2>/dev/null || true

{
    echo "=== Claude Code version ==="
    claude --version 2>&1 || echo "(claude CLI not in PATH)"
    echo
    echo "=== OS ==="
    uname -a
    sw_vers 2>/dev/null || true
    echo
    echo "=== Shell ==="
    echo "SHELL=$SHELL"
    echo "TERM=$TERM"
    echo
    echo "=== Session metadata ==="
    echo "session_path=$SESSION_PATH"
    echo "size=$(wc -c < "$SESSION_PATH") bytes"
    echo "mtime=$(stat -f '%Sm' "$SESSION_PATH" 2>/dev/null || stat -c '%y' "$SESSION_PATH")"
} > "$OUT/environment.txt"

# Extract hooks specifically (most relevant config)
python3 -c "
import json
with open('$HOME/.claude/settings.json') as f:
    d = json.load(f)
print(json.dumps(d.get('hooks', {}), indent=2))
" > "$OUT/hooks.json" 2>/dev/null || echo "{}" > "$OUT/hooks.json"

# Run timing analysis on the session
python3 "$HOME/.claude/scripts/session-timing.py" "$SESSION_PATH" --top 30 \
    > "$OUT/session-timing.txt" 2>&1 || true

# Run trend analysis for context (project containing the session).
# Use --project-slug to bypass the slug↔path inversion (which is ambiguous because
# both '/' and '.' encode to '-' in Claude Code's slug scheme).
PROJ_SLUG=$(basename "$(dirname "$SESSION_PATH")")
# Use --project-slug=VALUE form: argparse interprets a bare leading '-' in VALUE
# as another flag if passed as two separate words.
python3 "$HOME/.claude/scripts/session-trend.py" "--project-slug=$PROJ_SLUG" --last 30 \
    > "$OUT/trend.txt" 2>&1 || true

# Capture current process state (useful if filing during a live hang).
# Buffer ps output to a temp file so head/grep can't SIGPIPE the producer
# (would trip `set -o pipefail` and abort the script).
PS_TMP=$(mktemp)
ps -eo pid,ppid,etime,pcpu,pmem,command > "$PS_TMP"
head -1 "$PS_TMP" > "$OUT/processes.txt"
grep -E "claude|node|python|pyright|uv" "$PS_TMP" | grep -v grep \
    >> "$OUT/processes.txt" || true
rm -f "$PS_TMP"

cat > "$OUT/README.md" << EOF
# Claude Code bug bundle

Generated: $(date -Iseconds)

## Files
- \`environment.txt\` — CLI version, OS, shell
- \`settings.json\` — global Claude Code settings
- \`hooks.json\` — extracted hook configuration
- \`session.jsonl\` — full session log (the suspected bad session)
- \`session-timing.txt\` — per-tool durations + slowest calls
- \`trend.txt\` — comparison against last 30 sessions in this project
- \`processes.txt\` — current process state (if captured during live hang)

## What to look for
1. In \`session-timing.txt\`: top slowest calls. Look for repeated polling or long blocks.
2. In \`trend.txt\`: \`bg\` (backgrounding count) and \`task_out\` (TaskOutput usage) columns
   — these mark sessions where the harness auto-backgrounded long commands.
3. In \`session.jsonl\`: search for \`"running in background"\` in tool_result content,
   then look at the model's next actions to see whether it used \`Read\` (good) or
   \`TaskOutput\` (regression).
EOF

echo "Bundle written to: $OUT"
ls -la "$OUT"
