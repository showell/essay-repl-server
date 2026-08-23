#!/bin/bash
# Install the server as a systemd --user service that survives reboots.
# Rerun after editing the unit file. Idempotent.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p ~/.config/systemd/user
ln -sf "$PWD/essay-repl-server.service" ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now essay-repl-server
systemctl --user --no-pager status essay-repl-server | head -5
if [ "$(loginctl show-user "$USER" -P Linger)" != "yes" ]; then
    echo "NOTE: linger is off -- the service dies with your last login."
    echo "Fix once with: sudo loginctl enable-linger $USER"
fi
