"""Page shell: one stylesheet, one nav. The typesetting follows the Safari book's
book.css in roc-apps, so a note reads like a page of the book."""
import html

import config

PAGE_CSS = """
:root {
  color-scheme: light dark;
  --paper: #fbfaf6;
  --ink: #23221f;
  --quiet: #736e64;
  --rule: #e3e0d7;
  --accent: #8a4a1c;
  --shade: #f3f1ea;
  --draft: #fbefc6;
  --draft-rule: #e6d670;
  --error: #a00000;
  --prose: 'Iowan Old Style', Charter, 'Bitstream Charter', 'Sitka Text', Cambria, Georgia, serif;
  --plain: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  --mono: ui-monospace, 'SF Mono', Menlo, Consolas, 'DejaVu Sans Mono', monospace;
  --measure: 39rem;
  --wide: 52rem;
  font-size: 18px;
}

@media (prefers-color-scheme: dark) {
  :root {
    --paper: #1b1a18;
    --ink: #e4e1d8;
    --quiet: #9c978b;
    --rule: #38352f;
    --accent: #dba56d;
    --shade: #26241f;
    --draft: #443612;
    --draft-rule: #6b5a24;
    --error: #e8907c;
  }

  /* Most diagrams set their own fills, so a diagram turns over whole: its text
     stays readable on any fill, where recoloring the text alone would not. */
  figure.dot svg { filter: invert(0.87) hue-rotate(180deg); }
}

* { box-sizing: border-box; }

/* The left padding centers the reading measure in the window, which leaves the
   room on the right for what runs wider. */
body {
  margin: 0;
  padding: 2rem 1rem 4rem max(1rem, calc((100vw - var(--measure)) / 2));
  background: var(--paper);
  color: var(--ink);
  font-family: var(--prose);
  line-height: 1.6;
  text-rendering: optimizeLegibility;
}

a { color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 0.15em; }

body > *, .wiki-md > * { max-width: var(--measure); }
body > .wiki-md { max-width: none; }
.wiki-md > table, .wiki-md > figure.dot { max-width: min(var(--wide), 100%); }

/* A code block matches the prose, and widens only for the lines that need it. */
.wiki-md > pre { width: fit-content; min-width: min(100%, var(--measure)); max-width: min(var(--wide), 100%); }

.wiki-md { margin-top: 1.5rem; overflow-wrap: break-word; }

nav { display: flex; gap: 0.8rem; margin-bottom: 1.5rem; color: var(--quiet); font: 0.74rem/1.35 var(--plain); }
nav a, .back a { color: var(--quiet); text-decoration: none; }
nav a:hover, .back a:hover { color: var(--accent); }
nav .who { display: flex; gap: 0.6rem; margin-left: auto; }
.back { margin: 0; font: 0.74rem/1.35 var(--plain); }

h1, h2, h3, h4 { line-height: 1.2; font-weight: 600; scroll-margin-top: 1.5rem; }
h1 { font-size: 2.1rem; letter-spacing: -0.01em; margin: 0 0 1.5rem; }
h2 { font-size: 1.4rem; margin: 2.8rem 0 0.8rem; }
h3 { font-size: 1.1rem; margin: 2rem 0 0.6rem; }
h4 { font-size: 1rem; margin: 1.6rem 0 0.5rem; }

p { margin: 0 0 1rem; }
ul, ol { padding-left: 1.4rem; }
li { margin: 0.25rem 0; }
hr { margin: 2.4rem 0; border: 0; border-top: 1px solid var(--rule); }

blockquote { margin: 0 0 1rem; padding-left: 1rem; border-left: 3px solid var(--rule); }
.wiki-md img { max-width: 100%; height: auto; margin: 0.5rem 0; border: 1px solid var(--rule); border-radius: 3px; }

code { font-family: var(--mono); font-size: 0.82em; }
:not(pre) > code { background: var(--shade); border-radius: 2px; padding: 0.05em 0.12em; }

pre {
  margin: 0 0 1.6rem;
  padding: 0.75rem 1rem;
  overflow-x: auto;
  background: var(--shade);
  border-radius: 4px;
  font-size: 0.78rem;
  line-height: 1.5;
  tab-size: 4;
}
pre code { font-size: inherit; }

figure.dot { margin: 0 0 1.6rem; }
figure.dot svg { display: block; max-width: 100%; height: auto; }
.dot-error { color: var(--error); font-family: var(--mono); white-space: pre-wrap; }

table {
  display: block;
  overflow-x: auto;
  margin: 0 0 1.6rem;
  border-collapse: collapse;
  font: 0.8rem/1.45 var(--plain);
}
th { border-bottom: 1px solid var(--quiet); }
td { border-bottom: 1px solid var(--rule); }
th, td { padding: 0.35rem 1rem 0.35rem 0; vertical-align: top; }
th:not([align]), td:not([align]) { text-align: left; }

.sub { margin-bottom: 1.6rem; color: var(--quiet); font: 0.8rem/1.45 var(--plain); }
.muted { color: var(--quiet); }
.error { margin: 0.7rem 0; color: var(--error); }

ul.essays { margin: 0; padding: 0; list-style: none; font: 0.82rem/1.35 var(--plain); }
ul.essays li { display: flex; justify-content: space-between; align-items: baseline; gap: 1.2rem; margin: 0; padding: 0.5rem 0; border-bottom: 1px solid var(--rule); }
ul.essays li:last-child { border-bottom: none; }
ul.essays a { color: var(--ink); font-weight: 600; text-decoration: none; overflow-wrap: anywhere; }
ul.essays a:hover { color: var(--accent); }
.date { color: var(--quiet); font-size: 0.72rem; white-space: nowrap; font-variant-numeric: tabular-nums; }

form.auth { max-width: 18rem; font-family: var(--plain); }
form.auth label { display: block; margin: 0.7rem 0 0.2rem; font-size: 0.78rem; }
form.auth input { width: 100%; padding: 0.35rem 0.45rem; font-size: 0.78rem; background: var(--paper); color: var(--ink); border: 1px solid var(--quiet); border-radius: 3px; }
form.auth button { margin-top: 0.9rem; padding: 0.35rem 0.9rem; font-size: 0.78rem; border: none; border-radius: 3px; background: var(--accent); color: var(--paper); cursor: pointer; }

@media (max-width: 40rem) {
  h1 { font-size: 1.7rem; }

  /* A wide diagram shrunk to a phone's width can't be read, so it keeps its
     size and scrolls sideways, as code does. */
  figure.dot { overflow-x: auto; }
  figure.dot svg { max-width: none; }
}
"""


def page_head(title, user):
    links = ''.join(f'<a href="/{html.escape(c)}">{html.escape(c.title())}</a>'
                    for c in config.COLLECTIONS) + '<a href="/repl">REPL</a>'
    if user:
        who = (f'<span class="who">{html.escape(user)}'
               f' <a href="/logout">log out</a></span>')
    else:
        who = ('<span class="who"><a href="/login">log in</a>'
               ' <a href="/register">register</a></span>')
    return (f'<!DOCTYPE html>\n<html><head>'
            f'<title>{html.escape(title)} — essay-repl-server</title>'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<style>{PAGE_CSS}</style></head><body>'
            f'<nav>{links}{who}</nav>\n')


def page_foot():
    return '</body></html>'


def page(title, user, body):
    return page_head(title, user) + body + page_foot()
