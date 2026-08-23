#!/bin/bash
# Copy the native executables the REPL runs from a ladder checkout into
# bin/ (gitignored), stamping provenance. Default source is the repo
# clone; export REPL_NATIVES_SRC to take a sandbox's branch build
# instead. The subject (subjects/fib.codex) is a committed file, not a
# copy -- it is the FIB chapter from ast/gen_fib_harness.py.
set -euo pipefail
SRC="${REPL_NATIVES_SRC:-$HOME/showell_repos/codex-zig-ladder}"
cd "$(dirname "$0")/.."
mkdir -p bin
cp "$SRC/native/codexir" "$SRC/native/zigemit" bin/
{ echo "src      $SRC"
  echo "copied   $(date -u +%FT%TZ)"
  echo "ladder   $(git -C "$SRC" rev-parse --short HEAD 2>/dev/null || echo '?')"
  echo "codex    $(git -C "$SRC" rev-parse --short HEAD:../codex 2>/dev/null || echo 'see sandbox MANIFEST')"
  # Same stamp tiers_run.py prints, so a REPL run is attributable to the
  # exact build a tier verdict named.
  echo "natives  $(cat bin/codexir bin/zigemit | sha256sum | cut -c1-12)"
} > bin/PROVENANCE
cat bin/PROVENANCE
