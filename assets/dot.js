// Renders every ```dot fence in a note as an SVG figure.
//
// The page loads this after viz-standalone.js, and only on a note that has a
// dot fence (essays.view_body decides), so a note is just Markdown with
// ```dot blocks in it: no script, no style.
//
// DEFAULTS fill in only what a graph leaves unset; an attribute written in the
// dot source wins. tools/check_dot.cjs requires this file for the same
// DEFAULTS, so a check renders exactly what a reader sees.
var DOT_DEFAULTS = {
  graphAttributes: { bgcolor: 'transparent', fontname: 'Helvetica' },
  nodeAttributes: { fontname: 'Helvetica', fontsize: 11 },
  edgeAttributes: { fontname: 'Helvetica', fontsize: 10 }
};

if (typeof module !== 'undefined' && module.exports) {
  module.exports = DOT_DEFAULTS;
} else {
  Viz.instance().then(function (viz) {
    document.querySelectorAll('code.language-dot').forEach(function (code) {
      var pre = code.closest('pre');
      try {
        var svg = viz.renderSVGElement(code.textContent, DOT_DEFAULTS);
        var fig = document.createElement('figure');
        fig.className = 'dot';
        fig.appendChild(svg);
        pre.replaceWith(fig);
      } catch (e) {
        var err = document.createElement('div');
        err.className = 'dot-error';
        err.textContent = 'graphviz: ' + e.message;
        pre.appendChild(err);
      }
    });
  }).catch(function (e) {
    console.error('viz load failed', e);
  });
}
