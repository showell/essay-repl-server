#!/bin/bash
# Copy the native executables + the subject the REPL compiles from a
# ladder checkout into bin/ and subjects/ (both gitignored), stamping
# provenance. Default source is the repo clone; export REPL_NATIVES_SRC
# to take a sandbox's branch build instead.
set -euo pipefail
SRC="${REPL_NATIVES_SRC:-$HOME/showell_repos/codex-zig-ladder}"
cd "$(dirname "$0")/.."
mkdir -p bin subjects
cp "$SRC/native/codexir" "$SRC/native/zigemit" bin/
cp "$SRC/ast/fib-subject.codex" subjects/
{ echo "src      $SRC"
  echo "copied   $(date -u +%FT%TZ)"
  echo "ladder   $(git -C "$SRC" rev-parse --short HEAD 2>/dev/null || echo '?')"
  echo "codex    $(git -C "$SRC" rev-parse --short HEAD:../codex 2>/dev/null || echo 'see sandbox MANIFEST')"
  # Same stamp tiers_run.py prints, so a REPL run is attributable to the
  # exact build a tier verdict named.
  echo "natives  $(cat bin/codexir bin/zigemit | sha256sum | cut -c1-12)"
} > bin/PROVENANCE
cat bin/PROVENANCE
