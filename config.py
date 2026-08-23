"""All configuration. No CLI flags anywhere; edit this file."""
import pathlib

HOST = '0.0.0.0'
PORT = 9100

REPO = pathlib.Path(__file__).resolve().parent
DATA = REPO / 'data'

# Collections: URL prefix -> directory of *.md files. claude-collab's
# published essays seed the public shelf; notes/ is this box's own
# drafting space (session essays, REPL design notes, whatever wants a
# rendered page instead of a console wall).
COLLECTIONS = {
    'essays': pathlib.Path.home() / 'showell_repos' / 'claude-collab' / 'essays',
    'notes': REPO / 'notes',
}

# The REPL's executables and subject, installed by ops/refresh_natives.sh.
REPL_BIN = REPO / 'bin'
REPL_SUBJECT = REPO / 'subjects' / 'fib.codex'
REPL_OUT = DATA / 'repl'
REPL_MEMORY_MAX = '6G'   # the ladder's zig-arm resident bound
REPL_TIMEOUT = 120       # seconds per stage; fib is expected in single digits

BLURBS = {
    'essays': 'Published essays on working with Claude. Log in to leave '
              'paragraph-anchored notes.',
    'notes': 'Working notes from the ladder droplet. Drafts, not doctrine.',
}
