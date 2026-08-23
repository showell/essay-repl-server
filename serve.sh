#!/bin/bash
# Foreground server. ops/essay-repl-server.service wraps this for the
# durable install; run it bare to try a change.
cd "$(dirname "$0")"
exec python3 app.py
