#!/usr/bin/env bash
# SessionStart hook — surface bd cross-project "global" memories in every project.
#
# Why this exists:
#   `bd remember --global` writes to the project-agnostic `beads_global` store on
#   the shared Dolt server, but `bd prime` only reads the LOCALLY-connected
#   database's memories — it has no path that reads `beads_global`. So global
#   memories never appear at session start on their own. This hook closes that
#   gap by reading the global store directly and printing it into session context.
#
# How it reaches the global store on bd 1.0.4:
#   bd's project-identity guard refuses to connect when the workspace's
#   metadata.json project_id != the connected DB's project_id, and `beads_global`
#   carries the all-zeros sentinel id. We therefore query through a dedicated
#   "sentinel workspace" (~/.beads-global) whose metadata.json project_id IS the
#   all-zeros sentinel, so the guard passes. See `bd -C ~/.beads-global`.
#
# Safety:
#   Degrades silently — emits nothing (exit 0) if the shared server is down or the
#   global store is empty, so it never disrupts session start.

set -u

WORKSPACE="${HOME}/.beads-global"

# No sentinel workspace -> nothing to do (keeps this hook a no-op on machines
# that haven't set up the global store).
[ -f "${WORKSPACE}/.beads/metadata.json" ] || exit 0

out=$(BEADS_DOLT_SHARED_SERVER=1 bd -C "${WORKSPACE}" --global memories 2>/dev/null) || exit 0

case "${out}" in
  ""|*"No memories"*)
    # Empty store or unreachable server: stay quiet.
    exit 0
    ;;
  *)
    printf '\n## Global Memories (cross-project, via `bd remember --global`)\n\n%s\n' "${out}"
    ;;
esac
