"""The online REPL: watch a Codex program get compiled, then watch it run.

The visitor picks the subject (fib, or eight queens); four stages, the
ladder's native loop with the QEMU taken out, ending where a compiler
pipeline should -- at the program's own output:

    stage ir    bin/codexir     the subject on stdin -> IR on stderr
    stage zig   bin/zigemit     the IR on stdin -> zig source on stderr
    stage exe   zig build-exe   prog.zig -> a native binary
    stage run   ./prog          the binary runs; its output is the pane

Each stage is bounded the way the ladder bounds its own arms
(systemd-run --user --scope MemoryMax, plus a timeout). The run stage
executes GENERATED code, so its scope also carries RuntimeMaxSec:
systemd kills the whole scope even if our own timeout misses --
subprocess timeouts kill only the direct child, and an orphaned
grandchild is exactly the runaway this page must not mint. Nothing here
touches QEMU, so nothing here needs the box's one-compute-job lock;
when a QEMU-path stage arrives it will take that lock and users wait.

Every press of the button is one sandboxed use: the ir stage mints a
directory under data/repl/runs/ and every later stage reads and writes
only inside it, so a stage can never answer from another run's artifact
-- the ladder's stale-artifact rule, applied to the web. Old runs are
pruned to the newest few. The subject is still the server's own
fib.codex; when user-submitted programs arrive, this per-run directory
is where their isolation story starts, and it will need more than
directories (the scope has no PrivateNetwork under a user manager).

Running requires an account; reading results does not. One run at a
time -- the second clicker gets a 409, not a queue.
"""
import html
import json
import re
import resource
import shutil
import subprocess
import threading
import time

from flask import Blueprint, Response, abort, jsonify, request

import auth
import config
from shell import page

bp = Blueprint('repl', __name__)

RUN_LOCK = threading.Lock()

# reads/writes are names inside the run's own directory -- generic on
# purpose, since the run dir itself is the identity; the ir stage reads
# the chosen server-side subject and MINTS the directory, which is what
# makes a press of the button one sandboxed use: nothing a stage reads
# can come from any other run.
STAGES = {
    'ir': {
        'kind': 'transform',
        'binary': config.REPL_BIN / 'codexir',
        'reads': None,
        'writes': 'prog.ir',
        'label': 'Codex source -> IR (bin/codexir)',
        'pretty': True,
    },
    'zig': {
        'kind': 'transform',
        'binary': config.REPL_BIN / 'zigemit',
        'reads': 'prog.ir',
        'writes': 'prog.zig',
        'label': 'IR -> zig source (bin/zigemit)',
        'skip_prelude': True,
    },
    'exe': {
        'kind': 'build',
        'reads': 'prog.zig',
        'writes': 'prog',
        'label': 'zig source -> native binary (zig build-exe)',
    },
    'run': {
        'kind': 'execute',
        'reads': 'prog',
        'writes': 'prog.out',
        'label': 'The program runs (./prog)',
    },
}

# The artifacts the raw-view route may serve out of a run directory. The
# binary is not here on purpose: the route says text/plain and means it.
RAW_NAMES = {'prog.ir', 'prog.zig', 'prog.out'}

# Minted by mint_run, so anything else in a URL is someone probing.
RUN_ID = re.compile(r'^\d{8}T\d{6}Z-\d+$')
_run_serial = 0


def mint_run():
    """A fresh directory per use, pruned to the newest REPL_KEEP_RUNS.
    The serial disambiguates two presses inside one second."""
    global _run_serial
    _run_serial += 1
    run = f'{time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())}-{_run_serial}'
    (config.REPL_RUNS / run).mkdir(parents=True)
    for stale in sorted(config.REPL_RUNS.iterdir())[:-config.REPL_KEEP_RUNS]:
        shutil.rmtree(stale, ignore_errors=True)
    return run


def run_dir(run):
    if not run or not RUN_ID.match(run):
        return None
    d = config.REPL_RUNS / run
    return d if d.is_dir() else None

PREVIEW_LINES = 500
PRETTY_CAP = 512 * 1024   # pretty-print IR only under this size; raw past it


def provenance():
    try:
        return (config.REPL_BIN / 'PROVENANCE').read_text()
    except OSError:
        return 'no natives installed -- run ops/refresh_natives.sh'


