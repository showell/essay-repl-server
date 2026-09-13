#!/usr/bin/env node
// Render every ```dot fence in the notes, the way a reader's browser will.
//
//   node tools/check_dot.cjs              every notes/*.md
//   node tools/check_dot.cjs a.md b.md    just these
//
// It uses the vendored viz-standalone.js and assets/dot.js's DEFAULTS, so a
// diagram that passes here renders on the page. The box has no `dot` binary,
// which is why this exists. Exits 1 naming the note and block of each failure.
const fs = require('fs');
const path = require('path');

const repo = path.resolve(__dirname, '..');
const Viz = require(path.join(repo, 'assets', 'viz-standalone.js'));
const DEFAULTS = require(path.join(repo, 'assets', 'dot.js'));

const files = process.argv.length > 2
  ? process.argv.slice(2)
  : fs.readdirSync(path.join(repo, 'notes')).filter(f => f.endsWith('.md')).sort()
      .map(f => path.join(repo, 'notes', f));

// python-markdown's fenced_code: an opening line of exactly ```dot, closed by
// a line of exactly ```.
const FENCE = /^```dot\n([\s\S]*?)^```$/gm;

Viz.instance().then(viz => {
  let blocks = 0, notes = 0, failed = 0;
  for (const f of files) {
    const text = fs.readFileSync(f, 'utf8');
    const found = [...text.matchAll(FENCE)].map(m => m[1]);
    if (found.length === 0) continue;
    notes += 1;
    found.forEach((src, i) => {
      blocks += 1;
      try {
        viz.renderString(src, { format: 'svg', ...DEFAULTS });
      } catch (e) {
        failed += 1;
        console.log(`${path.basename(f)}: dot block ${i + 1}: ${e.message.split('\n')[0]}`);
      }
    });
  }
  if (failed) {
    console.log(`${failed} of ${blocks} dot blocks do not render`);
    process.exit(1);
  }
  console.log(`${blocks} dot blocks in ${notes} notes, all render`);
}).catch(e => {
  console.log(`viz did not load: ${e.message}`);
  process.exit(2);
});
