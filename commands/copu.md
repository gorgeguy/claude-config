---
description: Commit and push changes with generated message
allowed-tools:
  - Bash(git add:*)
  - Bash(git status:*)
  - Bash(git commit:*)
  - Bash(git push:*)
argument-hint: "[context-for-commit-msg]"
model: haiku
---

# Commit and Push

1. Analyze git diff to understand changes
2. Generate appropriate commit message (Conventional Commits format)
3. Stage all changes with `git add -A`
4. Commit with generated message
5. Push to current branch

Execute all steps in a single response.

Optional: $ARGUMENTS can provide context for the commit message.
