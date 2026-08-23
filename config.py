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

BLURBS = {
    'essays': 'Published essays on working with Claude. Log in to leave '
              'paragraph-anchored notes.',
    'notes': 'Working notes from the ladder droplet. Drafts, not doctrine.',
}
