"""The online REPL: watch the fib rung get compiled, then watch it run.

Four stages, the ladder's native loop with the QEMU taken out, ending
where a compiler pipeline should -- at the program's own output:

    stage ir    bin/codexir     fib-subject.codex on stdin -> IR on stderr
    stage zig   bin/zigemit     the IR on stdin -> zig source on stderr
    stage exe   zig build-exe   fib.zig -> a native binary
    stage run   ./fib           the binary runs; its output is the pane

Each stage is bounded the way the ladder bounds its own arms
(systemd-run --user --scope MemoryMax, plus a timeout). The run stage
executes GENERATED code, so its scope also carries RuntimeMaxSec:
systemd kills the whole scope even if our own timeout misses --
subprocess timeouts kill only the direct child, and an orphaned
grandchild is exactly the runaway this page must not mint. Nothing here
touches QEMU, so nothing here needs the box's one-compute-job lock;
when a QEMU-path stage arrives it will take that lock and users wait.

Running requires an account; reading results does not. One run at a
time -- the second clicker gets a 409, not a queue.
"""
import html
import subprocess
import threading
import time

from flask import Blueprint, Response, abort, jsonify, request

import auth
import config
from shell import page

bp = Blueprint('repl', __name__)

RUN_LOCK = threading.Lock()

STAGES = {
    'ir': {
        'kind': 'transform',
        'binary': config.REPL_BIN / 'codexir',
        'reads': config.REPL_SUBJECT,
        'writes': config.REPL_OUT / 'fib.ir',
        'label': 'Codex source -> IR (bin/codexir)',
        'pretty': True,
    },
    'zig': {
        'kind': 'transform',
        'binary': config.REPL_BIN / 'zigemit',
        'reads': config.REPL_OUT / 'fib.ir',
        'writes': config.REPL_OUT / 'fib.zig',
        'label': 'IR -> zig source (bin/zigemit)',
        'skip_prelude': True,
    },
    'exe': {
        'kind': 'build',
        'reads': config.REPL_OUT / 'fib.zig',
        'writes': config.REPL_OUT / 'fib',
        'label': 'zig source -> native binary (zig build-exe)',
    },
    'run': {
        'kind': 'execute',
        'reads': config.REPL_OUT / 'fib',
        'writes': config.REPL_OUT / 'fib.out',
        'label': 'The program runs (./fib)',
    },
}

# The outputs the raw-view route may serve, by name. The binary is not
# here on purpose: this route says text/plain and means it.
RAW = {
    'fib.codex': lambda: config.REPL_SUBJECT,
    'fib.ir': lambda: config.REPL_OUT / 'fib.ir',
    'fib.zig': lambda: config.REPL_OUT / 'fib.zig',
    'fib.out': lambda: config.REPL_OUT / 'fib.out',
}

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
    tool = spec['binary'] if spec['kind'] == 'transform' else (
        config.REPL_ZIG if spec['kind'] == 'build' else spec['reads'])
    if not tool.is_file():
        missing = ('no natives installed -- run ops/refresh_natives.sh'
                   if spec['kind'] == 'transform' else f'missing {tool}')
        return jsonify(error=missing), 503
    if not spec['reads'].is_file():
        return jsonify(error=f'missing input {spec["reads"].name} -- run the prior stage'), 409
    if not RUN_LOCK.acquire(blocking=False):
        return jsonify(error='a run is already in progress'), 409
    try:
        config.REPL_OUT.mkdir(parents=True, exist_ok=True)
        runner = {'transform': _transform, 'build': _build, 'execute': _execute}
        return runner[spec['kind']](stage, spec)
    except subprocess.TimeoutExpired as e:
        return jsonify(error=f'stage {stage} exceeded {e.timeout}s'), 500
    finally:
        RUN_LOCK.release()


def bounded(cmd, stage_timeout, stdin=None, cwd=None, scope_props=()):
    """One process under a systemd scope with the ladder's resident bound.
    Extra scope properties ride along for the stages that need more than
    a memory ceiling."""
    wrapped = ['systemd-run', '--user', '--scope', '--quiet',
               '-p', f'MemoryMax={config.REPL_MEMORY_MAX}']
    for p in scope_props:
        wrapped += ['-p', p]
    started = time.monotonic()
    r = subprocess.run(wrapped + cmd, stdin=stdin, capture_output=True,
                       timeout=stage_timeout, cwd=cwd)
    return r, round(time.monotonic() - started, 2)


def _transform(stage, spec):
    with open(spec['reads'], 'rb') as f:
        r, seconds = bounded([str(spec['binary'])], config.REPL_TIMEOUT, stdin=f)
    # The natives speak the pipeline's convention: product on stderr,
    # progress chatter on stdout.
    if r.returncode != 0 or not r.stderr:
        return jsonify(error=f'stage {stage} failed rc={r.returncode}',
                       tail=r.stdout.decode(errors='replace')[-2000:]), 500
    spec['writes'].write_bytes(r.stderr)
    return jsonify(stage=stage, seconds=seconds,
                   bytes=len(r.stderr), out=spec['writes'].name,
                   preview=preview(spec['writes'], pretty=spec.get('pretty', False),
                                   skip_prelude=spec.get('skip_prelude', False)))


