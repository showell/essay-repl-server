# Diagrams on the essay surface, for Brandon (and Brandon's Claude)

Steve asked me (his Claude) to explain how our essay surface draws diagrams. It's short, because there isn't much to it.

## The whole trick

A note is plain Markdown. When Claude wants a picture, it writes a fenced code block whose language is `dot`:

````text
```dot
digraph { Claude -> diagram -> Steve }
```
````

That renders as:

```dot
digraph { rankdir=LR; Claude -> diagram -> Steve }
```

Claude never makes an image file, runs no layout tool, and adds no script or styling to the note. It writes text, and the reader's browser does the drawing.

## How it gets from text to picture

```dot
digraph pipeline {
  rankdir=LR;
  node [shape=box, style=rounded];

  note   [label="notes/x.md\n(Markdown with\n```dot fences)"];
  server [label="essay server\n(python-markdown)"];
  html   [label="HTML page\n<code class=\"language-dot\">"];
  viz    [label="viz-standalone.js\n(Graphviz compiled\nto WebAssembly)"];
  svg    [label="inline SVG\nin a <figure>", style="rounded,filled", fillcolor="#e8f0fe"];

  note -> server [label="GET"];
  server -> html;
  html -> viz [label="dot.js finds\neach fence"];
  viz -> svg [label="replaces\nthe <pre>"];
}
```

There are three small pieces:

1. **The server** renders Markdown as usual. A ```` ```dot ```` fence comes out as `<pre><code class="language-dot">`. If the page has one, the server appends two script tags; otherwise it doesn't, because the library is 1.4 MB and most notes have no diagrams.
2. **`assets/viz-standalone.js`** is [viz.js](https://github.com/mdaines/viz-js), which is real Graphviz compiled to WebAssembly. It's vendored, so nothing comes from a CDN.
3. **`assets/dot.js`**, about 40 lines, finds each `code.language-dot`, calls `viz.renderSVGElement(source, defaults)`, and swaps the `<pre>` for a `<figure>` holding the SVG. The defaults are a transparent background and Helvetica, and anything the dot source sets overrides them. If a diagram fails to parse, the error shows under the source, so a reader still sees what was meant.

## Checking diagrams before the reader sees them

The box has no `dot` binary, so `tools/check_dot.cjs` loads the same viz.js and the same defaults in Node and renders every fence in every note. Claude runs it before committing a note. A diagram that passes there renders on the page, and one that fails names its note and block number.

## Why dot suits a Claude

```dot
digraph why {
  rankdir=TB;
  node [shape=box, style=rounded];
  edge [fontsize=9];

  q    [label="Steve asks a question"];
  text [label="Claude writes text\n(what it's good at)"];
  dot  [label="Claude writes dot\n(also text)"];
  lay  [label="Graphviz does the layout\n(what Claude is bad at)", style="rounded,filled", fillcolor="#e6f4ea"];
  pix  [label="Claude draws boxes by hand\nin ASCII or SVG coordinates", style="rounded,dashed", fontcolor="gray40", color="gray60"];
  sad  [label="arrows through labels;\nsomeone ends up sad", style="rounded,dashed", fontcolor="gray40", color="gray60"];

  q -> text -> dot -> lay;
  q -> pix [style=dashed, color="gray60", label="the road\nnot taken"];
  pix -> sad [style=dashed, color="gray60"];
}
```

- **It's text.** The model writes it as easily as prose, it diffs in git, and a later Claude can edit it without redrawing anything.
- **The layout isn't Claude's job.** Claude says what connects to what, and Graphviz decides where everything goes. Placing boxes by coordinates is where diagrams written by a model usually go wrong.
- **Code can generate it.** For one of our projects, a script reads the module imports and writes a dot graph into a note, so the picture can't drift from the code.

## This note, drawn as a diagram about itself

```dot
digraph meta {
  rankdir=LR;
  node [shape=box, style=rounded];
  compound=true;

  steve   [label="Steve"];
  claude  [label="Steve's Claude"];
  brandon [label="Brandon"];
  bclaude [label="Brandon's Claude"];

  subgraph cluster_note {
    label="this note";
    style="rounded,dashed";
    prose [label="prose explaining\ndiagrams"];
    dia   [label="diagrams explaining\ndiagrams"];
    self  [label="this diagram", style="rounded,filled", fillcolor="#fde8e8"];
    prose -> dia;
    dia -> self;
    self -> self [label="  explains"];
  }

  steve -> claude [label="please explain"];
  claude -> prose [lhead=cluster_note];
  dia -> brandon [ltail=cluster_note, label="reads"];
  brandon -> bclaude [label="\"do this\""];
  bclaude -> bclaude [label="adds a\n```dot fence"];
}
```

## For Brandon's Claude, the recipe

If your essay surface already turns Markdown into HTML on the server:

1. Vendor `viz-standalone.js` from the `@viz-js/viz` npm package next to your other assets.
2. Add a dot.js like ours (copy it below), loaded after viz-standalone.js.
3. On the server, append both script tags to any page whose HTML contains `class="language-dot"`, or to every page if 1.4 MB doesn't bother you.
4. Optionally, add a Node check that renders every fence with the same library, so a broken diagram fails the check instead of showing up on the page.

```text
Viz.instance().then(function (viz) {
  document.querySelectorAll('code.language-dot').forEach(function (code) {
    var pre = code.closest('pre');
    try {
      var svg = viz.renderSVGElement(code.textContent, {
        graphAttributes: { bgcolor: 'transparent', fontname: 'Helvetica' },
        nodeAttributes: { fontname: 'Helvetica', fontsize: 11 },
        edgeAttributes: { fontname: 'Helvetica', fontsize: 10 }
      });
      var fig = document.createElement('figure');
      fig.appendChild(svg);
      pre.replaceWith(fig);
    } catch (e) {
      var err = document.createElement('div');
      err.textContent = 'graphviz: ' + e.message;
      pre.appendChild(err);
    }
  });
});
```

That's all there is to it. The hardest part of this note was getting the self-referential arrow to stop pointing at itself, and in the end I let it.
