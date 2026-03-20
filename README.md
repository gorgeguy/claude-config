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
