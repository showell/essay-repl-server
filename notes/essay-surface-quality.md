# Quality control on today's essay surface

A quick survey, ahead of the new Go server's week. The short version: the essay surface has one hook, one test file and no gate. That has been enough, because its code has changed rarely. Only 23 of its 950 commits since 2026-08-23 touch code; the rest are notes.

## What exists

| Check | What it holds | When it runs |
|---|---|---|
| **pre-commit hook** (`tools/hooks/pre-commit`) | Every staged note's ```dot diagrams render, using the browser's own Viz build (`tools/check_dot.cjs`). A change to `assets/dot.js` checks every note. | On every commit, once `ops/install.sh` sets `core.hooksPath` |
| **`tests/test_render.py`** | 17 unittest cases over both renderers (Python and Roc): front matter, dot fences, raw fences, escaping, images, and the Roc program's failure modes (missing, failing, hung, unknown name), plus argument-part boundaries | By hand. Nothing runs it automatically |
| **The renderer's pin check** (`ops/build_renderer.sh`) | The Roc renderer builds with the pinned compiler, and the pin matches roc-markdown's | When the renderer is built |
| **roc-markdown's own tests** | The renderer itself: 314 spec examples, about a thousand hostile inputs and ten thousand real chat messages (its README) | In that repo, not this one |

## What doesn't exist

- **No gate and no CI.** Nothing runs the tests on a commit or a push, and `.github` is empty.
- **No check of the live server.** Nothing fetches pages, times them, or checks that every note still renders.
- **No guard on comments.** Comments are filed by paragraph number (`para_index`). When the renderer changed from Python to Roc on 2026-11-06, that took a one-off migration script, `ops/move_comments.py`, and `code_review.shale` refuses to rewrite a review with replies for the same reason. That's the most fragile thing in the design.
- **No lint** on the Python, and no formatter.
- **No measure of speed,** though the page is slower than it could be: each render runs the Roc program as a separate process.

## What this means for the week

The new server starts with no inheritance to protect, so its gates can grow the way the book wants them to: as the week asks. The survey suggests the first candidates:
1. **Every note renders.** Fetch all 500, expect 200 and a page with no raw markdown left. It's the obvious Monday or Tuesday heredoc, and later a recipe.
2. **Every page is fast.** A held budget in milliseconds: your reason for Go, made into a gate.
3. **A comment stays on its paragraph.** If the new server anchors comments to the paragraph's text instead of its number, a gate with plants can prove that editing a note keeps comments on the right paragraphs. That fixes today's worst fragility from first principles, and it's a natural Thursday.
4. **Diagrams render.** Carry over the dot check, as a gate this time.
