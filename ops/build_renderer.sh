#!/bin/bash
# Build bin/render_note, the program behind essays.render_with_roc, with the
# Roc that roc-version pins. The running server picks up a new build at once.
set -euo pipefail
cd "$(dirname "$0")/.."
pin="$(cat roc-version)"
package_pin="$(cat ../roc-markdown/roc-version)"
if [ "$pin" != "$package_pin" ]; then
    echo "roc-version is $pin, and ../roc-markdown is on $package_pin: move them together" >&2
    exit 1
fi
roc="$HOME/tools/roc-$pin/roc"
[ -x "$roc" ] || roc=roc
said="$("$roc" version)"
if [ "${said##* }" != "$pin" ]; then
    echo "$roc says '$said', and roc-version pins $pin" >&2
    exit 1
fi
mkdir -p bin
# The dev backend builds in seconds, and a note renders fast enough on it.
"$roc" build renderer/render_note.roc --opt=dev --output=bin/render_note
