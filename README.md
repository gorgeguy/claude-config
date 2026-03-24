# claude-config

Portable [Claude Code](https://claude.ai/code) configuration. Tracks only the authored config files — everything machine-generated is gitignored via an allowlist pattern.

## What's included

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Global instructions loaded into every conversation |
| `settings.json` | Permissions, hooks, enabled plugins, output style |
| `commands/*.md` | Custom slash commands |
| `statusline.sh` | Custom status line script |

Everything else in `~/.claude/` (sessions, debug logs, telemetry, plugin caches, project memory, etc.) is machine-generated and excluded.

### CLAUDE.md structure

The global `CLAUDE.md` has two sections:

- **Universal rules** (top) — git workflow, agent autonomy, coding preferences, port management. These apply to every project.
- **Language-specific rules** (bottom) — scoped under headings like "When Working in Python Projects". Claude applies these contextually based on what's in the repo.

### Available commands

| Command | Purpose |
|---------|---------|
| `/create-python-project` | Scaffold a new Python project with uv, ruff, pytest |
| `/copu` | Commit and push with auto-generated message |
| `/merge-to-main` | Run tests, commit, and merge branch to main |
| `/plan-to-beads` | Convert implementation plans to Beads tickets |
| `/cr-step-1` | Bug-finder agent (code review step 1) |
| `/cr-step-2` | Adversarial review agent (code review step 2) |
| `/cr-step-3` | Referee agent (code review step 3) |

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

Use `settings.local.json` (not tracked) for per-machine settings like machine-specific tool permissions. It layers on top of `settings.json`.

## Updating

After editing config in `~/.claude/`:

```bash
cd ~/.claude
git add -A
git commit -m "update config"
git push
```

On other machines:

```bash
cd ~/.claude && git pull
```

## Reinstalling plugins

`settings.json` records which plugins are enabled, but the plugin binaries aren't tracked. After cloning on a new machine, reinstall plugins with:

```bash
claude plugins install
```
