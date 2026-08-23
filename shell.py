"""Page shell: one stylesheet, one nav. CSS lifted from claude-collab's
server/helpers.go so the surface reads the same on both boxes."""
import html

import config

PAGE_CSS = """
body { font-family: sans-serif; margin: 40px auto; max-width: 820px; padding: 0 24px; color: #222; line-height: 1.55; }
h1 { color: #000080; margin-bottom: 8px; }
h2 { color: #000080; margin-top: 32px; }
nav { margin-bottom: 16px; font-size: 13px; display: flex; gap: 14px; }
nav a { color: #000080; }
nav .who { margin-left: auto; color: #666; display: flex; gap: 10px; }
code { background: #f4f0e4; padding: 1px 4px; border-radius: 3px; font-size: 90%; }
pre { background: #f4f0e4; padding: 12px 14px; border-radius: 4px; overflow-x: auto; }
pre code { background: none; padding: 0; }
.sub { color: #666; margin-bottom: 28px; font-size: 14px; }
.muted { color: #888; }
.error { color: #a00; margin: 12px 0; }
table { border-collapse: collapse; margin: 16px 0; }
th, td { text-align: left; padding: 8px 12px; border-bottom: 1px solid #eee; }
th { background: #f4f0e4; }
ul.essays { list-style: none; padding: 0; margin: 0; }
ul.essays li { padding: 10px 0; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; gap: 20px; align-items: baseline; }
ul.essays li:last-child { border-bottom: none; }
ul.essays a { color: #000080; font-weight: bold; text-decoration: none; font-size: 16px; }
ul.essays a:hover { text-decoration: underline; }
.date { color: #666; font-size: 13px; white-space: nowrap; font-variant-numeric: tabular-nums; }
.wiki-md { margin-top: 24px; }
.wiki-md h2 { margin-top: 28px; }
.wiki-md blockquote { margin: 0 0 16px; padding: 0 14px; color: #555; border-left: 3px solid #d6d0be; }
.wiki-md img { max-width: 100%; height: auto; border: 1px solid #e6e0d0; border-radius: 3px; margin: 8px 0; }
form.auth { max-width: 320px; }
form.auth label { display: block; margin: 12px 0 4px; font-size: 14px; }
form.auth input { width: 100%; padding: 6px 8px; font-size: 14px; border: 1px solid #c9bfa7; border-radius: 3px; box-sizing: border-box; }
form.auth button { margin-top: 16px; padding: 6px 16px; font-size: 14px; border: none; border-radius: 3px; background: #000080; color: white; cursor: pointer; }
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
