"""Paragraph-anchored notes, the claude-collab mechanic with accounts.

Same sidecar schema ({comments: [{para_index, author, timestamp, text}]},
hand-editable JSON) but stored under data/comments/<collection>/ rather
than beside the essays: the essays live in git clones and reader data
does not belong in them. Author comes from the session, so posting
requires an account; reading never does."""
import json
import time

from flask import Blueprint, jsonify, request

import auth
import config
import essays

bp = Blueprint('comments', __name__)


def resolve_article(article):
    """'/essays/foo.md' -> (collection, name), or None on any funny business."""
    parts = article.strip('/').split('/')
    if len(parts) != 2:
        return None
    collection, name = parts
    directory = essays.collection_dir(collection)
    if directory is None or not essays.safe_name(name) or not name.endswith('.md'):
        return None
    if not (directory / name).is_file():
        return None
    return collection, name


def sidecar(collection, name):
    d = config.DATA / 'comments' / collection
    d.mkdir(parents=True, exist_ok=True)
    return d / f'{name}.comments.json'


def load(collection, name):
    try:
        return json.loads(sidecar(collection, name).read_text())
    except (OSError, ValueError):
        return {'comments': []}


@bp.route('/article-comments', methods=['GET'])
def get_comments():
    resolved = resolve_article(request.args.get('article', ''))
    if not resolved:
        return jsonify(error='invalid article path'), 400
    return jsonify(load(*resolved))


@bp.route('/article-comments', methods=['POST'])
def post_comment():
    user = auth.current_user()
    if not user:
        return jsonify(error='log in to leave notes'), 401
    resolved = resolve_article(request.form.get('article', ''))
    if not resolved:
        return jsonify(error='invalid article path'), 400
    text = request.form.get('text', '').strip()
    if not text:
        return jsonify(error='empty comment'), 400
    if len(text) > 10000:
        return jsonify(error='comment too long'), 400
    f = load(*resolved)
    f['comments'].append({
        'para_index': int(request.form.get('para_index', 0)),
        'author': user,
        'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'text': text,
    })
    sidecar(*resolved).write_text(json.dumps(f, indent=2) + '\n')
    return jsonify(f)


