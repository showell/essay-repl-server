#!/usr/bin/env python3
"""essay-repl-server: the ladder droplet's public reading surface.

Milestone 1: rendered essay collections, accounts, paragraph-anchored
notes. The online Codex REPL rides on this same server later; anything
it sends through QEMU respects the box's one-compute-job rule, the
native loop answers at keyboard tempo.

Run: ./serve.sh (waitress on config.HOST:config.PORT). No CLI flags;
configuration lives in config.py.
"""
import json

from flask import Flask, abort, redirect, send_from_directory

import auth
import comments
import config
import essays
from shell import page

config.DATA.mkdir(exist_ok=True)

app = Flask(__name__)
app.secret_key = auth.secret_key()
app.register_blueprint(auth.bp)
app.register_blueprint(comments.bp)


@app.route('/')
def index():
    return redirect('/essays')


@app.route('/<collection>')
def listing(collection):
    if essays.collection_dir(collection) is None:
        abort(404)
    return page(collection.title(), auth.current_user(),
                essays.listing_body(collection))


@app.route('/<collection>/<name>')
def view(collection, name):
    directory = essays.collection_dir(collection)
    if directory is None or not essays.safe_name(name):
        abort(404)
    if essays.is_image(name):
        return send_from_directory(directory, name)
    if not name.endswith('.md') or not (directory / name).is_file():
        abort(404)
    user = auth.current_user()
    body = essays.view_body(collection, name, (directory / name).read_text(errors='replace'))
    body += f'<script>window.ESSAY_USER = {json.dumps(user)};</script>'
    body += comments.WIDGET_JS
    title = essays.extract_title(directory / name) or name[:-3]
    return page(title, user, body)


if __name__ == '__main__':
    import waitress
    print(f'essay-repl-server on {config.HOST}:{config.PORT}')
    waitress.serve(app, host=config.HOST, port=config.PORT)
