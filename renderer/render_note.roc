## This program prints one note as HTML. Roc's echo platform gives it its
## arguments and a way to print, nothing else, so the note arrives as arguments.
## Linux stops one argument at 128 KiB, and two notes are bigger than that, so
## essays.render_with_roc passes the text in parts, which this program joins.
app [main!] { md: "../../roc-markdown/package/main.roc" }

import md.Md

main! = |parts| {
	page = Md.render_document(Str.join_with(parts, "").to_utf8(), { fence: fence, images: Shown })
	match Str.from_utf8(page.html) {
		Ok(html) => echo!(html)
		Err(_) => crash "render_note: the renderer wrote bytes that aren't UTF-8"
	}
	Ok({})
}

## A `raw` fence is a note's own HTML. Every other fence stays code, so a dot
## fence reaches the page as class="language-dot", where dot.js draws it.
fence = |{ tag, body, .. }|
	if tag == "raw".to_utf8() {
		Html(body)
	} else {
		Pass
	}
