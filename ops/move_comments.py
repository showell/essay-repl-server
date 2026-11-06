#!/usr/bin/env python3
"""Move every stored comment's para_index from the Python render to the Roc render.

    ops/move_comments.py dry-run    print what would move and write nothing
    ops/move_comments.py write      move them, with the server stopped

A comment's paragraph is found by its text. Any comment that can't be placed
stops the run, named, before anything is written. Run this while config still
says 'python', and before the config changes to 'roc': a stored index counts
paragraphs of the render that was live when the comment was posted.

The old data/comments becomes data/comments-before-roc. That folder is both the
backup and the sign that the move is done, because no index can tell which
render it counts, and comments posted after the switch are Roc's from the start.
"""
import json
import os
import pathlib
import shutil
import socket
import sys

import html5lib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import config  # noqa: E402
import essays  # noqa: E402

COMMENTS = config.DATA / 'comments'
BACKUP = config.DATA / 'comments-before-roc'
STAGED = config.DATA / 'comments-moving'

# Python runs a paragraph and the list after it together, so such a comment has
# no paragraph of the same text under Roc, and only a person can say which piece
# it belongs on. (collection, note, timestamp) -> the piece's opening words.
PLACED = {}


def anchors(page):
    """The elements the comment widget numbers, parsed as a browser parses them."""
    root = html5lib.parse(f'<div class="wiki-md">{page}</div>',
                          treebuilder='etree', namespaceHTMLElements=False)
    container = next(e for e in root.iter('div') if e.get('class') == 'wiki-md')
    return [e for e in container.iter()
            if e.tag == 'p' or (e.tag == 'li' and e.find('p') is None)]


def own_words(element):
    """An element's text, without the paragraphs and list items inside it.

    Python flattens some nested lists that Roc keeps, so an outer item's whole
    text differs between them while its own words agree."""
    words = [element.text or '']
    for child in element:
        # An HTML comment's tag isn't a string, and its text isn't on the page.
        if isinstance(child.tag, str) and child.tag not in ('p', 'li'):
            words.append(own_words(child))
        words.append(child.tail or '')
    return ''.join(words)


def paragraphs(renderer, source):
    config.MARKDOWN_RENDERER = renderer
    page = essays.render_markdown(source)
    return [' '.join(own_words(e).split()) for e in anchors(page)]


class Unplaced(Exception):
    pass


def placed_by_hand(words, wanted, roc):
    fits = [i for i, text in enumerate(roc)
            if text.startswith(words) and text in wanted]
    if len(fits) != 1:
        raise Unplaced(f'PLACED says {words!r}, which fits {len(fits)} paragraphs '
                       'of its old paragraph under Roc')
    return fits[0]


def roc_index(comment, key, python, roc):
    index = comment.get('para_index')
    if not isinstance(index, int) or not 0 <= index < len(python):
        raise Unplaced(f'para_index {index!r} is not one of the {len(python)} '
                       'paragraphs under Python')
    wanted = python[index]
    if key in PLACED:
        return placed_by_hand(PLACED[key], wanted, roc)
    if not wanted:
        raise Unplaced(f'paragraph {index} has no text to match by')
    twins = [i for i, text in enumerate(python) if text == wanted]
    matches = [i for i, text in enumerate(roc) if text == wanted]
    if len(matches) != len(twins):
        pieces = [f'{i}: {text[:60]!r}' for i, text in enumerate(roc)
                  if text and text in wanted]
        raise Unplaced(f'{len(twins)} under Python and {len(matches)} under Roc '
                       f'read {wanted[:80]!r}; pieces under Roc: {pieces}')
    return matches[twins.index(index)]


def sidecars():
    return sorted(COMMENTS.glob('*/*.comments.json'))


def plan_sidecar(sidecar):
    """The sidecar's data with its indexes moved, its moves, and what couldn't move."""
    collection = sidecar.parent.name
    name = sidecar.name.removesuffix('.comments.json')
    where = f'{collection}/{name}'
    try:
        data = json.loads(sidecar.read_text())
        comments = data['comments']
    except (ValueError, KeyError) as error:
        return None, [], [f'{where}: unreadable: {error!r}']
    if not comments:
        return data, [], []
    directory = config.COLLECTIONS.get(collection)
    if directory is None or not (directory / name).is_file():
        return data, [], [f'{where}: {len(comments)} comments and no such note']
    source = (directory / name).read_text()
    python = paragraphs('python', source)
    roc = paragraphs('roc', source)
    moves = []
    problems = []
    for comment in comments:
        stamp = comment.get('timestamp')
        try:
            new = roc_index(comment, (collection, name, stamp), python, roc)
        except Unplaced as why:
            problems.append(f'{where}: {comment.get("author")} {stamp} '
                            f'{comment.get("text", "")[:60]!r}: {why}')
            continue
        old = comment['para_index']
        if new != old:
            moves.append(f'{where}: para {old} -> {new}  {comment.get("author")} '
                         f'{stamp}  {roc[new][:60]!r}')
            comment['para_index'] = new
    return data, moves, problems


def stop(message):
    sys.exit(f'move_comments: {message}')


def server_is_up():
    with socket.socket() as probe:
        probe.settimeout(1)
        return probe.connect_ex(('127.0.0.1', config.PORT)) == 0


def write(changed):
    """The live folder changes only by the two renames at the end, so a run that
    dies before them leaves every comment where it was."""
    if server_is_up():
        stop(f'the server is up on port {config.PORT}, and a comment posted now '
             'would be lost: stop it first')
    shutil.rmtree(STAGED, ignore_errors=True)
    shutil.copytree(COMMENTS, STAGED)
    for sidecar, data in changed:
        staged = STAGED / sidecar.relative_to(COMMENTS)
        staged.write_text(json.dumps(data, indent=2) + '\n')
    os.rename(COMMENTS, BACKUP)
    os.rename(STAGED, COMMENTS)
    print(f'moved; the old comments are in {BACKUP}')


def main():
    if sys.argv[1:] not in (['dry-run'], ['write']):
        stop('say dry-run or write')
    if BACKUP.exists():
        if not COMMENTS.exists():
            stop(f'{COMMENTS} is missing: a run died between its renames, so '
                 f'rename {STAGED} to it')
        print(f'{BACKUP} exists, so the comments are already moved: 0 move')
        return
    if config.MARKDOWN_RENDERER != 'python':
        stop(f'config says {config.MARKDOWN_RENDERER!r} and {BACKUP} does not '
             'exist, so the stored indexes may not be Python\'s')
    changed = []
    problems = []
    comments = notes = moved = 0
    for sidecar in sidecars():
        data, moves, unplaced = plan_sidecar(sidecar)
        problems += unplaced
        if data and data['comments']:
            comments += len(data['comments'])
            notes += 1
        moved += len(moves)
        for move in moves:
            print(move)
        if moves:
            changed.append((sidecar, data))
    print(f'{comments} comments in {notes} notes: {moved} move')
    if problems:
        for problem in problems:
            print(problem)
        stop(f'{len(problems)} comments can\'t be placed, and nothing was written')
    if sys.argv[1] == 'write':
        write(changed)


if __name__ == '__main__':
    main()
