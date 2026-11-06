"""Essay listing and rendering: the two faces of a collection. Markdown
goes through the renderer config.MARKDOWN_RENDERER names; YAML front-matter
is stripped before rendering, first '# ' heading is the display title."""
import datetime
import html
import pathlib
import re
import subprocess

import markdown

import config

MD_EXTENSIONS = ['fenced_code', 'tables', 'sane_lists']
FRONT_MATTER_RE = re.compile(r'\A---\n.*?\n---\n', re.DOTALL)
IMAGE_SUFFIXES = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.ico'}
# A note may lean on a vendored library or stylesheet living beside it --
# the graphviz renderer an AST-diagram essay embeds, say. Served verbatim,
# like an image; the server hosts our own files, not a user's.
ASSET_SUFFIXES = {'.js', '.css', '.wasm', '.woff', '.woff2'}
# Linux stops one argument at 128 KiB, and a character is at most four bytes.
ROC_PART_CHARS = 32000


def collection_dir(collection):
    return config.COLLECTIONS.get(collection)


def safe_name(name):
    return name and '/' not in name and '\\' not in name and '..' not in name


def is_image(name):
    return pathlib.PurePath(name).suffix.lower() in IMAGE_SUFFIXES


def is_asset(name):
    return pathlib.PurePath(name).suffix.lower() in ASSET_SUFFIXES


def render_with_python(source):
    return markdown.markdown(source, extensions=MD_EXTENSIONS)


def render_with_roc(source):
    if not config.ROC_RENDERER_BIN.is_file():
        raise RuntimeError(f'{config.ROC_RENDERER_BIN} is missing: '
                           'run ops/build_renderer.sh')
    parts = [source[at:at + ROC_PART_CHARS]
             for at in range(0, len(source), ROC_PART_CHARS)]
    done = subprocess.run([config.ROC_RENDERER_BIN, *parts],
                          capture_output=True,
                          timeout=config.ROC_RENDER_TIMEOUT)
    if done.returncode != 0:
        raise RuntimeError(f'{config.ROC_RENDERER_BIN} exited '
                           f'{done.returncode}: {done.stderr.decode(errors="replace")}')
    return done.stdout.decode()


RENDERERS = {'python': render_with_python, 'roc': render_with_roc}


def render_markdown(text):
    return RENDERERS[config.MARKDOWN_RENDERER](FRONT_MATTER_RE.sub('', text))


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


# A ```dot fence renders as a diagram. The library is 1.4 MB, so it loads only
# on a note that has one; assets/dot.js does the rendering.
DOT_SCRIPTS = ('<script src="/assets/viz-standalone.js"></script>'
               '<script src="/assets/dot.js"></script>')


def view_body(collection, name, text):
    rendered = render_markdown(text)
    body = (f'<p><a href="/{html.escape(collection)}">&larr; Back</a></p>'
            f'<div class="wiki-md">{rendered}</div>')
    if 'class="language-dot"' in rendered:
        body += DOT_SCRIPTS
    return body