def preview(path, pretty=False, skip_prelude=False):
    try:
        text = path.read_text(errors='replace')
    except OSError:
        return ''
    if pretty and len(text) <= PRETTY_CAP:
        text = pretty_sexp(text)
    lines = text.splitlines(keepends=True)
    if skip_prelude:
        # Every emitted program shares one runtime prelude, all of it in
        # cx_*/Cx* names; the program's own defs come after it. Show those.
        for i, line in enumerate(lines):
            if line.startswith('fn ') and not line.startswith(('fn cx_', 'fn Cx')):
                lines = [f'... (runtime prelude, {i} lines shared by every '
                         f'program, hidden; see full)\n\n'] + lines[i:]
                break
    if len(lines) > PREVIEW_LINES:
        lines = lines[:PREVIEW_LINES] + [f'... ({len(lines) - PREVIEW_LINES} more lines; see full)']
    return ''.join(lines)


def pretty_sexp(text, width=100):
    """Re-indent the IR's s-expressions: a form stays on one line while it
    fits in `width` columns, else its children stack. Falls back to the
    raw text on anything unparseable."""
    try:
        forms, i = [], 0
        while True:
            form, i = _parse_sexp(text, i)
            if form is None:
                break
            forms.append(form)
        return '\n'.join(_render_sexp(f, 0, width) for f in forms) + '\n'
    except (ValueError, RecursionError):
        return text


def _parse_sexp(text, i):
    n = len(text)
    while i < n and text[i].isspace():
        i += 1
    if i >= n:
        return None, i
    if text[i] == '(':
        i += 1
        children = []
        while True:
            while i < n and text[i].isspace():
                i += 1
            if i >= n:
                raise ValueError('unclosed form')
            if text[i] == ')':
                return children, i + 1
            child, i = _parse_sexp(text, i)
            children.append(child)
    if text[i] == '"':
        j = i + 1
        while j < n:
            if text[j] == '\\':
                j += 2
                continue
            if text[j] == '"':
                return text[i:j + 1], j + 1
            j += 1
        raise ValueError('unclosed string')
    j = i
    while j < n and not text[j].isspace() and text[j] not in '()':
        j += 1
    return text[i:j], j


def _render_sexp(form, indent, width):
    if isinstance(form, str):
        return form
    flat = '(' + ' '.join(_render_sexp(c, 0, width) for c in form) + ')'
    if indent + len(flat) <= width:
        return flat
    if not form:
        return '()'
    head = _render_sexp(form[0], indent, width)
    lines = ['(' + head]
    for c in form[1:]:
        lines.append(' ' * (indent + 2) + _render_sexp(c, indent + 2, width))
    lines[-1] += ')'
    return '\n'.join(lines)


@bp.route('/repl/run/<stage>', methods=['POST'])
def run_stage(stage):
    if not auth.current_user():
        return jsonify(error='log in to run the compiler'), 401
    spec = STAGES.get(stage)
    if spec is None:
        abort(404)
    if spec['kind'] == 'transform' and not spec['binary'].is_file():
        return jsonify(error='no natives installed -- run ops/refresh_natives.sh'), 503
    if spec['kind'] == 'build' and not config.REPL_ZIG.is_file():
        return jsonify(error=f'missing {config.REPL_ZIG}'), 503
    if not RUN_LOCK.acquire(blocking=False):
        return jsonify(error='a run is already in progress'), 409
    try:
        if spec['reads'] is None:
            rd = config.REPL_SUBJECTS.get(request.args.get('subject', ''))
            if rd is None or not rd.is_file():
                return jsonify(error='no such subject'), 404
            d = config.REPL_RUNS / mint_run()
        else:
            d = run_dir(request.args.get('run', ''))
            if d is None:
                return jsonify(error='no such run -- start from the top'), 409
            rd = d / spec['reads']
            if not rd.is_file():
                return jsonify(error=f'missing input {rd.name} -- run the prior stage'), 409
        runner = {'transform': _transform, 'build': _build, 'execute': _execute}
        return runner[spec['kind']](stage, spec, d, rd)
    except subprocess.TimeoutExpired as e:
        return jsonify(error=f'stage {stage} exceeded {e.timeout}s'), 500
    finally:
        RUN_LOCK.release()


def bounded(cmd, stage_timeout, stdin=None, cwd=None, scope_props=(),
            stdout=None, stderr=None, fsize=None):
    """One process under a systemd scope with the ladder's resident bound.
    Extra scope properties ride along for the stages that need more than a
    memory ceiling. `fsize` sets RLIMIT_FSIZE before exec -- a scope unit
    cannot carry Limit* properties (systemd never forks its processes), so
    the rlimit is set here and inherited through systemd-run."""
    wrapped = ['systemd-run', '--user', '--scope', '--quiet',
               '-p', f'MemoryMax={config.REPL_MEMORY_MAX}']
    for p in scope_props:
        wrapped += ['-p', p]
    pre = (lambda: resource.setrlimit(resource.RLIMIT_FSIZE, (fsize, fsize))) if fsize else None
    started = time.monotonic()
    r = subprocess.run(wrapped + cmd, stdin=stdin, cwd=cwd,
                       stdout=stdout or subprocess.PIPE,
                       stderr=stderr or subprocess.PIPE,
                       timeout=stage_timeout, preexec_fn=pre)
    return r, round(time.monotonic() - started, 2)