# The client-side widget, lifted from claude-collab's article_comments.go.
# One behavioral change: the author box is gone — the server signs notes
# with the session user, and a logged-out click on "note" goes to /login.
WIDGET_JS = r"""
<script>
(function(){
  var container = document.querySelector('.wiki-md');
  if (!container) return;
  if (!/\.md$/.test(location.pathname)) return;
  var articlePath = location.pathname;
  var user = window.ESSAY_USER || null;

  var style = document.createElement('style');
  style.textContent = [
    '.para-wrap { position: relative; }',
    '.para-add-btn { margin-left: 8px; cursor: pointer; font-size: 13px; border: 1px solid #000080; background: white; color: #000080; padding: 1px 6px; border-radius: 3px; vertical-align: middle; }',
    '.para-add-btn:hover { background: #000080; color: white; }',
    '.para-comments { margin: 6px 0 14px 24px; padding-left: 10px; border-left: 3px solid #d6d0be; }',
    '.para-comment { background: #faf7ef; border: 1px solid #e8e1cc; border-radius: 3px; padding: 10px 12px; margin: 6px 0; font-size: 14px; font-family: sans-serif; color: #333; line-height: 1.55; }',
    '.para-comment .meta { color: #888; font-size: 11px; margin-bottom: 2px; }',
    '.para-compose { margin: 6px 0 14px 24px; padding: 8px; background: #fff3a8; border: 1px solid #e6d670; border-radius: 4px; font-family: sans-serif; }',
    '.para-compose textarea { width: 100%; min-height: 120px; padding: 8px 10px; font-size: 14px; font-family: sans-serif; line-height: 1.5; box-sizing: border-box; border: 1px solid #c9bfa7; border-radius: 3px; }',
    '.para-compose button { margin-top: 6px; margin-right: 6px; padding: 4px 12px; font-size: 13px; border: none; border-radius: 3px; cursor: pointer; }',
    '.para-compose .save { background: #000080; color: white; }',
    '.para-compose .cancel { background: #eee; color: #333; }',
  ].join('\n');
  document.head.appendChild(style);

  var candidates = container.querySelectorAll('p, li');
  var paras = [];
  candidates.forEach(function(el){
    if (el.tagName === 'LI' && el.querySelector(':scope > p')) return;
    paras.push(el);
  });
  var paraByIndex = {};
  paras.forEach(function(p, i){
    p.setAttribute('data-para-index', i);
    p.classList.add('para-wrap');
    paraByIndex[i] = p;
    var btn = document.createElement('button');
    btn.className = 'para-add-btn';
    btn.textContent = 'note';
    btn.title = user ? 'Add a note on this paragraph' : 'Log in to leave a note';
    btn.addEventListener('click', function(){
      if (!user) { location = '/login?next=' + encodeURIComponent(articlePath); return; }
      openCompose(i);
    });
    p.appendChild(btn);
  });

  function attachAfter(p, child) {
    if (p.tagName === 'LI') p.appendChild(child);
    else p.parentNode.insertBefore(child, p.nextSibling);
  }
  function findExistingCommentsBox(p) {
    if (p.tagName === 'LI') return p.querySelector(':scope > .para-comments');
    var sib = p.nextElementSibling;
    if (sib && sib.classList.contains('para-comments')) return sib;
    return null;
  }

  fetch('/article-comments?article=' + encodeURIComponent(articlePath))
    .then(function(r){ return r.ok ? r.json() : { comments: [] }; })
    .then(function(data){ (data.comments || []).forEach(renderComment); });

  function renderComment(c) {
    var p = paraByIndex[c.para_index];
    if (!p) return;
    var box = findExistingCommentsBox(p);
    if (!box) {
      box = document.createElement('div');
      box.className = 'para-comments';
      box.setAttribute('data-para-index', c.para_index);
      attachAfter(p, box);
    }
    var cEl = document.createElement('div');
    cEl.className = 'para-comment';
    var meta = document.createElement('div');
    meta.className = 'meta';
    meta.textContent = c.author + ' · ' + c.timestamp;
    cEl.appendChild(meta);
    var text = document.createElement('div');
    text.textContent = c.text;
    cEl.appendChild(text);
    box.appendChild(cEl);
  }

  function openCompose(paraIdx) {
    var existing = document.querySelector('.para-compose[data-para-index="' + paraIdx + '"]');
    if (existing) { existing.querySelector('textarea').focus(); return; }
    var p = paraByIndex[paraIdx];
    var compose = document.createElement('div');
    compose.className = 'para-compose';
    compose.setAttribute('data-para-index', paraIdx);
    compose.innerHTML =
      '<textarea placeholder="Light note..."></textarea>' +
      '<div><button class="save">Save</button><button class="cancel">Cancel</button></div>';
    var existingBox = findExistingCommentsBox(p);
    if (existingBox) existingBox.parentNode.insertBefore(compose, existingBox.nextSibling);
    else attachAfter(p, compose);
    var textarea = compose.querySelector('textarea');
    textarea.focus();
    compose.querySelector('.cancel').addEventListener('click', function(){ compose.remove(); });
    compose.querySelector('.save').addEventListener('click', function(){
      var text = textarea.value.trim();
      if (!text) return;
      var body = new URLSearchParams();
      body.set('article', articlePath);
      body.set('para_index', String(paraIdx));
      body.set('text', text);
      fetch('/article-comments', {
        method: 'POST',
        headers: {'Content-Type':'application/x-www-form-urlencoded'},
        body: body.toString(),
      }).then(function(r){ return r.ok ? r.json() : Promise.reject(r.status); })
        .then(function(data){
          document.querySelectorAll('.para-comments').forEach(function(el){ el.remove(); });
          (data.comments || []).forEach(renderComment);
          compose.remove();
        })
        .catch(function(err){ alert('Failed to save: ' + err); });
    });
  }
})();
</script>
"""
