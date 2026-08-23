"""Accounts: register, log in, log out. Deliberately minimal — usernames
and scrypt-hashed passwords in SQLite, a signed session cookie, nothing
else. No email, no reset flow; an account here is a name to sign notes
with, not an identity."""
import html
import os
import re
import secrets
import sqlite3
import time

from flask import Blueprint, redirect, request, session

import config
from shell import page

bp = Blueprint('auth', __name__)

USERS_DB = config.DATA / 'users.db'
USERNAME_RE = re.compile(r'^[A-Za-z0-9_-]{1,32}$')
SCRYPT_N, SCRYPT_R, SCRYPT_P = 2 ** 14, 8, 1


def db():
    conn = sqlite3.connect(USERS_DB)
    conn.execute('CREATE TABLE IF NOT EXISTS users ('
                 ' id INTEGER PRIMARY KEY,'
                 ' username TEXT UNIQUE COLLATE NOCASE NOT NULL,'
                 ' pwhash TEXT NOT NULL,'
                 ' created TEXT NOT NULL)')
    return conn


def hash_password(password):
    salt = secrets.token_bytes(16)
    h = _scrypt(password, salt)
    return f'scrypt:{SCRYPT_N}:{SCRYPT_R}:{SCRYPT_P}:{salt.hex()}:{h.hex()}'


def check_password(password, stored):
    kind, n, r, p, salthex, hashhex = stored.split(':')
    assert kind == 'scrypt'
    h = _scrypt(password, bytes.fromhex(salthex), int(n), int(r), int(p))
    return secrets.compare_digest(h.hex(), hashhex)


def _scrypt(password, salt, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P):
    import hashlib
    return hashlib.scrypt(password.encode(), salt=salt, n=n, r=r, p=p,
                          maxmem=64 * 1024 * 1024)


def current_user():
    return session.get('user')


def secret_key():
    """Signing key for the session cookie, generated once and kept out
    of git. Regenerating it logs everyone out and nothing else."""
    path = config.DATA / 'secret_key'
    if not path.is_file():
        path.write_bytes(secrets.token_bytes(32))
        os.chmod(path, 0o600)
    return path.read_bytes()


def _auth_form(title, action, error=''):
    err = f'<p class="error">{html.escape(error)}</p>' if error else ''
    nxt = html.escape(request.values.get('next', ''), quote=True)
    body = (f'<h1>{html.escape(title)}</h1>{err}'
            f'<form class="auth" method="post" action="{action}">'
            f'<input type="hidden" name="next" value="{nxt}">'
            f'<label>username</label><input name="username" autofocus'
            f' value="{html.escape(request.form.get("username", ""), quote=True)}">'
            f'<label>password</label><input name="password" type="password">'
            f'<button>{html.escape(title)}</button></form>')
    return page(title, current_user(), body)


def _next_url():
    nxt = request.form.get('next', '')
    return nxt if nxt.startswith('/') and not nxt.startswith('//') else '/'


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return _auth_form('Register', '/register')
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    if not USERNAME_RE.match(username):
        return _auth_form('Register', '/register',
                          'username: 1-32 letters, digits, - or _')
    if len(password) < 8:
        return _auth_form('Register', '/register',
                          'password: 8 characters minimum')
    conn = db()
    try:
        conn.execute('INSERT INTO users (username, pwhash, created) VALUES (?, ?, ?)',
                     (username, hash_password(password),
                      time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())))
        conn.commit()
    except sqlite3.IntegrityError:
        return _auth_form('Register', '/register', 'that name is taken')
    finally:
        conn.close()
    session['user'] = username
    return redirect(_next_url())


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return _auth_form('Log in', '/login')
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    conn = db()
    row = conn.execute('SELECT username, pwhash FROM users WHERE username = ?',
                       (username,)).fetchone()
    conn.close()
    if not row or not check_password(password, row[1]):
        return _auth_form('Log in', '/login', 'no match for that name and password')
    session['user'] = row[0]
    return redirect(_next_url())


@bp.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')
