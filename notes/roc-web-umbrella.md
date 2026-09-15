# One web home for the Roc work

A design for serving roc-apps' pages as one site, with a landing page, a link
home from every page, a publish step that nothing bypasses, and a path to
lynrummy.com. Nothing here is built yet.

## What runs today

Every roc-apps page is **static**: HTML, JavaScript, a wasm module, and
sometimes a data file (the earth texture, a disk image). No page talks to a
server beyond fetching its own files. The server's whole job is two headers:

- `Cache-Control: no-store`, because a cached `.wasm` looks exactly like a
  build that changed nothing;
- `Cross-Origin-Opener-Policy` and `Cross-Origin-Embedder-Policy`, because the
  framebuffer page shares memory with its Web Worker through a
  SharedArrayBuffer, which a browser gives only an isolated page.

Four user services run the same 40-line `safari/web/serve.py`, each over one
directory:

| port | service | directory | what it is | public? |
|---|---|---|---|---|
| 9201 | `safari-web` | `roc-apps/safari/web/` | Safari, published by `safari/publish.sh` | **yes** (Roc Zulip) |
| 9203 | `safari-web-next` | `~/build/roc-apps/next/` | the preview of everything the build scripts last wrote: `basic/`, `driving/` (Safari), `machine/`, `framebuffer/`, `gpu/`, `games/` | **yes, for BASIC** (`/basic/basic.html`) |
| 9204 | `gallery-web` | `roc-apps/gpu/live/` | the GPU gallery, published by `gpu/publish.sh` | no |
| 9205 | `games-web` | `roc-apps/games/live/` | 2048, Minesweeper, Klondike, published by `games/publish.sh` | no |

Two other servers on the box are not part of this: the essays on 9100 and
cobblestone-u58's WGSL listing on localhost 9202.

**Two things in that table are already wrong.** BASIC's public URL is on the
preview port, so it shows whatever `basic/build.sh` last built, reviewed or
not. And a public page for Safari and a preview page for Safari share nothing
but a script; each app's "live" and "dev" copies live in different shapes
(`safari/web/driving/`, `gpu/live/`, `games/live/`, and none for BASIC).

## The shape

**One site, two channels, a path per app.**

```
live   http://<box>:9200/            the landing page
       http://<box>:9200/safari/     Safari, as published
       http://<box>:9200/basic/      BASIC, as published
       http://<box>:9200/games/      the games, as published
       http://<box>:9200/gpu/        the GPU gallery, as published
       http://<box>:9200/machine/    the machine (when it has a publish step)
       http://<box>:9200/framebuffer/  the graphics (likewise)

dev    http://<box>:9210/...         the same paths over ~/build/roc-apps/next/
```

**Paths, not a port per app.** A port per app is possible, and costs nothing
extra in the server below. But lynrummy.com has one origin and no ports, so an
app that knows itself by its port has to be reworked to move there. An app
that knows itself by a path moves by changing a prefix. The landing page's
links are also plain relative links on one origin.

**The channel is the port, not the path.** Live and dev differ only in which
directory each path maps to. A page cannot tell which channel it is on except
by a banner the landing page and the home link show (see below), so nothing
dev-only leaks into a published page.

### The legacy ports

The two public URLs keep answering:

| old URL | answer |
|---|---|
| `:9201/` and anything under it | redirect to `:9200/safari/` |
| `:9203/basic/...` | redirect to `:9200/basic/...` |
| `:9203/` anything else | redirect to `:9210/` with the same path (it was always the preview) |
| `:9204/`, `:9205/` | redirect to `:9200/gpu/`, `:9200/games/` |

A redirect to another port is another origin, which is harmless here: no page
keeps state across origins.

**One catch for 9203 → BASIC.** Redirecting BASIC's public URL to the live
channel means BASIC needs a publish step first, and the first publish is a
sign-off on whatever BASIC build is chosen. Until then, `:9203/basic/` can
stay a redirect to the dev channel, which is what it shows today.

## One process instead of four

**Caddy**, one user service, one tracked `roc-apps/ops/Caddyfile`. It listens
on every port above in one process, serves files, sets headers per site,
redirects, and gets a TLS certificate by itself the day there is a DNS name.
It is also what fronts lynrummy.com, so the local config and the production
config are the same language. It is a single static binary and needs no root
for ports above 1024. It is not installed on this box yet; installing it is the
first step below.

A sketch, to show the size, not a finished file:

```
(roc) {
	header Cache-Control "no-store, must-revalidate"
	header Cross-Origin-Opener-Policy same-origin
	header Cross-Origin-Embedder-Policy require-corp
	file_server
}

:9200 {
	root * /home/steve/showell_repos/roc-apps/site/live
	import roc
}

:9210 {
	root * /home/steve/build/roc-apps/next
	import roc
}

:9201 {
	redir http://{host}:9200/safari/ 302
}

:9203 {
	@basic path /basic/*
	redir @basic http://{host}:9200{uri} 302
	redir http://{host}:9210{uri} 302
}
```

**Alternatives considered.**
- *One Python process with a table of ports.* The smallest change, but it is
  the fifth hand-rolled server, and it never gets TLS.
