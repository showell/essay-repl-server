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

# The REPL's executables (installed by ops/refresh_natives.sh) and the
# programs a visitor may choose between. Server-side files only: nothing
# a user types ever becomes a subject.
REPL_BIN = REPO / 'bin'
REPL_SUBJECTS = {
    'fib': REPO / 'subjects' / 'fib.codex',
    'queens': REPO / 'subjects' / 'queens.codex',
    'queens-bt': REPO / 'subjects' / 'queens-bt.codex',
}
REPL_OUT = DATA / 'repl'
REPL_MEMORY_MAX = '6G'   # the ladder's zig-arm resident bound
REPL_TIMEOUT = 120       # seconds per stage; fib is expected in single digits

# The zig that compiles what zigemit wrote. Absolute because the systemd
# --user service's PATH is not the shell's.
REPL_ZIG = pathlib.Path.home() / 'zig-0.16.0' / 'zig'
REPL_RUN_TIMEOUT = 30    # seconds for the compiled program itself; fib is ~instant

# Every press of the button gets its own directory under here, so a stage
# can only ever read THIS run's artifacts -- the ladder's stale-artifact
# rule, applied to the web.
REPL_RUNS = REPL_OUT / 'runs'
REPL_KEEP_RUNS = 20          # newest kept; older run dirs are deleted
REPL_OUTPUT_CAP = 2 * 1024 * 1024  # RLIMIT_FSIZE on the generated program
REPL_CPU_QUOTA = '100%'      # one core; the box is shared with the ladder

BLURBS = {
    'essays': 'Published essays on working with Claude. Log in to leave '
              'paragraph-anchored notes.',
    'notes': 'Working notes from the ladder droplet. Drafts, not doctrine.',
}