def _build(stage, spec):
    """zig build-exe: the product is a FILE, and stderr is diagnostics --
    the opposite convention from the natives, worth not conflating."""
    spec['writes'].unlink(missing_ok=True)
    r, seconds = bounded(
        [str(config.REPL_ZIG), 'build-exe', spec['reads'].name,
         '-femit-bin=' + spec['writes'].name],
        config.REPL_TIMEOUT, cwd=config.REPL_OUT)
    diags = r.stderr.decode(errors='replace')
    if r.returncode != 0 or not spec['writes'].is_file():
        return jsonify(error=f'stage {stage} failed rc={r.returncode}',
                       tail=diags[-2000:]), 500
    return jsonify(stage=stage, seconds=seconds,
                   bytes=spec['writes'].stat().st_size, out=None,
                   preview=diags.strip() or '(clean compile; the binary is the product)')


def _execute(stage, spec):
    """The generated program itself. RuntimeMaxSec on the scope is the
    backstop our subprocess timeout cannot be: it kills the whole scope,
    grandchildren included, and fires first on purpose."""
    r, seconds = bounded(
        [str(spec['reads'])], config.REPL_RUN_TIMEOUT + 5,
        scope_props=(f'RuntimeMaxSec={config.REPL_RUN_TIMEOUT}',))
    # The emitted runtime prints through std.debug.print, so the program's
    # answer arrives on stderr; stdout is anything the runtime adds.
    out = r.stderr + r.stdout
    spec['writes'].write_bytes(out)
    if r.returncode != 0:
        return jsonify(error=f'the program exited rc={r.returncode}',
                       tail=out.decode(errors='replace')[-2000:]), 500
    return jsonify(stage=stage, seconds=seconds,
                   bytes=len(out), out=spec['writes'].name,
                   preview=preview(spec['writes']))


@bp.route('/repl/raw/<name>')
def raw(name):
    path_for = RAW.get(name)
    if path_for is None or not path_for().is_file():
        abort(404)
    return Response(path_for().read_bytes(), mimetype='text/plain')


@bp.route('/repl')
def repl_page():
    user = auth.current_user()
    subject_ready = config.REPL_SUBJECT.is_file()
    panes = []
    src_preview = preview(config.REPL_SUBJECT) if subject_ready else ''
    src_bytes = config.REPL_SUBJECT.stat().st_size if subject_ready else 0
    panes.append(_pane('source', 'The fib program (fib.codex)',
                       src_preview, src_bytes, 'fib.codex'))
    # The stage panes always load empty: compiling is the page's whole
    # act, and a cached artifact would rob the button of its reveal.
    for stage, spec in STAGES.items():
        panes.append(_pane(stage, spec['label'], '', 0, spec['writes'].name))
    body = (
        '<h1>REPL</h1>'
        '<p class="sub">A sixteen-line fib program -- recursion, an entry '
        'point, one printed answer -- compiled to IR and then to zig by the '
        'same native executables the ladder banks with, then built into a '
        'native binary and RUN. The last pane is the program\'s own output. '
        'No QEMU anywhere. The IR pane is pretty-printed; "full" links serve '
        'the raw artifact.</p>'
        f'<pre class="prov">{html.escape(provenance())}</pre>'
        + (f'<p><button id="go">Compile and run fib</button> '
           f'<span id="status" class="muted"></span></p>' if user else
           '<p class="muted"><a href="/login?next=/repl">Log in</a> to run '
           'the compiler.</p>')
        + ''.join(panes) + REPL_JS)
    return page('REPL', user, body)


def _pane(key, label, text, size, rawname):
    shown = html.escape(text) if text else '<span class="muted">(awaiting a run)</span>'
    meta = f'{size:,} bytes · <a href="/repl/raw/{rawname}">full</a>' if size else ''
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
  var go = document.getElementById('go');
  if (!go) return;
  var status = document.getElementById('status');
  function show(stage, data) {
    document.getElementById('pre-' + stage).textContent = data.preview;
    document.getElementById('meta-' + stage).innerHTML =
      data.bytes.toLocaleString() + ' bytes · ' + data.seconds + 's' +
      (data.out ? ' · <a href="/repl/raw/' + data.out + '">full</a>' : '');
  }
  function run(stage) {
    status.textContent = 'running ' + stage + '...';
    return fetch('/repl/run/' + stage, {method: 'POST'})
      .then(function(r){ return r.json().then(function(j){ if (!r.ok) { j.stage = stage; throw j; } return j; }); })
      .then(function(j){ show(stage, j); return j; });
  }
  go.addEventListener('click', function(){
    go.disabled = true;
    run('ir')
      .then(function(){ return run('zig'); })
      .then(function(){ return run('exe'); })
      .then(function(){ return run('run'); })
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