def _answer(stage, d, seconds, nbytes, artifact, preview_text):
    return jsonify(stage=stage, run=d.name, seconds=seconds, bytes=nbytes,
                   raw=f'/repl/raw/{d.name}/{artifact}' if artifact else None,
                   preview=preview_text)


def _transform(stage, spec, d, rd):
    with open(rd, 'rb') as f:
        r, seconds = bounded([str(spec['binary'])], config.REPL_TIMEOUT, stdin=f)
    # The natives speak the pipeline's convention: product on stderr,
    # progress chatter on stdout.
    if r.returncode != 0 or not r.stderr:
        return jsonify(error=f'stage {stage} failed rc={r.returncode}',
                       tail=r.stdout.decode(errors='replace')[-2000:]), 500
    wr = d / spec['writes']
    wr.write_bytes(r.stderr)
    return _answer(stage, d, seconds, len(r.stderr), wr.name,
                   preview(wr, pretty=spec.get('pretty', False),
                           skip_prelude=spec.get('skip_prelude', False)))


def _build(stage, spec, d, rd):
    """zig build-exe: the product is a FILE, and stderr is diagnostics --
    the opposite convention from the natives, worth not conflating. The
    CPU quota keeps a compile from pegging the box the ladder shares."""
    wr = d / spec['writes']
    r, seconds = bounded(
        [str(config.REPL_ZIG), 'build-exe', rd.name, '-femit-bin=' + wr.name],
        config.REPL_TIMEOUT, cwd=d,
        scope_props=(f'CPUQuota={config.REPL_CPU_QUOTA}',))
    diags = r.stderr.decode(errors='replace')
    if r.returncode != 0 or not wr.is_file():
        return jsonify(error=f'stage {stage} failed rc={r.returncode}',
                       tail=diags[-2000:]), 500
    return _answer(stage, d, seconds, wr.stat().st_size, None,
                   diags.strip() or '(clean compile; the binary is the product)')


def _execute(stage, spec, d, rd):
    """The generated program itself, held three ways: RuntimeMaxSec on the
    scope (kills the whole scope, grandchildren included -- the backstop a
    subprocess timeout cannot be), a CPU quota, and RLIMIT_FSIZE with the
    output on a file rather than a pipe, so a print loop dies at the cap
    instead of filling the disk or this process's memory."""
    wr = d / spec['writes']
    with open(wr, 'wb') as out_file:
        r, seconds = bounded(
            [str(rd)], config.REPL_RUN_TIMEOUT + 5,
            scope_props=(f'RuntimeMaxSec={config.REPL_RUN_TIMEOUT}',
                         f'CPUQuota={config.REPL_CPU_QUOTA}'),
            # The emitted runtime prints through std.debug.print, so the
            # answer arrives on stderr; both land in the one file, in order.
            stdout=out_file, stderr=out_file,
            fsize=config.REPL_OUTPUT_CAP)
    nbytes = wr.stat().st_size
    if r.returncode != 0:
        tail = wr.read_bytes()[-2000:].decode(errors='replace')
        return jsonify(error=f'the program exited rc={r.returncode}', tail=tail), 500
    return _answer(stage, d, seconds, nbytes, wr.name, preview(wr))


@bp.route('/repl/raw/subject/<name>')
def raw_subject(name):
    src = config.REPL_SUBJECTS.get(name)
    if src is None or not src.is_file():
        abort(404)
    return Response(src.read_bytes(), mimetype='text/plain')


@bp.route('/repl/raw/<run>/<name>')
def raw(run, name):
    d = run_dir(run)
    if d is None or name not in RAW_NAMES or not (d / name).is_file():
        abort(404)
    return Response((d / name).read_bytes(), mimetype='text/plain')


# How each subject introduces itself beside its radio button.
SUBJECT_TITLES = {
    'fib': 'fib -- recursion, one printed number',
    'queens': 'eight queens -- recursive backtracking, first solution as a board',
}