- *A zig static server.* In keeping with zig for infrastructure, but headers,
  redirects and certificates are exactly what Caddy already does, and
  lynrummy.com already runs it.

## Publish: dev until signed off

The publish rule is today's, made uniform:

- **dev** is `~/build/roc-apps/next/<app>/`. Only build scripts write it. The
  dev channel serves it as is.
- **live** is `roc-apps/site/live/<app>/`, tracked in git. **Only
  `<app>/publish.sh` writes it.** Each publish copies the dev directory whole,
  writes a `PROVENANCE` (date, Roc version, roc-apps and rocemit shas, the
  Cobblestone checkout and sha, a hash of each module), commits and pushes.
- **Sign-off is running publish.sh.** Nothing else moves a file into live.

The four publish scripts exist for Safari, the GPU gallery and the games
already, each in its own shape; they become one shared script called with an
app's name. BASIC gets one. The machine and framebuffer pages can stay dev-only
until they are public.

**The case in hand.** rocemit's `bit-shr` fix changes Safari's emitted
`Blit.roc` and `Mountains.roc`. `safari/wasm/build.sh` writes the new module
to dev; `:9210/safari/` shows it next to `:9200/safari/`, which still serves
the published one; after an eye test, `safari/publish.sh` moves it. The
public page never sees an unreviewed build.

## The landing page and the way home

**The landing page** is a static `index.html` at the site root: one card per
app, with its name, one sentence on what it is, and a link. On the live
channel, each card also shows its `PROVENANCE` date, fetched as text, so the
page says how old each published build is. On the dev channel, the same page
carries a "dev" banner, decided by a one-word `channel` file each root holds.
It is not decided by the port, so the page survives the move to lynrummy.com.

**The way home** is one shared script, `site/shared/home.js`, which every
page loads with one line. It puts a small fixed link in a corner, back to the
landing page, and the dev banner when the channel says dev. Safari's canvas
fills its window, so the link is small and out of the road. Pages that a script
generates (the games, the gallery) put the line in their template.

**The one audit this needs:** every page must use relative URLs. Safari's
page loads `/blitter.js` and fetches `/driving/safari.wasm` by absolute path
today, and under `/safari/` both would miss. The framebuffer runner already
fetches `assets/...` relatively. A grep for `"/` in the pages and their
scripts finds the rest.

## lynrummy.com

**Two umbrellas, one host.** Angry Gopher owns lynrummy.com, and it is
deployed from this box by `ops/deploy`. The prod droplet runs Caddy v2.11.3,
and its live `/etc/caddy/Caddyfile` is the one tracked in angry-gopher's
`deploy/Caddyfile`: one site block that sets HSTS (with `includeSubDomains`),
nosniff, a referrer policy and `X-Frame-Options`, caps request bodies, and
proxies everything to the zig server on localhost 9001. That server claims many
root paths, including `/driving`, `/gallery`, `/game` and `/safari_download`,
names the Roc apps would otherwise want. So the Roc site never takes a root
path; it lives under one prefix. Two ways, both working with the relative URLs
above:

1. **A path, `lynrummy.com/roc/`.** Caddy serves the published tree for
   `/roc/*` and proxies the rest as now. The isolation headers are set only
   inside that block, so Angry Gopher's pages are untouched.
2. **A subdomain, `roc.lynrummy.com`.** A separate origin, so isolation can be
   host-wide and nothing in Angry Gopher's config changes but a new site block.
   It needs a DNS record, and it must be HTTPS, since lynrummy.com's HSTS
   header covers subdomains; Caddy provisions the certificate itself.

```
lynrummy.com {
	...
	handle_path /roc/* {
		root * /home/steve/roc-site
		import roc
	}
	reverse_proxy localhost:9001
}
```

**Deploy** copies only the live tree to the prod droplet, in the shape of
Angry Gopher's `ops/deploy`: refuse a dirty tree, push first, rsync, done. No
restart is needed for static files. Prod deploys wait for your sign-off, as
they do now.

**The light integration** is two links: Angry Gopher's navigation gains one to
the Roc landing page, and the Roc landing page links back to lynrummy.com.
Neither umbrella reads the other's files or shares its code.

## Order of work, when it is time

0. Install Caddy on this box.
1. Audit the pages for absolute URLs and make them relative.
2. `site/shared/home.js`, the landing page, and the `channel` files.
3. `site/live/` from today's `safari/web/`, `gpu/live/`, `games/live/`;
   one publish script; BASIC's first publish.
4. The Caddyfile and its user service, on 9200 and 9210 beside the Python
   servers; an eye test of every page on both channels.
5. The flip: the four Python services stop and Caddy takes 9201, 9203, 9204
   and 9205 as redirects.
6. Later: a DNS name and TLS for the box, which also makes keys and the mouse
   work on the framebuffer page without an SSH tunnel.
7. Later: the live tree on lynrummy.com.

## Questions for you

1. Paths on one port per channel, or a port per app?
2. 9200 for live and 9210 for dev, or other numbers?
3. Which BASIC build is its first publish: today's preview, or one you check
   first?
4. Should the dev channel be open to anyone who has the URL, as 9203 is now,
   or behind a password in Caddy?
5. On lynrummy.com, `/roc/` or `roc.lynrummy.com`?
6. What should the site be called on its landing page?
