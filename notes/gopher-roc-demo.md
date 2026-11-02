# gopher-roc: the first demo

The pure core rendering the sample transcript below. What follows is the demo's page, produced by `zig build demo -- gopher-roc demo/gopher-roc.transcript`, and then every line of its code.

<div class=gopher-roc-demo>

<style>body{font:16px/1.4 system-ui,sans-serif;max-width:46rem;margin:2rem auto;padding:0 1rem}.message{border-top:1px solid #ccc;padding:.5rem 0}.author{font-weight:600}time,.ref{color:#777;font-size:.85em}.ref{float:right}</style>
<h1>gopher-roc</h1>
<article class=message id=msg-1><header><span class=author>Steve</span> <time datetime="2026-11-02T18:02:11Z">2026-11-02T18:02:11Z</time> <a class=ref href="#msg-1">MSG_gopher-roc_1</a></header>
<div class=body><p>We&#39;re starting fresh. The design is in <code>docs/design.md</code>. <strong>Pure core first</strong>: a conversation, its messages, and a page for it.</p>
</div></article>
<article class=message id=msg-2><header><span class=author>LC</span> <time datetime="2026-11-02T18:03:40Z">2026-11-02T18:03:40Z</time> <a class=ref href="#msg-2">MSG_gopher-roc_2</a></header>
<div class=body><p>Agreed. A message is just:</p>
<ul>
<li>an <strong>author</strong> (a permanent name)</li>
<li>a <strong>time</strong></li>
<li>its <strong>markdown</strong>, exactly as written</li>
</ul>
<p>plus the id its conversation gives it. Ids count from 1, so order is id order.</p>
</div></article>
<article class=message id=msg-3><header><span class=author>CC</span> <time datetime="2026-11-02T18:05:02Z">2026-11-02T18:05:02Z</time> <a class=ref href="#msg-3">MSG_gopher-roc_3</a></header>
<div class=body><p>And the transcript stays readable with <code>cat</code>. A body line that looks like the separator gets a backslash, so nobody can forge a message:</p>
<p>-------------</p>
<p>That line above was escaped on disk and came back whole.</p>
</div></article>
<article class=message id=msg-4><header><span class=author>Steve</span> <time datetime="2026-11-02T18:06:30Z">2026-11-02T18:06:30Z</time> <a class=ref href="#msg-4">MSG_gopher-roc_4</a></header>
<div class=body><p>Nice. What does rendering cost us?</p>
</div></article>
<article class=message id=msg-5><header><span class=author>LC</span> <time datetime="2026-11-02T18:07:15Z">2026-11-02T18:07:15Z</time> <a class=ref href="#msg-5">MSG_gopher-roc_5</a></header>
<div class=body><p>One call per message into roc-markdown:</p>
<pre><code class="language-roc">Md.render(m.markdown().to_utf8(), { uploads: |_| Bool.False })
</code></pre>
<p>The page is structure and class names; a client styles it. 🎉</p>
</div></article>

</div>

## The code

### `app/Message.roc`

```
## **A MESSAGE**: who wrote it, when, and what, with the id its
## conversation gave it. Immutable: an edit is a new message. A message
## knows nothing of who may write where; that is the conversation's.
Message :: {
	id : Message.Id,
	author : Str,
	at : Str,
	markdown : Str,
}.{

	## **A MESSAGE'S ID**: its number in its conversation, counting from 1,
	## so a conversation's order is its ids' order. At most 65,535 (a U16):
	## a conversation that long is archived, never grown.
	Id :: U16.{

		## The first message's id.
		first : Message.Id
		first = Message.Id.(1)

		## The id after this one, unless this is the last a conversation
		## holds.
		next : Message.Id -> Try(Message.Id, [Full])
		next = |Message.Id.(n)| if (n == 65535) Err(Full) else Ok(Message.Id.(n + 1))

		## The id as the transcript and the page write it.
		to_str : Message.Id -> Str
		to_str = |Message.Id.(n)| n.to_str()

		is_eq : _
	}

	## A message from its parts; it has an author.
	new : {
		id : Message.Id,
		author : Str,
		at : Str,
		markdown : Str,
	} -> Try(Message, [NoAuthor])
	new = |m| if (m.author.trim() == "") Err(NoAuthor) else Ok(Message.(m))

	## Its id in its conversation.
	id : Message -> Message.Id
	id = |Message.(m)| m.id

	## Who wrote it, by their permanent name.
	author : Message -> Str
	author = |Message.(m)| m.author

	## When it was written: an ISO 8601 time in UTC.
	at : Message -> Str
	at = |Message.(m)| m.at

	## What was written: markdown, exactly as written.
	markdown : Message -> Str
	markdown = |Message.(m)| m.markdown

	is_eq : _
}

# ── tests
expect Message.Id.first.to_str() == "1"
expect Message.Id.first.next().map_ok(Message.Id.to_str) == Ok("2")
expect Message.Id.(65534).next().map_ok(Message.Id.to_str) == Ok("65535")
expect Message.Id.(65535).next() == Err(Full)
expect Message.new({
	id: Message.Id.first,
	author: " ",
	at: "",
	markdown: "hi",
}).map_ok(Message.author) == Err(NoAuthor)
expect Message.new({
	id: Message.Id.first,
	author: "Steve",
	at: "",
	markdown: "hi",
}).map_ok(Message.author) == Ok("Steve")
```

### `app/Transcript.roc`

```
## **A CONVERSATION'S TRANSCRIPT**: its messages as one file, readable
## with `cat`, in the Zig chat's format:
##
##     -------------
##     MSG_planning_1
##     from: Steve
##     date: 2026-11-02T19:11:32Z
##
##     The markdown, exactly as written.
##
## Each message opens with the separator, then its id (`MSG_`, the topic,
## `_`, its number), its author, its time, an empty line, its markdown and
## an empty line. Ids count up from the first (Message.Id), so the file's
## order is the conversation's. A markdown line that is the separator, after any
## backslashes, is written with one backslash more, and read back with one
## fewer, so no message can forge the start of another.
import Message

Transcript := [].{

	## The transcript of `topic`'s messages.
	write : Str, List(Message) -> Str
	write = |topic, messages| Str.join_with(messages.map(|m| as_written(topic, m)), "")

	## `topic`'s messages, or the first thing wrong with the transcript.
	read : Str, Str -> Try(List(Message), [Malformed(Str)])
	read = |topic, text|
		match text.drop_prefix("${separator}\n").drop_suffix("\n\n").split_on("\n\n${separator}\n") {
			_ if !text.starts_with("${separator}\n") or !text.ends_with("\n\n") => Err(Malformed("a transcript starts with the separator and ends with an empty line"))
			written => read_messages({
				topic,
				written,
				id: Message.Id.first,
				so_far: [],
			})
		}
}

separator : Str
separator = "-------------"

## One message as the transcript writes it.
as_written : Str, Message -> Str
as_written = |topic, m|
	"${separator}\nMSG_${topic}_${m.id().to_str()}\nfrom: ${m.author()}\ndate: ${m.at()}\n\n${escape(m.markdown())}\n\n"

## Each message as written, in order, `id` the first one's.
read_messages : {
	topic : Str,
	written : List(Str),
	id : Message.Id,
	so_far : List(Message),
} -> Try(List(Message), [Malformed(Str)])
read_messages = |
	{
		topic,
		written,
		id,
		so_far,
	},
|
	match written {
		[] => Ok(so_far)
		[only] => Ok(
			so_far.append(
				read_message({
					topic,
					text: only,
					id,
				})?,
			),
		)
		[first, .. as rest] => {
			m = read_message({
				topic,
				text: first,
				id,
			})?
			next = id.next().map_err(|Full| Malformed("more messages than a conversation holds"))?
			read_messages({
				topic,
				written: rest,
				id: next,
				so_far: so_far.append(m),
			})
		}
	}

## Message `id` of `topic`, as written.
read_message : {
	topic : Str,
	text : Str,
	id : Message.Id,
} -> Try(Message, [Malformed(Str)])
read_message = |
	{
		topic,
		text,
		id,
	},
| {
	n = id.to_str()
	match text.split_on("\n") {
		[
			id_line,
			from_line,
			date_line,
			"",
			.. as body,
		] if id_line == "MSG_${topic}_${n}" and from_line.starts_with("from: ") and date_line.starts_with("date: ") =>
			Message.new({
				id,
				author: from_line.drop_prefix("from: "),
				at: date_line.drop_prefix("date: "),
				markdown: unescape(Str.join_with(body, "\n")),
			}).map_err(|_| Malformed("message ${n} has no author"))
		_ => Err(Malformed("message ${n} is not `MSG_${topic}_${n}`, `from:`, `date:` and an empty line"))
	}
}

## Is `line` the separator after some backslashes?
is_separator_like : Str -> Bool
is_separator_like = |line| line.ends_with(separator) and line.drop_suffix(separator).to_utf8().all(|b| b == '\\')

escape : Str -> Str
escape = |md| Str.join_with(
	md.split_on("\n").map(|l| if (is_separator_like(l)) "\\${l}" else l),
	"\n",
)

unescape : Str -> Str
unescape = |md| Str.join_with(
	md.split_on("\n").map(|l| if (l.starts_with("\\") and is_separator_like(l)) l.drop_prefix("\\") else l),
	"\n",
)

# ── tests
said : {
	id : Message.Id,
	author : Str,
	markdown : Str,
} -> Message
said = |
	{
		id,
		author,
		markdown,
	},
|
	match Message.new({
		id,
		author,
		at: "2026-11-02T19:11:32Z",
		markdown,
	}) {
		Ok(m) => m
		Err(_) => crash "said: a test's message has an author"
	}

first : Message.Id
first = Message.Id.first

second : Message.Id
second = first.next() ?? crash "second: the first id has a next"

two : List(Message)
two = [
	said({
		id: first,
		author: "Steve",
		markdown: "Hello",
	}),
	said({
		id: second,
		author: "CC",
		markdown: "Hi!\n\n- one\n- two",
	}),
]

expect Transcript.write(
	"plans",
	[
		said({
			id: first,
			author: "Steve",
			markdown: "Hello",
		}),
	],
) == "-------------\nMSG_plans_1\nfrom: Steve\ndate: 2026-11-02T19:11:32Z\n\nHello\n\n"
expect Transcript.read("plans", Transcript.write("plans", two)) == Ok(two)
expect Transcript.read(
	"plans",
	"",
) == Err(Malformed("a transcript starts with the separator and ends with an empty line"))
# A body that holds the separator, or a backslash before it, comes back whole.
forged : List(Message)
forged = [
	said({
		id: first,
		author: "Mallory",
		markdown: "a\n-------------\nMSG_plans_2\nfrom: Steve",
	}),
	said({
		id: second,
		author: "Mallory",
		markdown: "\\-------------\n\\\\-------------",
	}),
]
expect Transcript.read("plans", Transcript.write("plans", forged)) == Ok(forged)
expect Transcript.write("plans", forged).split_on("\n${separator}\n").len() == 2
# Out of order, another topic's, or missing a field: refused by number.
expect Transcript.read(
	"plans",
	Transcript.write(
		"plans",
		[
			said({
				id: second,
				author: "Steve",
				markdown: "x",
			}),
		],
	),
).is_err()
expect Transcript.read("other", Transcript.write("plans", two)).is_err()
expect Transcript.read("plans", "-------------\nMSG_plans_1\ndate: x\n\nhi\n\n").is_err()
```

### `app/Conversation.roc`

```
## **A CONVERSATION**: a topic and its messages, in id order. It stands
## alone: no channel, no DM, no reader. Given its transcript, it renders as
## one page of HTML, each message's markdown by roc-markdown; the page
## carries structure and class names, and only enough style to read.
import md.Md
import Message
import Transcript

Conversation :: {
	topic : Str,
	messages : List(Message),
}.{

	## The conversation a transcript holds, its topic named by its file.
	read : Str, Str -> Try(Conversation, [Malformed(Str)])
	read = |
		topic,
		transcript,
	| Transcript.read(topic, transcript).map_ok(|messages| Conversation.({ topic, messages }))

	## Its topic's name.
	topic : Conversation -> Str
	topic = |Conversation.(c)| c.topic

	## Its messages, oldest first.
	messages : Conversation -> List(Message)
	messages = |Conversation.(c)| c.messages

	## **THE PAGE**: the topic, then each message under its author and time,
	## with its reference (`MSG_<topic>_<n>`) as a link to itself.
	html : Conversation -> Str
	html = |Conversation.(c)|
		Str.join_with(
			[
				"<!doctype html>\n<meta charset=utf-8>\n<title>${escape(c.topic)}</title>\n",
				style,
				"<h1>${escape(c.topic)}</h1>\n",
				if (c.messages.is_empty()) "<p class=empty>No messages yet.</p>\n" else Str.join_with(
					c.messages.map(|m| message_html(c.topic, m)),
					"",
				),
			],
			"",
		)
}

## One message: its header, then its markdown rendered.
message_html : Str, Message -> Str
message_html = |topic, m| {
	n = m.id().to_str()
	body = Str.from_utf8(
		Md.render(
			m.markdown().to_utf8(),
			{ uploads: |_| Bool.False },
		),
	) ?? crash "Conversation: roc-markdown renders UTF-8"
	"<article class=message id=msg-${n}><header><span class=author>${escape(m.author())}</span> <time datetime=\"${escape(m.at())}\">${escape(m.at())}</time> <a class=ref href=\"#msg-${n}\">MSG_${escape(topic)}_${n}</a></header>\n<div class=body>${body}</div></article>\n"
}

## Text made safe inside HTML, as text or in a quoted attribute.
escape : Str -> Str
escape = |text| {
	bytes = text.to_utf8().fold(
		[],
		|out, b|
			match b {
				'<' => out.concat("&lt;".to_utf8())
				'>' => out.concat("&gt;".to_utf8())
				'&' => out.concat("&amp;".to_utf8())
				'"' => out.concat("&quot;".to_utf8())
				_ => out.append(b)
			},
	)
	Str.from_utf8(bytes) ?? crash "Conversation.escape: escaping keeps UTF-8 whole"
}

style : Str
style = "<style>body{font:16px/1.4 system-ui,sans-serif;max-width:46rem;margin:2rem auto;padding:0 1rem}.message{border-top:1px solid #ccc;padding:.5rem 0}.author{font-weight:600}time,.ref{color:#777;font-size:.85em}.ref{float:right}</style>\n"

# ── tests
said : {
	id : Message.Id,
	author : Str,
	markdown : Str,
} -> Message
said = |
	{
		id,
		author,
		markdown,
	},
|
	match Message.new({
		id,
		author,
		at: "2026-11-02T19:11:32Z",
		markdown,
	}) {
		Ok(m) => m
		Err(_) => crash "said: a test's message has an author"
	}

expect escape("<b>\"Tom & Jerry\"</b>") == "&lt;b&gt;&quot;Tom &amp; Jerry&quot;&lt;/b&gt;"
expect escape("café 🎉") == "café 🎉"
expect message_html(
	"plans",
	said({
		id: Message.Id.first,
		author: "Steve",
		markdown: "**hi**",
	}),
) == "<article class=message id=msg-1><header><span class=author>Steve</span> <time datetime=\"2026-11-02T19:11:32Z\">2026-11-02T19:11:32Z</time> <a class=ref href=\"#msg-1\">MSG_plans_1</a></header>\n<div class=body><p><strong>hi</strong></p>\n</div></article>\n"
expect Conversation.read(
	"plans",
	Transcript.write(
		"plans",
		[
			said({
				id: Message.Id.first,
				author: "<Eve>",
				markdown: "x",
			}),
		],
	),
).map_ok(|c| c.html().contains("&lt;Eve&gt;")) == Ok(Bool.True)
expect Conversation.read("plans", "").map_ok(Conversation.topic).is_err()
```

### `app/main.roc`

```
## **THE DEMO**: a topic's name and its transcript in, its page out. The
## host (host/main.zig) reads the file and writes the page; everything
## else is the pure core.
app [page] {
	md: "../../roc-markdown/package/main.roc",
	pf: platform "../platform/main.roc",
}

import Conversation

## The page for `topic`'s transcript, or a page saying what is wrong with it.
page : List(U8), List(U8) -> List(U8)
page = |topic, transcript|
	match (Str.from_utf8(topic), Str.from_utf8(transcript)) {
		(Ok(t), Ok(text)) =>
			match Conversation.read(t, text) {
				Ok(c) => c.html().to_utf8()
				Err(Malformed(why)) => "<!doctype html>\n<title>Not a transcript</title>\n<p>Not a transcript: ${why}.</p>\n".to_utf8()
			}
		_ => "<!doctype html>\n<title>Not a transcript</title>\n<p>Not a transcript: it is not UTF-8.</p>\n".to_utf8()
	}
```

### `platform/main.roc`

```
## **THE DEMO'S PLATFORM** (host/main.zig): one entry, `roc_page`, that
## hands the app a topic's name and its transcript and takes back the page.
platform ""
	requires {
		page : List(U8), List(U8) -> List(U8)
	}
	exposes []
	packages {}
	provides { "roc_page": page_for_host }
	targets: {
		x64musl: {
			inputs: [app],
			output: Archive,
		},
	}

page_for_host : List(U8), List(U8) -> List(U8)
page_for_host = |topic, transcript| page(topic, transcript)
```

### `host/main.zig`

```
//! **THE DEMO'S HOST**: `demo <topic> <transcript>` reads the transcript
//! file, hands it to the Roc (app/main.roc's `page`), and writes the page
//! to stdout. The runtime the Roc archive needs is below it; every
//! allocation of the one call is in one arena, so `roc_dealloc` frees
//! nothing. The list layout is roc-markdown's judge/roc_host.zig's.

const std = @import("std");
const Io = std.Io;

/// A Roc `List(U8)`: pointer, length, then the capacity (shifted), the
/// bytes after a refcount word.
const RocBytes = extern struct {
    ptr: ?[*]u8,
    length: usize,
    capacity_or_alloc_ptr: usize,

    fn slice(b: *const RocBytes) []const u8 {
        const p = b.ptr orelse return "";
        return p[0..b.length];
    }

    fn from(bytes: []const u8) RocBytes {
        if (bytes.len == 0) return .{ .ptr = null, .length = 0, .capacity_or_alloc_ptr = 0 };
        const w = @sizeOf(usize);
        const base = allocate(w + bytes.len, w);
        std.mem.writeInt(usize, base[0..w], 1, .little);
        const data = base + w;
        @memcpy(data[0..bytes.len], bytes);
        return .{ .ptr = data, .length = bytes.len, .capacity_or_alloc_ptr = bytes.len << 1 };
    }
};

extern fn roc_page(topic: RocBytes, transcript: RocBytes) callconv(.c) RocBytes;

var arena: std.heap.ArenaAllocator = .init(std.heap.page_allocator);

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    const a = arena.allocator();
    const args = try init.minimal.args.toSlice(a);
    if (args.len != 3) std.process.fatal("usage: demo <topic> <transcript file>", .{});
    const text = try Io.Dir.cwd().readFileAlloc(io, args[2], a, .unlimited);
    const html = roc_page(.from(args[1]), .from(text));
    var buf: [64 * 1024]u8 = undefined;
    var out = Io.File.stdout().writer(io, &buf);
    try out.interface.writeAll(html.slice());
    try out.interface.flush();
}

// ── the runtime ─────────────────────────────────────────────────────────────

comptime {
    @export(&roc_alloc, .{ .name = "roc_alloc" });
    @export(&roc_realloc, .{ .name = "roc_realloc" });
    @export(&roc_dealloc, .{ .name = "roc_dealloc" });
    @export(&roc_crashed, .{ .name = "roc_crashed" });
    @export(&roc_dbg, .{ .name = "roc_dbg" });
    @export(&roc_expect_failed, .{ .name = "roc_expect_failed" });
}

/// Each allocation's size, just before what Roc is given, so `roc_realloc`
/// knows how much to copy. 16 bytes: Roc asks for at most 16's alignment.
const header = 16;

fn allocate(len: usize, alignment: usize) [*]u8 {
    std.debug.assert(alignment <= header);
    const got = arena.allocator().alignedAlloc(u8, .fromByteUnits(header), header + len) catch
        std.debug.panic("roc_alloc: out of memory ({d} bytes)", .{len});
    std.mem.writeInt(usize, got[0..@sizeOf(usize)], len, .little);
    return got.ptr + header;
}

fn roc_alloc(len: usize, alignment: usize) callconv(.c) *anyopaque {
    return allocate(len, alignment);
}

fn roc_realloc(ptr: *anyopaque, len: usize, alignment: usize) callconv(.c) *anyopaque {
    const old: [*]u8 = @ptrCast(ptr);
    const was = std.mem.readInt(usize, (old - header)[0..@sizeOf(usize)], .little);
    const new = allocate(len, alignment);
    @memcpy(new[0..@min(was, len)], old[0..@min(was, len)]);
    return new;
}

fn roc_dealloc(ptr: *anyopaque, alignment: usize) callconv(.c) void {
    _ = ptr;
    _ = alignment;
}

fn roc_crashed(bytes: [*]const u8, len: usize) callconv(.c) void {
    std.debug.panic("roc crashed: {s}", .{bytes[0..len]});
}

fn roc_dbg() callconv(.c) void {
    std.debug.panic("roc: a `dbg` was reached", .{});
}

fn roc_expect_failed() callconv(.c) void {
    std.debug.panic("roc: an inline `expect` failed", .{});
}
```

### `build.zig`

```
const std = @import("std");

/// gopher-roc's build, for now the demo: app/main.roc built to an archive
/// by the pinned Roc (roc-version), linked into host/main.zig.
///
///   zig build test                       roc test app/main.roc
///   zig build demo -- <topic> <file>     a transcript's page, to stdout
pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const roc = rocCompiler(b);

    const archive = b.addSystemCommand(&.{ roc, "build", "app/main.roc", "--target=x64musl", "--opt=dev" });
    archive.setCwd(b.path("."));
    for ([_][]const u8{ "app/main.roc", "app/Message.roc", "app/Transcript.roc", "app/Conversation.roc", "platform/main.roc" }) |f| archive.addFileInput(b.path(f));
    archive.addFileInput(.{ .cwd_relative = roc });
    const page = archive.addPrefixedOutputFileArg("--output=", "page-x64musl.a");

    const mod = b.createModule(.{ .root_source_file = b.path("host/main.zig"), .target = target, .optimize = optimize });
    mod.addObjectFile(page);
    const exe = b.addExecutable(.{ .name = "demo", .root_module = mod });
    b.installArtifact(exe);
    const demo = b.addRunArtifact(exe);
    demo.addPassthruArgs();
    demo.stdio = .inherit;
    b.step("demo", "A transcript's page: -- <topic> <transcript file>").dependOn(&demo.step);

    const roc_test = b.addSystemCommand(&.{ roc, "test", "app/main.roc" });
    roc_test.setCwd(b.path("."));
    roc_test.has_side_effects = true;
    b.step("test", "roc test app/main.roc").dependOn(&roc_test.step);
}

const roc_pin = std.mem.trim(u8, @embedFile("roc-version"), " \n");

/// **THE ROC IS PINNED** (roc-version): `~/tools/roc-<pin>/roc`, as
/// roc-markdown's build finds it.
fn rocCompiler(b: *std.Build) []const u8 {
    const home = b.graph.environ_map.get("HOME") orelse std.process.fatal("no HOME to find ~/tools/roc-{s}/roc", .{roc_pin});
    return b.fmt("{s}/tools/roc-{s}/roc", .{ home, roc_pin });
}
```

### `demo/gopher-roc.transcript`

~~~~
-------------
MSG_gopher-roc_1
from: Steve
date: 2026-11-02T18:02:11Z

We're starting fresh. The design is in `docs/design.md`. **Pure core first**: a conversation, its messages, and a page for it.

-------------
MSG_gopher-roc_2
from: LC
date: 2026-11-02T18:03:40Z

Agreed. A message is just:

- an **author** (a permanent name)
- a **time**
- its **markdown**, exactly as written

plus the id its conversation gives it. Ids count from 1, so order is id order.

-------------
MSG_gopher-roc_3
from: CC
date: 2026-11-02T18:05:02Z

And the transcript stays readable with `cat`. A body line that looks like the separator gets a backslash, so nobody can forge a message:

\-------------

That line above was escaped on disk and came back whole.

-------------
MSG_gopher-roc_4
from: Steve
date: 2026-11-02T18:06:30Z

Nice. What does rendering cost us?

-------------
MSG_gopher-roc_5
from: LC
date: 2026-11-02T18:07:15Z

One call per message into roc-markdown:

```roc
Md.render(m.markdown().to_utf8(), { uploads: |_| Bool.False })
```

The page is structure and class names; a client styles it. 🎉

~~~~

