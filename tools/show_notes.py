#!/usr/bin/env python3
"""Print reader notes, newest last. The read side of the notes widget.

    tools/show_notes.py                     every note on every essay
    tools/show_notes.py u49-and-the-twenty  essays whose name contains the string

Claude replies by appending to the sidecar JSON with author "claude"
(manual edits are fine; the UI is append-only)."""
import json
import pathlib
import sys

DATA = pathlib.Path(__file__).resolve().parent.parent / 'data' / 'comments'

needle = sys.argv[1] if len(sys.argv) > 1 else ''
sidecars = sorted(DATA.glob('*/*.comments.json'))
for sc in sidecars:
    essay = sc.name.removesuffix('.comments.json')
    if needle not in essay:
        continue
    collection = sc.parent.name
    comments = json.loads(sc.read_text()).get('comments', [])
    if not comments:
        continue
    print(f'== /{collection}/{essay} ({len(comments)} notes)')
    for c in sorted(comments, key=lambda c: (c['para_index'], c['timestamp'])):
        print(f'  para {c["para_index"]}  {c["author"]}  {c["timestamp"]}')
        for line in c['text'].splitlines():
            print(f'    {line}')
