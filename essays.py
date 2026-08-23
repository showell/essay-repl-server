"""Essay listing and rendering: the two faces of a collection. Markdown
via python-markdown with GFM-ish extensions; YAML front-matter stripped
before rendering, first '# ' heading is the display title."""
import datetime
import html
import pathlib
import re

import markdown

import config

MD_EXTENSIONS = ['fenced_code', 'tables', 'sane_lists']
FRONT_MATTER_RE = re.compile(r'\A---\n.*?\n---\n', re.DOTALL)
IMAGE_SUFFIXES = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico'}


def collection_dir(collection):
    return config.COLLECTIONS.get(collection)


def safe_name(name):
    return name and '/' not in name and '\\' not in name and '..' not in name


def is_image(name):
    return pathlib.PurePath(name).suffix.lower() in IMAGE_SUFFIXES


def render_markdown(text):
    return markdown.markdown(FRONT_MATTER_RE.sub('', text),
                             extensions=MD_EXTENSIONS)


def extract_title(path):
    """First '# ' heading within ~10 lines past optional front-matter."""
    try:
        lines = path.read_text(errors='replace').splitlines()
    except OSError:
        return ''
    if lines and lines[0].strip() == '---':
        for i, line in enumerate(lines[1:], start=1):
            if line.strip() == '---':
                lines = lines[i + 1:]
                break
    for line in lines[:10]:
        if line.startswith('# '):
            return line[2:].strip()
    return ''


def entries(directory):
    """(title, filename, mtime) per *.md, newest first."""
    out = []
    for p in sorted(directory.glob('*.md')):
        title = extract_title(p) or p.stem
        out.append((title, p.name, p.stat().st_mtime))
    out.sort(key=lambda e: e[2], reverse=True)
    return out


def listing_body(collection):
    directory = collection_dir(collection)
    items = []
    for title, fname, mtime in entries(directory):
        when = datetime.datetime.fromtimestamp(mtime).strftime('%b %-d, %Y')
        items.append(f'<li><a href="/{html.escape(collection)}/{html.escape(fname)}">'
                     f'{html.escape(title)}</a><span class="date">{when}</span></li>')
    if not items:
        items.append('<li class="muted">Nothing here yet.</li>')
    blurb = config.BLURBS.get(collection, '')
    return (f'<h1>{html.escape(collection.title())}</h1>'
            f'<p class="sub">{html.escape(blurb)}</p>'
            f'<ul class="essays">{"".join(items)}</ul>')


def view_body(collection, name, text):
    return (f'<p><a href="/{html.escape(collection)}">&larr; Back</a></p>'
            f'<div class="wiki-md">{render_markdown(text)}</div>')