@bp.route('/repl')
def repl_page():
    user = auth.current_user()
    subjects = {name: {'preview': preview(path),
                       'bytes': path.stat().st_size,
                       'raw': f'/repl/raw/subject/{name}'}
                for name, path in config.REPL_SUBJECTS.items() if path.is_file()}
    default = 'fib' if 'fib' in subjects else next(iter(subjects), '')
    first = subjects.get(default, {'preview': '', 'bytes': 0, 'raw': ''})
    panes = [_pane('source', 'The program', first['preview'],
                   first['bytes'], first['raw'])]
    # The stage panes always load empty: compiling is the page's whole
    # act, and a cached artifact would rob the button of its reveal.
    for stage, spec in STAGES.items():
        panes.append(_pane(stage, spec['label'], '', 0, ''))
    radios = ''.join(
        f'<label class="pick"><input type="radio" name="subject" value="{name}"'
        f'{" checked" if name == default else ""}> '
        f'{html.escape(SUBJECT_TITLES.get(name, name))}</label><br>'
        for name in subjects)
    body = (
        '<h1>REPL</h1>'
        '<p class="sub">Pick a small Codex program; it is compiled to IR and '
        'then to zig by the same native executables the ladder banks with, '
        'built into a native binary, and RUN. The last pane is the '
        'program\'s own output. No QEMU anywhere. The IR pane is '
        'pretty-printed; "full" links serve the raw artifact.</p>'
        f'<pre class="prov">{html.escape(provenance())}</pre>'
        f'<p>{radios}</p>'
        + (f'<p><button id="go">Compile and run</button> '
           f'<span id="status" class="muted"></span></p>' if user else
           '<p class="muted"><a href="/login?next=/repl">Log in</a> to run '
           'the compiler.</p>')
        + ''.join(panes)
        + f'<script>var SUBJECTS = {_subjects_json(subjects)};</script>'
        + REPL_JS)
    return page('REPL', user, body)


def _subjects_json(subjects):
    # </script> inside a preview would end the tag; < cannot.
    return json.dumps(subjects).replace('<', '\\u003c')


def _pane(key, label, text, size, rawhref):
    shown = html.escape(text) if text else '<span class="muted">(awaiting a run)</span>'
    meta = f'{size:,} bytes · <a href="{rawhref}">full</a>' if size else ''
    return (f'<h2>{html.escape(label)}</h2>'
            f'<div class="pane" id="pane-{key}"><div class="meta" id="meta-{key}">{meta}</div>'
            f'<pre id="pre-{key}">{shown}</pre></div>')


REPL_JS = r"""
<style>
.pane pre { max-height: 420px; overflow: auto; }
.pane .meta { font-size: 12px; color: #666; margin-bottom: 4px; }
.prov { font-size: 12px; color: #666; }
#go { padding: 6px 16px; font-size: 14px; border: none; border-radius: 3px; background: #000080; color: white; cursor: pointer; }
</style>
<script>
(function(){
  var status = document.getElementById('status');
  function chosen() {
    var r = document.querySelector('input[name=subject]:checked');
    return r ? r.value : '';
  }
  function showSource(name) {
    var s = SUBJECTS[name];
    if (!s) return;
    document.getElementById('pre-source').textContent = s.preview;
    document.getElementById('meta-source').innerHTML =
      s.bytes.toLocaleString() + ' bytes · <a href="' + s.raw + '">full</a>';
    // A new subject means the old panes are another program's story.
    ['ir', 'zig', 'exe', 'run'].forEach(function(st){
      document.getElementById('pre-' + st).innerHTML =
        '<span class="muted">(awaiting a run)</span>';
      document.getElementById('meta-' + st).innerHTML = '';
    });
    if (status) status.textContent = '';
  }
  document.querySelectorAll('input[name=subject]').forEach(function(r){
    r.addEventListener('change', function(){ showSource(r.value); });
  });
  var go = document.getElementById('go');
  if (!go) return;
  function show(stage, data) {
    document.getElementById('pre-' + stage).textContent = data.preview;
    document.getElementById('meta-' + stage).innerHTML =
      data.bytes.toLocaleString() + ' bytes · ' + data.seconds + 's' +
      (data.raw ? ' · <a href="' + data.raw + '">full</a>' : '');
  }
  function run(stage, q) {
    status.textContent = 'running ' + stage + '...';
    return fetch('/repl/run/' + stage + '?' + q, {method: 'POST'})
      .then(function(r){ return r.json().then(function(j){ if (!r.ok) { j.stage = stage; throw j; } return j; }); })
      .then(function(j){ show(stage, j); return j; });
  }
  go.addEventListener('click', function(){
    go.disabled = true;
    run('ir', 'subject=' + encodeURIComponent(chosen()))
      .then(function(j){ return run('zig', 'run=' + j.run); })
      .then(function(j){ return run('exe', 'run=' + j.run); })
      .then(function(j){ return run('run', 'run=' + j.run); })
      .then(function(){ status.textContent = 'done'; })
      .catch(function(e){
        status.textContent = (e && e.error) || 'failed';
        if (e && e.stage) {
          document.getElementById('pre-' + e.stage).textContent =
            (e.error || 'failed') + (e.tail ? '\n\n' + e.tail : '');
        }
      })
      .finally(function(){ go.disabled = false; });
  });
})();
</script>
"""
