# claude-config

Portable [Claude Code](https://claude.ai/code) configuration. Tracks only the authored config files — everything machine-generated is gitignored via an allowlist pattern.

**This repository is public.** Never commit secrets, employer-internal material, or work-specific skills here. `settings.local.json` is untracked for exactly this reason: permission rules saved by "always allow" record the full command text, including any credential typed inline.

## What's included

| Path | Purpose |
|------|---------|
| `CLAUDE.md` | Global instructions loaded into every conversation |
| `settings.json` | Permissions, hooks, enabled plugins, skill overrides, output style |
| `commands/*.md` | Custom slash commands |
| `hooks/` | Hook scripts referenced by `settings.json` |
| `scripts/` | Standalone utilities for analyzing Claude Code session logs |
| `skills/complete-minimum/` | Hand-authored, general-purpose skill |
| `statusline.sh` | Status line: context usage plus 5-hour / 7-day rate limits |

Anything `settings.json` references must be tracked too, or a fresh clone runs hooks that don't exist.

Not tracked:

- Other `skills/*` — synced from claude.ai (`skills/synced/`), or work-specific and kept in private repos.
- Sessions, project memory, plugin caches, history, and other machine-generated state.

### CLAUDE.md structure

- **Universal rules** (top) — git workflow, agent autonomy, task tracking with beads, and rules for durable references in committed artifacts.
- **Language-specific rules** (bottom) — scoped under headings like "When Working in Python Projects". Claude applies these contextually based on what's in the repo.

### Commands

| Command | Purpose |
|---------|---------|
| `/make-beads <plan>` | Convert an implementation plan into dependency-linked, parallel-safe Beads tickets, then audit them |
| `/audit-beads` | Fresh-eyes audit of all open beads, then fix the defects |
| `/drain-beads [filter]` | Driver loop: dispatch one worker sub-agent at a time to claim and complete ready beads until the queue is empty. Requires `claim-bead` on `PATH`. |
| `/merge-to-main` | Commit, merge main, test, fast-forward main from a worktree branch, push, close beads |

### Hooks

| Hook | Event | Purpose |
|------|-------|---------|
| `hooks/bd-global-memories.sh` | SessionStart | Prints cross-project `bd remember --global` memories into every session. No-op when `~/.beads-global` isn't set up. |

## Setup

### Fresh machine (no existing `~/.claude/`)

```bash
git clone git@github.com:gorgeguy/claude-config.git ~/.claude/
```

Claude Code will create its ephemeral directories alongside the tracked config on first run.

### Existing `~/.claude/` installation

```bash
cd ~/.claude
git init
git remote add origin git@github.com:gorgeguy/claude-config.git
git fetch origin
git checkout origin/main -- .
git reset HEAD  # unstage so you can review
```

Review the incoming files (`git diff` against your current config), then:

```bash
git checkout main 2>/dev/null || git checkout -b main
git branch --set-upstream-to=origin/main main
git add -A
git commit -m "sync with claude-config"
```

### Machine-specific overrides

Use `settings.local.json` (not tracked) for per-machine settings like machine-specific tool permissions. It layers on top of `settings.json`. Review it occasionally: it accumulates one rule per "always allow" click.

## Updating

After editing config in `~/.claude/`:

```bash
cd ~/.claude
git status          # confirm nothing private is about to be published
git add -A
git commit -m "update config"
git push
```

On other machines:

```bash
cd ~/.claude && git pull
```

## Reinstalling plugins

`settings.json` records which plugins are enabled, but the plugin code isn't tracked. After cloning on a new machine, install each plugin listed under `enabledPlugins`:

```bash
jq -r '.enabledPlugins | to_entries[] | select(.value) | .key' ~/.claude/settings.json \
  | xargs -n1 claude plugin install
```

Plugins from a third-party marketplace (listed under `extraKnownMarketplaces`) need that marketplace added first with `claude plugin marketplace add <owner/repo>`.
