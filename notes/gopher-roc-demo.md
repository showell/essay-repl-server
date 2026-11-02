# gopher-roc: the first demo

The pure core rendering the sample transcript below. What follows is the demo's page, produced by `zig build demo -- gopher-roc demo/gopher-roc.transcript`, and then every line of its code.

<div class=gopher-roc-demo>

<style>
body{font:16px/1.4 system-ui,sans-serif;max-width:46rem;margin:2rem auto;padding:0 1rem}
.message{border-top:1px solid #ccc;padding:.5rem 0}
.author{font-weight:600}
time,.ref{color:#777;font-size:.85em}
.ref{float:right}
</style>
<h1>gopher-roc</h1>
<article class="message" id="msg-1"><header><span class="author">Steve</span> <time datetime="2026-11-02T18:02:11Z">2026-11-02T18:02:11Z</time> <a class="ref" href="#msg-1">MSG_gopher-roc_1</a></header>
<div class="body"><p>We&#39;re starting fresh. The design is in <code>docs/design.md</code>. <strong>Pure core first</strong>: a conversation, its messages, and a page for it.</p>
</div></article>
<article class="message" id="msg-2"><header><span class="author">LC</span> <time datetime="2026-11-02T18:03:40Z">2026-11-02T18:03:40Z</time> <a class="ref" href="#msg-2">MSG_gopher-roc_2</a></header>
<div class="body"><p>Agreed. A message is just:</p>
<ul>
<li>an <strong>author</strong> (a permanent name)</li>
<li>a <strong>time</strong></li>
<li>its <strong>markdown</strong>, exactly as written</li>
</ul>
<p>plus the id its conversation gives it. Ids count from 1, so order is id order.</p>
</div></article>
<article class="message" id="msg-3"><header><span class="author">CC</span> <time datetime="2026-11-02T18:05:02Z">2026-11-02T18:05:02Z</time> <a class="ref" href="#msg-3">MSG_gopher-roc_3</a></header>
<div class="body"><p>And the transcript stays readable with <code>cat</code>. A body line that looks like the separator gets a backslash on disk, so nobody can forge a message. In a code block, which shows every byte:</p>
<pre><code>-------------
</code></pre>
<p>That line was escaped on disk and came back whole, with no backslash.</p>
</div></article>
<article class="message" id="msg-4"><header><span class="author">Steve</span> <time datetime="2026-11-02T18:06:30Z">2026-11-02T18:06:30Z</time> <a class="ref" href="#msg-4">MSG_gopher-roc_4</a></header>
<div class="body"><p>Nice. What does rendering cost us?</p>
</div></article>
<article class="message" id="msg-5"><header><span class="author">LC</span> <time datetime="2026-11-02T18:07:15Z">2026-11-02T18:07:15Z</time> <a class="ref" href="#msg-5">MSG_gopher-roc_5</a></header>
<div class="body"><p>One call per message into roc-markdown, through <code>Html</code>:</p>
<pre><code class="language-roc">Html.markdown(payload.markdown)
</code></pre>
<p>The page is structure and class names; a client styles it. 🎉</p>
</div></article>

</div>

## The code

### `app/Ascii.roc`

```
## **ASCII BYTE CHECKS**: the byte classes the strict names and the
## timestamp's form are made of, each with one home here, so no other module
## writes a byte range. Cribbed from roc-chat's `app/Ascii.roc`, which keeps
## its own copy, on purpose, until a package both can share exists.
##
## **ONE BYTE AT A TIME, SAFE ON UTF-8 BY CONSTRUCTION.** Every byte of a
## multi-byte UTF-8 character is 128 or above, and every check here answers
## `Bool.False` for it, so these run over `Str.to_utf8` bytes as they are,
## never splitting a character.
Ascii :: [].{

	## `0`-`9` (48-57). Zig `isDigit`, Rust `is_ascii_digit`, C `isdigit`.
	is_digit : U8 -> Bool
	is_digit = |c| c >= '0' and c <= '9'

	## `A`-`Z` and `a`-`z` (65-90, 97-122). Zig `isAlphabetic`, Rust
	## `is_ascii_alphabetic`, C `isalpha`; `é` (bytes 195 169) is no letter.
	is_letter : U8 -> Bool
	is_letter = |c| (c >= 'A' and c <= 'Z') or (c >= 'a' and c <= 'z')

	## 0-31 and DEL (127): every ASCII byte that is not printable. Zig
	## `isControl`, Rust `is_ascii_control`, C `iscntrl`.
	is_control : U8 -> Bool
	is_control = |c| c < ' ' or c == del
}

## DEL, the one control byte above the printable ones. Roc's character
## literals have no escape for it.
del : U8
del = 127

# ── tests
# Each set is written out as its members, not as the ranges the code tests,
# and every check is held to it over all 256 bytes.
all_bytes : List(U8)
all_bytes = List.from_iter(U8.to(0, 255))

controls : List(U8)
controls = List.from_iter(U8.until(0, ' ')).append(del)

expect all_bytes.len() == 256
expect all_bytes.keep_if(Ascii.is_digit) == "0123456789".to_utf8()
expect all_bytes.keep_if(Ascii.is_letter) == "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz".to_utf8()
expect all_bytes.keep_if(Ascii.is_control) == controls
expect controls.len() == 33
# The bytes on each side of every range: of each probe, the members.
expect "/09:".to_utf8().keep_if(Ascii.is_digit) == "09".to_utf8()
expect "@AZ[`az{".to_utf8().keep_if(Ascii.is_letter) == "AZaz".to_utf8()
expect [
	0,
	31,
	' ',
	'~',
	127,
	128,
	255,
].keep_if(Ascii.is_control) == [
	0,
	31,
	127,
]
```

### `app/Author.roc`

```
## **AN AUTHOR**: who wrote a message, by their permanent name, exactly as
## they signed up (names are case-sensitive). Opaque, so `from_str` is the
## only way in: a name is never blank, and never holds a control byte, which
## could end the transcript's `from:` line early or hide in a page.
import Ascii

Author :: Str.{

	## The author named `name`, unless it is blank or holds a control byte.
	from_str : Str -> Try(Author, [Blank, ControlByte])
	from_str = |name|
		if (name.trim().is_empty())
			Err(Blank)
		else if (name.to_utf8().any(Ascii.is_control))
			Err(ControlByte)
		else
			Ok(Author.(name))

	## The name, exactly as given.
	to_str : Author -> Str
	to_str = |Author.(name)| name

	is_eq : _
}

# ── tests
expect Author.from_str("") == Err(Blank)
expect Author.from_str(" ") == Err(Blank)
expect Author.from_str("\t") == Err(Blank)
expect Author.from_str("\n") == Err(Blank)
expect Author.from_str("\r") == Err(Blank)
expect Author.from_str("\u(a0)") == Err(Blank)
expect Author.from_str("Ste\nve") == Err(ControlByte)
expect Author.from_str("Steve\r") == Err(ControlByte)
expect Author.from_str(" Zoë\t") == Err(ControlByte)
# Every control byte refused, the first and last of each run and DEL; the
# printable bytes beside them, and a byte past ASCII, kept.
expect Author.from_str("a\u(0)") == Err(ControlByte)
expect Author.from_str("a\u(1f)") == Err(ControlByte)
expect Author.from_str("a\u(7f)") == Err(ControlByte)
expect Author.from_str("a ~").map_ok(Author.to_str) == Ok("a ~")
expect Author.from_str("a¡").map_ok(Author.to_str) == Ok("a¡")
expect Author.from_str("S").map_ok(Author.to_str) == Ok("S")
expect Author.from_str("Steve Howell").map_ok(Author.to_str) == Ok("Steve Howell")
expect Author.from_str(" Zoë ").map_ok(Author.to_str) == Ok(" Zoë ")
```

### `app/Conversation.roc`

```
## **A CONVERSATION**: a topic and its messages, in id order. It stands
## alone: no channel, no DM, no reader, no file. It grows only by `append`,
## which gives each payload the next id, so a conversation whose ids skip,
## repeat or run backwards can't be built.
import Message
import Topic

Conversation :: {
	topic : Topic,
	messages : List({ id : Message.Id, payload : Message.Payload }),
}.{

	## A conversation with no messages yet.
	empty : Topic -> Conversation
	empty = |topic| Conversation.({ topic, messages: [] })

	## The conversation with `payload` added as its next message, unless it
	## already holds as many as an id can number.
	append : Conversation, Message.Payload -> Try(Conversation, [Full])
	append = |before, payload| {
		id = before.next_id()?
		Conversation.(c) = before
		Ok(Conversation.({ ..c, messages: c.messages.append({ id, payload }) }))
	}

	## The id `append` gives the next message, unless the conversation is
	## full.
	next_id : Conversation -> Try(Message.Id, [Full])
	next_id = |Conversation.(c)|
		match c.messages.last() {
			Ok(latest) => latest.id.next()
			Err(ListWasEmpty) => Ok(Message.Id.first)
		}

	## Its topic.
	topic : Conversation -> Topic
	topic = |Conversation.(c)| c.topic

	## Its messages, oldest first, each with the id `append` gave it.
	messages : Conversation -> List({ id : Message.Id, payload : Message.Payload })
	messages = |Conversation.(c)| c.messages

	is_eq : _
}
```

### `app/ConversationSpec.roc`

```
## **CONVERSATION'S TESTS**: numbering by `append`, from the first id to
## the last a conversation holds.
import Conversation
import Message
import Sample

ConversationSpec :: [].{}

expect Conversation.empty(Sample.plans).messages() == []
expect Conversation.empty(Sample.plans).topic() == Sample.plans
expect Conversation.empty(Sample.plans).next_id() == Ok(Sample.first)
# Each append takes the next id, in order.
expect Sample.two.messages() == [
	{ id: Sample.first, payload: Sample.hello },
	{ id: Sample.second, payload: Sample.reply },
]
expect Sample.two.next_id().map_ok(Message.Id.to_str) == Ok("3")
expect Sample.conversation(Sample.plans, [Sample.hello]).next_id() == Ok(Sample.second)
expect Sample.two.topic() == Sample.plans
# The last id at, under and over the highest: 65,534 messages take one
# more, the 65,535th, and then none.
expect {
	almost = Sample.almost_full({})
	full = almost.append(Sample.reply) ?? crash "ConversationSpec: the 65,535th message fits"
	last = full.messages().last().map_ok(|m| m.id.to_str())
	(almost.next_id().map_ok(Message.Id.to_str) == Ok("65535")
		and full.messages().len() == 65535
		and last == Ok("65535")
		and full.next_id() == Err(Full)
		and full.append(Sample.hello) == Err(Full))
}
```

### `app/Html.roc`

```
## **AN `Html` IS SAFE BY CONSTRUCTION**: opaque (`::`), so outside this
## module nothing makes one from a `Str`. The ways in: `text` (anything a
## person, an agent or a file supplied, escaped), `markdown` (a message's
## markdown, rendered by roc-markdown, the one HTML this chat does not
## write), `tag` (an element the pages use, its attributes typed and their
## values escaped), `doctype` and `style` (the page's head, fixed) and
## `join`. `to_str` is the one way out.
import md.Md
import Timestamp

Html :: Str.{

	## **AN ELEMENT A PAGE USES**: a closed set, so a tag's name is never data.
	Name : [A, Article, Div, H1, Header, P, Span, Time, Title]

	## **AN ATTRIBUTE, ITS NAME BY ITS TAG**, so a name and its value can't
	## be swapped, and a time is a `Timestamp`, never any text.
	Attribute : [
		Class(Str),
		Id(Str),
		Href(Str),
		Datetime(Timestamp),
	]

	## **TEXT AS HTML TEXT**: its `&`, `<`, `>`, `"` and `'` as entities, so
	## no text a page writes is ever markup, in an element or an attribute.
	## `&` goes first, so no entity this writes is escaped again.
	text : Str -> Html
	text = |s|
		Html.(
			s
				.replace_each("&", "&amp;")
				.replace_each("<", "&lt;")
				.replace_each(">", "&gt;")
				.replace_each("\"", "&quot;")
				.replace_each("'", "&#39;"),
		)

	## **A MESSAGE'S MARKDOWN, RENDERED** by roc-markdown, which escapes the
	## text and allows only its own markup. No upload is known yet, so every
	## image is refused as one.
	markdown : Str -> Html
	markdown = |md| {
		rendered = Md.render(md.to_utf8(), { uploads: |_| Bool.False })
		Html.(Str.from_utf8(rendered) ?? crash "Html.markdown: roc-markdown renders UTF-8 from UTF-8")
	}

	## **AN ELEMENT**: `<name a="v">inner</name>`, each attribute's value
	## escaped as text and quoted, so no value is ever spliced into a tag.
	tag : {
		name : Html.Name,
		attrs : List(Html.Attribute),
		inner : Html,
	} -> Html
	tag = |
		{
			name,
			attrs,
			inner,
		},
	| {
		opened = Str.join_with(attrs.map(attribute), "")
		written = name_of(name)
		Html.("<${written}${opened}>${inner.to_str()}</${written}>")
	}

	## The pieces, in order.
	join : List(Html) -> Html
	join = |pieces| Html.(Str.join_with(pieces.map(Html.to_str), ""))

	## The doctype and the charset, which every page opens with.
	doctype : Html
	doctype = Html.("<!doctype html>\n<meta charset=utf-8>\n")

	## **A STYLE SHEET**: `css` in a `<style>` element. CSS is code, never
	## data, and holds no `<`, so it can't close its element early.
	style : Str -> Html
	style = |css|
		if (css.contains("<"))
			crash "Html.style: a style sheet holds no `<`"
		else
			Html.("<style>\n${css}</style>\n")

	## The page's text, once, for the host.
	to_str : Html -> Str
	to_str = |Html.(s)| s
}

name_of : Html.Name -> Str
name_of = |name|
	match name {
		A => "a"
		Article => "article"
		Div => "div"
		H1 => "h1"
		Header => "header"
		P => "p"
		Span => "span"
		Time => "time"
		Title => "title"
	}

## One attribute as an element's open tag writes it, space first.
attribute : Html.Attribute -> Str
attribute = |attr| {
	(name, value) =
		match attr {
			Class(v) => ("class", v)
			Id(v) => ("id", v)
			Href(v) => ("href", v)
			Datetime(t) => ("datetime", t.to_str())
		}
	" ${name}=\"${Html.text(value).to_str()}\""
}

# ── tests
expect Html.text("Bea <i>x</i> & \"co\" 'q'").to_str() == "Bea &lt;i&gt;x&lt;/i&gt; &amp; &quot;co&quot; &#39;q&#39;"
expect Html.text("&lt;").to_str() == "&amp;lt;"
expect Html.text("café 🎉").to_str() == "café 🎉"
# A value holding a quote and a script is text inside its attribute.
expect
	Html.tag({
		name: Span,
		attrs: [Class("<script>\"")],
		inner: Html.text("<i>"),
	}).to_str()
		== "<span class=\"&lt;script&gt;&quot;\">&lt;i&gt;</span>"
expect
	Html.tag({
		name: A,
		attrs: [Id("x"), Href("#y")],
		inner: Html.join([]),
	}).to_str()
		== "<a id=\"x\" href=\"#y\"></a>"
expect
	Html.tag({
		name: P,
		attrs: [],
		inner: Html.text("hi"),
	}).to_str()
		== "<p>hi</p>"
expect
	Timestamp.from_str("2026-11-02T19:11:32Z").map_ok(
		|t|
			Html.tag({
				name: Time,
				attrs: [Datetime(t)],
				inner: Html.join([]),
			}).to_str(),
	)
		== Ok("<time datetime=\"2026-11-02T19:11:32Z\"></time>")
expect [A, Article, Div, H1, Header, P, Span, Time, Title].map(name_of) == [
	"a",
	"article",
	"div",
	"h1",
	"header",
	"p",
	"span",
	"time",
	"title",
]
expect Html.join([
	Html.text("a&b"),
	Html.text("<"),
]).to_str() == "a&amp;b&lt;"
# The markdown's own markup kept, its text escaped.
expect Html.markdown("**hi** <b>").to_str() == "<p><strong>hi</strong> &lt;b&gt;</p>\n"
expect Html.doctype.to_str() == "<!doctype html>\n<meta charset=utf-8>\n"
expect Html.style("p{x:y}\n").to_str() == "<style>\np{x:y}\n</style>\n"
```

### `app/Message.roc`

```
## **A MESSAGE**: who wrote it, when, and what (its payload), with the id
## its conversation gives it. Immutable: an edit is a new message. A message
## knows nothing of who may write where; that is the conversation's.
##
## There is no way to build a numbered message here: only
## `Conversation.append` gives a payload its id, so a message's id is always
## its place in its conversation.
import Author
import Timestamp
import Topic

Message :: [].{

	## **WHAT A MESSAGE IS BEFORE IT HAS AN ID**: who wrote it, when, and the
	## markdown, exactly as written.
	Payload : {
		author : Author,
		time : Timestamp,
		markdown : Str,
	}

	## **A MESSAGE'S ID**: its number in its conversation, counting from 1,
	## so a conversation's order is its ids' order. At most U16's highest,
	## 65,535: a conversation that long is archived, never grown.
	Id :: U16.{

		## The first message's id.
		first : Message.Id
		first = Message.Id.(1)

		## The id after this one, unless this is the last a conversation
		## holds.
		next : Message.Id -> Try(Message.Id, [Full])
		next = |Message.Id.(n)| if (n == U16.highest) Err(Full) else Ok(Message.Id.(n + 1))

		## The number, as a page's anchors and a refusal write it.
		to_str : Message.Id -> Str
		to_str = |Message.Id.(n)| n.to_str()

		is_eq : _
	}

	## **THE ONE NAME OF A MESSAGE**, `MSG_<topic>_<n>`, as a transcript's
	## id line and a page's link write it.
	reference : Topic, Message.Id -> Str
	reference = |topic, id| "MSG_${topic.to_str()}_${id.to_str()}"
}

# ── tests
plans : Topic
plans = Topic.from_str("plans") ?? crash "Message's tests: a topic's name"

expect Message.Id.first.to_str() == "1"
expect Message.Id.first.next().map_ok(Message.Id.to_str) == Ok("2")
expect Message.reference(plans, Message.Id.first) == "MSG_plans_1"
expect Message.Id.first.next().map_ok(|id| Message.reference(plans, id)) == Ok("MSG_plans_2")
# The last id at, under and over the highest.
expect Message.Id.(65534).next().map_ok(Message.Id.to_str) == Ok("65535")
expect Message.Id.(65535).next() == Err(Full)
```

### `app/Page.roc`

```
## **THE PAGES**: a conversation's, and the one that says why there is
## none. Every page is the same skeleton (the doctype, its title, the style,
## then its body); the page carries structure and class names, and only
## enough style to read, so a client can style the rest.
import Conversation
import Html
import Message
import Topic

Page :: [].{

	## **A CONVERSATION'S PAGE**: the topic, then each message under its
	## author and time, with its reference (`Message.reference`) as a link to
	## itself.
	conversation : Conversation -> Html
	conversation = |c| {
		topic = c.topic()
		heading = Html.tag({
			name: H1,
			attrs: [],
			inner: Html.text(topic.to_str()),
		})
		messages =
			if (c.messages().is_empty())
				Html.join([
					Html.tag({
						name: P,
						attrs: [Class("empty")],
						inner: Html.text("No messages yet."),
					}),
					newline,
				])
			else
				Html.join(c.messages().map(|m| message({ topic, message: m })))
		whole({
			title: topic.to_str(),
			body: Html.join([
				heading,
				newline,
				messages,
			]),
		})
	}

	## **THE PAGE FOR A REFUSED TRANSCRIPT**, saying why in `why`'s words.
	refused : Str -> Html
	refused = |why|
		whole({
			title: "Not a transcript",
			body: Html.tag({
				name: P,
				attrs: [],
				inner: Html.text("Not a transcript: ${why}."),
			}),
		})
}

## One message: its header, then its markdown rendered.
message : { topic : Topic, message : { id : Message.Id, payload : Message.Payload } } -> Html
message = |{ topic, message: { id, payload } }| {
	anchor = "msg-${id.to_str()}"
	header = Html.join([
		Html.tag({
			name: Span,
			attrs: [Class("author")],
			inner: Html.text(payload.author.to_str()),
		}),
		space,
		Html.tag({
			name: Time,
			attrs: [Datetime(payload.time)],
			inner: Html.text(payload.time.to_str()),
		}),
		space,
		Html.tag({
			name: A,
			attrs: [Class("ref"), Href("#${anchor}")],
			inner: Html.text(Message.reference(topic, id)),
		}),
	])
	article = Html.tag({
		name: Article,
		attrs: [Class("message"), Id(anchor)],
		inner: Html.join([
			Html.tag({
				name: Header,
				attrs: [],
				inner: header,
			}),
			newline,
			Html.tag({
				name: Div,
				attrs: [Class("body")],
				inner: Html.markdown(payload.markdown),
			}),
		]),
	})
	Html.join([article, newline])
}

## **THE SKELETON EVERY PAGE SHARES**: the doctype and charset, `title` as
## its title, the style, then `body`.
whole : { title : Str, body : Html } -> Html
whole = |{ title, body }|
	Html.join([
		Html.doctype,
		Html.tag({
			name: Title,
			attrs: [],
			inner: Html.text(title),
		}),
		newline,
		Html.style(style),
		body,
	])

newline : Html
newline = Html.text("\n")

space : Html
space = Html.text(" ")

## Only enough style to read; a client styles the rest.
style : Str
style =
	\\body{font:16px/1.4 system-ui,sans-serif;max-width:46rem;margin:2rem auto;padding:0 1rem}
	\\.message{border-top:1px solid #ccc;padding:.5rem 0}
	\\.author{font-weight:600}
	\\time,.ref{color:#777;font-size:.85em}
	\\.ref{float:right}
	\\

# ── tests
expect
	Page.refused("it <is> not UTF-8").to_str()
		== "<!doctype html>\n<meta charset=utf-8>\n<title>Not a transcript</title>\n<style>\n${style}</style>\n<p>Not a transcript: it &lt;is&gt; not UTF-8.</p>"
```

### `app/PageSpec.roc`

```
## **PAGE'S TESTS**: a conversation's page, byte for byte.
import Conversation
import Page
import Sample

PageSpec :: [].{}

## What every page opens with, titled `title` (already escaped).
head : Str -> Str
head = |title|
	"<!doctype html>\n<meta charset=utf-8>\n<title>${title}</title>\n<style>\nbody{font:16px/1.4 system-ui,sans-serif;max-width:46rem;margin:2rem auto;padding:0 1rem}\n.message{border-top:1px solid #ccc;padding:.5rem 0}\n.author{font-weight:600}\ntime,.ref{color:#777;font-size:.85em}\n.ref{float:right}\n</style>\n"

# No messages: the page says so, and only then.
expect Page.conversation(Conversation.empty(Sample.plans)).to_str() == "${head("plans")}<h1>plans</h1>\n<p class=\"empty\">No messages yet.</p>\n"
expect
	Page.conversation(Sample.two).to_str()
		== "${head("plans")}<h1>plans</h1>\n<article class=\"message\" id=\"msg-1\"><header><span class=\"author\">Steve</span> <time datetime=\"2026-11-02T19:11:32Z\">2026-11-02T19:11:32Z</time> <a class=\"ref\" href=\"#msg-1\">MSG_plans_1</a></header>\n<div class=\"body\"><p>Hello</p>\n</div></article>\n<article class=\"message\" id=\"msg-2\"><header><span class=\"author\">CC</span> <time datetime=\"2026-11-02T19:12:28Z\">2026-11-02T19:12:28Z</time> <a class=\"ref\" href=\"#msg-2\">MSG_plans_2</a></header>\n<div class=\"body\"><p>Hi!</p>\n<ul>\n<li>one</li>\n<li>two</li>\n</ul>\n</div></article>\n"
# A name holding markup is text on the page; the markdown's markup is kept.
expect
	Page.conversation(
		Sample.conversation(
			Sample.plans,
			[
				Sample.payload({
					author: "<Eve>",
					time: "2026-11-02T19:11:32Z",
					markdown: "**hi** <b>",
				}),
			],
		),
	).to_str()
		== "${head("plans")}<h1>plans</h1>\n<article class=\"message\" id=\"msg-1\"><header><span class=\"author\">&lt;Eve&gt;</span> <time datetime=\"2026-11-02T19:11:32Z\">2026-11-02T19:11:32Z</time> <a class=\"ref\" href=\"#msg-1\">MSG_plans_1</a></header>\n<div class=\"body\"><p><strong>hi</strong> &lt;b&gt;</p>\n</div></article>\n"
```

### `app/Sample.roc`

```
## **SAMPLES FOR THE SPECS**: the topics, payloads and conversation the
## `*Spec.roc` modules share, so each test reads as what it checks. Only a
## Spec imports it; no production module does.
import Author
import Conversation
import Message
import Timestamp
import Topic

Sample :: [].{

	## The topic the samples are written under.
	plans : Topic
	plans = Topic.from_str("plans") ?? crash "Sample.plans: a topic's name"

	## Another topic, whose transcript is not `plans`'s.
	other : Topic
	other = Topic.from_str("other") ?? crash "Sample.other: a topic's name"

	## A payload from its parts' text, each a test's own and accepted.
	payload : {
		author : Str,
		time : Str,
		markdown : Str,
	} -> Message.Payload
	payload = |
		{
			author,
			time,
			markdown,
		},
	|
		{
			author: Author.from_str(author) ?? crash "Sample.payload: a test's author is a name",
			time: Timestamp.from_str(time) ?? crash "Sample.payload: a test's time is a time",
			markdown,
		}

	## Steve's hello.
	hello : Message.Payload
	hello = Sample.payload({
		author: "Steve",
		time: "2026-11-02T19:11:32Z",
		markdown: "Hello",
	})

	## CC's reply, a minute later, with a list in its markdown.
	reply : Message.Payload
	reply = Sample.payload({
		author: "CC",
		time: "2026-11-02T19:12:28Z",
		markdown: "Hi!\n\n- one\n- two",
	})

	## `topic`'s conversation of `payloads`, appended in order; a test's
	## conversation is never full.
	conversation : Topic, List(Message.Payload) -> Conversation
	conversation = |topic, payloads|
		payloads.fold(
			Conversation.empty(topic),
			|c, p| c.append(p) ?? crash "Sample.conversation: a test's conversation is not full",
		)

	## `plans`'s hello and reply.
	two : Conversation
	two = Sample.conversation(Sample.plans, [Sample.hello, Sample.reply])

	## **A CONVERSATION ONE MESSAGE SHORT OF FULL**: 65,534 of Steve's hello.
	## A function, not a constant, so the work runs with the test, never in
	## `roc check`'s compile-time evaluation.
	almost_full : {} -> Conversation
	almost_full = |{}| filled({ so_far: Conversation.empty(Sample.plans), count: 65534 })

	## The first message's id.
	first : Message.Id
	first = Message.Id.first

	## The second message's id.
	second : Message.Id
	second = Message.Id.first.next() ?? crash "Sample.second: the first id has a next"
}

## `so_far` with `count` more of Steve's hello.
filled : { so_far : Conversation, count : U64 } -> Conversation
filled = |{ so_far, count }|
	if (count == 0)
		so_far
	else
		filled({
			so_far: so_far.append(Sample.hello) ?? crash "Sample.filled: the conversation has room",
			count: count - 1,
		})
```

### `app/Separator.roc`

```
## **THE SEPARATOR, AND A MESSAGE THAT CAN'T FORGE ONE**: a transcript
## opens each message with the line `-------------`. A markdown line that is
## the separator, after any backslashes, is written with one backslash
## more, and read back with one fewer, so no message's markdown is ever a
## separator on disk, and every markdown comes back exactly as written.
Separator :: [].{

	## The line that opens each message.
	line : Str
	line = "-------------"

	## `markdown` as the transcript writes it: no line of it the separator.
	escape : Str -> Str
	escape = |markdown| Str.join_with(
		markdown.split_on("\n").map(|l| if (is_separator_like(l)) "\\${l}" else l),
		"\n",
	)

	## The markdown a transcript holds, as it was written.
	unescape : Str -> Str
	unescape = |written| Str.join_with(
		written.split_on("\n").map(|l| if (l.starts_with("\\") and is_separator_like(l)) l.drop_prefix("\\") else l),
		"\n",
	)
}

## Is `l` the separator after some backslashes?
is_separator_like : Str -> Bool
is_separator_like = |l| l.ends_with(Separator.line) and l.drop_suffix(Separator.line).to_utf8().all(|b| b == '\\')

# ── tests
expect is_separator_like("-------------")
expect is_separator_like("\\-------------")
expect is_separator_like("\\\\-------------")
expect !is_separator_like("a-------------")
expect !is_separator_like("-------------x")
expect !is_separator_like("\\x")
expect !is_separator_like("------------")
expect !is_separator_like("\\------------")
expect Separator.escape("a\n-------------\n\\-------------\nb") == "a\n\\-------------\n\\\\-------------\nb"
expect Separator.unescape("a\n\\-------------\n\\\\-------------\nb") == "a\n-------------\n\\-------------\nb"
# A lone backslash, or one before a near miss, is no escape.
expect Separator.unescape("\\\n\\------------") == "\\\n\\------------"
# Escaping, then unescaping, gives the markdown back, separators and all.
expect
	[
		"",
		"plain",
		"-------------",
		"\\-------------\n\\\\-------------",
		"a\n-------------\nMSG_x_2\nfrom: Steve",
	].all(|md| Separator.unescape(Separator.escape(md)) == md)
# No escaped line is the separator.
expect !Separator.escape("-------------\nx\n-------------").split_on("\n").any(|l| l == Separator.line)
```

### `app/Specs.roc`

```
## **THE SPECS' ROOT**: every `*Spec.roc`, imported so one `roc test` runs
## them all (`roc test app/Specs.roc --main=app/main.roc`, which the gate
## runs beside `roc test app/main.roc`). A Spec left out of this list never
## runs, and the gate's floor then fails.
import ConversationSpec
import PageSpec
import TranscriptSpec

Specs :: [].{}
```

### `app/Timestamp.roc`

```
## **A TIMESTAMP**: when a message was written, as ISO 8601 in UTC, in
## exactly one form, `YYYY-MM-DDTHH:MM:SSZ`, so two times compare as text
## and a transcript reads the same everywhere. Opaque, so `from_str` is the
## only way in, and every one names a second some calendar and clock show.
import Ascii

Timestamp :: Str.{

	## The time `text` names, or why it is refused: not the form, or a
	## month, day, hour, minute or second no calendar or clock shows (a
	## 31st of April, a 29th of February outside a leap year, a 24th hour).
	from_str : Str -> Try(Timestamp, [WrongShape, OutOfRange])
	from_str = |text|
		match text.to_utf8() {
			[
				y1,
				y2,
				y3,
				y4,
				'-',
				m1,
				m2,
				'-',
				d1,
				d2,
				'T',
				h1,
				h2,
				':',
				n1,
				n2,
				':',
				s1,
				s2,
				'Z',
			] if [
				y1,
				y2,
				y3,
				y4,
				m1,
				m2,
				d1,
				d2,
				h1,
				h2,
				n1,
				n2,
				s1,
				s2,
			].all(Ascii.is_digit) => {
				year = number([y1, y2]) * 100 + number([y3, y4])
				month = number([m1, m2])
				day = number([d1, d2])
				in_calendar = month >= 1 and month <= 12 and day >= 1 and day <= days_in({ year, month })
				on_clock = number([h1, h2]) <= 23 and number([n1, n2]) <= 59 and number([s1, s2]) <= 59
				if (in_calendar and on_clock) Ok(Timestamp.(text)) else Err(OutOfRange)
			}
			_ => Err(WrongShape)
		}

	## The time as written.
	to_str : Timestamp -> Str
	to_str = |Timestamp.(text)| text

	is_eq : _
}

## The number the digits write, most significant first.
number : List(U8) -> U64
number = |digits| digits.fold(0, |n, d| n * 10 + (d - '0').to_u64())

## How many days `month` (1 to 12) has in `year`, by the Gregorian rule.
days_in : { year : U64, month : U64 } -> U64
days_in = |{ year, month }|
	match month {
		2 => if (is_leap(year)) 29 else 28
		4 | 6 | 9 | 11 => 30
		_ => 31
	}

## Every fourth year, but not every hundredth, unless every four-hundredth.
is_leap : U64 -> Bool
is_leap = |year| year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

# ── tests
## The text of the time `text` names, if it is accepted.
ok : Str -> Try(Str, [WrongShape, OutOfRange])
ok = |text| Timestamp.from_str(text).map_ok(Timestamp.to_str)

expect ok("2026-11-02T19:11:32Z") == Ok("2026-11-02T19:11:32Z")
expect Timestamp.from_str("") == Err(WrongShape)
expect Timestamp.from_str("2026-11-02T19:11:32") == Err(WrongShape)
expect Timestamp.from_str("2026-11-02T19:11:32z") == Err(WrongShape)
expect Timestamp.from_str("2026-11-02 19:11:32Z") == Err(WrongShape)
expect Timestamp.from_str("2026-11-02T19:11:32.5Z") == Err(WrongShape)
expect Timestamp.from_str("2026-11-02T19:11:32+00:00") == Err(WrongShape)
expect Timestamp.from_str("2026-1-02T19:11:32Z") == Err(WrongShape)
expect Timestamp.from_str("2026-11-02T19:11:3xZ") == Err(WrongShape)
expect Timestamp.from_str("2026-11-02T19:11:32Z\n") == Err(WrongShape)
expect Timestamp.from_str("２026-11-02T19:11:32Z") == Err(WrongShape)
expect Timestamp.from_str("2026/11-02T19:11:32Z") == Err(WrongShape)
# A digit's neighbours, in a digit's place.
expect Timestamp.from_str("202/-11-02T19:11:32Z") == Err(WrongShape)
expect Timestamp.from_str("202:-11-02T19:11:32Z") == Err(WrongShape)
# Each field at, and just past, each end of its range.
expect Timestamp.from_str("2026-00-02T19:11:32Z") == Err(OutOfRange)
expect ok("2026-01-02T19:11:32Z") == Ok("2026-01-02T19:11:32Z")
expect ok("2026-12-02T19:11:32Z") == Ok("2026-12-02T19:11:32Z")
expect Timestamp.from_str("2026-13-02T19:11:32Z") == Err(OutOfRange)
expect Timestamp.from_str("2026-11-00T19:11:32Z") == Err(OutOfRange)
expect ok("2026-11-01T19:11:32Z") == Ok("2026-11-01T19:11:32Z")
expect ok("2026-11-02T00:00:00Z") == Ok("2026-11-02T00:00:00Z")
expect ok("2026-11-02T23:59:59Z") == Ok("2026-11-02T23:59:59Z")
expect Timestamp.from_str("2026-11-02T24:11:32Z") == Err(OutOfRange)
expect Timestamp.from_str("2026-11-02T19:60:32Z") == Err(OutOfRange)
expect Timestamp.from_str("2026-11-02T19:11:60Z") == Err(OutOfRange)
expect ok("0000-01-01T00:00:00Z") == Ok("0000-01-01T00:00:00Z")
expect ok("9999-12-31T23:59:59Z") == Ok("9999-12-31T23:59:59Z")
expect Timestamp.from_str("2026-99-99T99:99:99Z") == Err(OutOfRange)
# Each month's last day, and the day after it.
expect ok("2026-01-31T19:11:32Z") == Ok("2026-01-31T19:11:32Z")
expect Timestamp.from_str("2026-01-32T19:11:32Z") == Err(OutOfRange)
expect ok("2026-04-30T19:11:32Z") == Ok("2026-04-30T19:11:32Z")
expect Timestamp.from_str("2026-04-31T19:11:32Z") == Err(OutOfRange)
expect Timestamp.from_str("2026-06-31T19:11:32Z") == Err(OutOfRange)
expect Timestamp.from_str("2026-09-31T19:11:32Z") == Err(OutOfRange)
expect ok("2026-11-30T19:11:32Z") == Ok("2026-11-30T19:11:32Z")
expect Timestamp.from_str("2026-11-31T19:11:32Z") == Err(OutOfRange)
expect ok("2026-12-31T19:11:32Z") == Ok("2026-12-31T19:11:32Z")
expect Timestamp.from_str("2026-12-32T19:11:32Z") == Err(OutOfRange)
# February: 28 days, 29 in a leap year, by all three of the rule's parts.
expect ok("2026-02-28T19:11:32Z") == Ok("2026-02-28T19:11:32Z")
expect Timestamp.from_str("2026-02-29T19:11:32Z") == Err(OutOfRange)
expect ok("2024-02-29T19:11:32Z") == Ok("2024-02-29T19:11:32Z")
expect Timestamp.from_str("2024-02-30T19:11:32Z") == Err(OutOfRange)
expect Timestamp.from_str("1900-02-29T19:11:32Z") == Err(OutOfRange)
expect ok("2000-02-29T19:11:32Z") == Ok("2000-02-29T19:11:32Z")
expect is_leap(2024) and is_leap(2000) and is_leap(0)
expect !is_leap(2026) and !is_leap(1900) and !is_leap(2100)
```

### `app/Topic.roc`

```
## **A TOPIC**: a conversation's name, which becomes a file name and a URL,
## so it is strictly named: ASCII letters, digits and `-`, starting with a
## letter, at most `longest` bytes. Opaque, so `from_str` is the only way in;
## no space, CR or LF ever reaches a path, a URL or a transcript's id line.
import Ascii

Topic :: Str.{

	## The topic named `name`, or the first reason, in this order, it is
	## refused.
	from_str : Str -> Try(Topic, [Empty, StartsWithNonLetter, TooLong, ForbiddenByte])
	from_str = |name| {
		bytes = name.to_utf8()
		match bytes {
			[] => Err(Empty)
			[first, ..] if !Ascii.is_letter(first) => Err(StartsWithNonLetter)
			_ if bytes.len() > Topic.longest => Err(TooLong)
			_ if !bytes.all(is_allowed) => Err(ForbiddenByte)
			_ => Ok(Topic.(name))
		}
	}

	## The longest name, in bytes; every byte is ASCII, so in characters too.
	longest : U64
	longest = 60

	## The name, as a file name and a URL take it.
	to_str : Topic -> Str
	to_str = |Topic.(name)| name

	is_eq : _
}

is_allowed : U8 -> Bool
is_allowed = |b| Ascii.is_letter(b) or Ascii.is_digit(b) or b == '-'

# ── tests
expect Topic.from_str("") == Err(Empty)
expect Topic.from_str(" ") == Err(StartsWithNonLetter)
expect Topic.from_str("\t") == Err(StartsWithNonLetter)
expect Topic.from_str("\n") == Err(StartsWithNonLetter)
expect Topic.from_str("\r") == Err(StartsWithNonLetter)
expect Topic.from_str("1plans") == Err(StartsWithNonLetter)
expect Topic.from_str("-plans") == Err(StartsWithNonLetter)
# The bytes beside the letters' ranges, first.
expect Topic.from_str("@a") == Err(StartsWithNonLetter)
expect Topic.from_str("[a") == Err(StartsWithNonLetter)
expect Topic.from_str("`a") == Err(StartsWithNonLetter)
expect Topic.from_str("{a") == Err(StartsWithNonLetter)
# The bytes beside every allowed range, after the first.
expect Topic.from_str("aAzZ09-").map_ok(Topic.to_str) == Ok("aAzZ09-")
expect Topic.from_str("a/") == Err(ForbiddenByte)
expect Topic.from_str("a:") == Err(ForbiddenByte)
expect Topic.from_str("a@") == Err(ForbiddenByte)
expect Topic.from_str("a[") == Err(ForbiddenByte)
expect Topic.from_str("a`") == Err(ForbiddenByte)
expect Topic.from_str("a{") == Err(ForbiddenByte)
expect Topic.from_str("a,") == Err(ForbiddenByte)
expect Topic.from_str("a.") == Err(ForbiddenByte)
expect Topic.from_str("plans\nnext") == Err(ForbiddenByte)
expect Topic.from_str("plans\r") == Err(ForbiddenByte)
expect Topic.from_str("plans ") == Err(ForbiddenByte)
expect Topic.from_str("plans_2") == Err(ForbiddenByte)
expect Topic.from_str("café") == Err(ForbiddenByte)
# The length at, under and over the longest.
expect Topic.from_str("a".repeat(61)) == Err(TooLong)
expect Topic.from_str("a".repeat(60)).map_ok(Topic.to_str) == Ok("a".repeat(60))
expect Topic.from_str("a".repeat(59)).map_ok(Topic.to_str) == Ok("a".repeat(59))
expect Topic.longest == 60
# The order of refusals: the first byte, then the length, then the bytes.
expect Topic.from_str("1${"a".repeat(60)}") == Err(StartsWithNonLetter)
expect Topic.from_str("a${"a".repeat(59)} ") == Err(TooLong)
expect Topic.from_str("a b") == Err(ForbiddenByte)
expect Topic.from_str("p").map_ok(Topic.to_str) == Ok("p")
expect Topic.from_str("Z").map_ok(Topic.to_str) == Ok("Z")
expect Topic.from_str("gopher-roc-2").map_ok(Topic.to_str) == Ok("gopher-roc-2")
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
## Each message opens with the separator, then its reference
## (`Message.reference`), its author, its time, an empty line, its markdown
## and an empty line. A conversation with no messages is an empty file. No
## message's markdown can forge the start of another (Separator).
import Author
import Conversation
import Message
import Separator
import Timestamp
import Topic

Transcript :: [].{

	## The transcript of the whole conversation.
	write : Conversation -> Str
	write = |conversation| {
		topic = conversation.topic()
		Str.join_with(conversation.messages().map(|m| record({ topic, message: m })), "")
	}

	## What `append` gives: the conversation grown by one, and the one
	## message's record.
	Appended : { conversation : Conversation, record : Str }

	## **ONE MESSAGE'S RECORD, FOR A STORE TO APPEND**: the conversation
	## with `payload` appended, and that message's record, so the file a
	## store grows a record at a time is `write` of the conversation.
	append : Conversation, Message.Payload -> Try(Transcript.Appended, [Full])
	append = |before, payload| {
		after = before.append(payload)?
		added = after.messages().last() ?? crash "Transcript.append: an append adds a message"
		Ok({ conversation: after, record: record({ topic: after.topic(), message: added }) })
	}

	## `topic`'s conversation, each message appended in turn, or the first
	## thing wrong with the transcript.
	read : Topic,
	Str -> Try(
		Conversation,
		[
			BadEnds,
			BadHead(Message.Id),
			Author(Message.Id, [Blank, ControlByte]),
			Time(Message.Id, [WrongShape, OutOfRange]),
			Full,
		],
	)
	read = |topic, text|
		if (text.is_empty())
			Ok(Conversation.empty(topic))
		else if (!text.starts_with("${separator}\n") or !text.ends_with("\n\n"))
			Err(BadEnds)
		else {
			records = text.drop_prefix("${separator}\n").drop_suffix("\n\n").split_on("\n\n${separator}\n")
			read_onto(Conversation.empty(topic), records)
		}
}

separator : Str
separator = Separator.line

## One message as the transcript writes it.
record : { topic : Topic, message : { id : Message.Id, payload : Message.Payload } } -> Str
record = |{ topic, message: { id, payload } }|
	"${separator}\n${Message.reference(topic, id)}\nfrom: ${payload.author.to_str()}\ndate: ${payload.time.to_str()}\n\n${Separator.escape(payload.markdown)}\n\n"

## `so_far` with each record appended in order, or the first record's fault.
read_onto : Conversation, List(Str) -> Try(Conversation, _)
read_onto = |so_far, records|
	match records {
		[] => Ok(so_far)
		[first, .. as rest] => read_onto(read_message(so_far, first)?, rest)
	}

## `c` with the message `written` appended, or why it can't be.
read_message : Conversation, Str -> Try(Conversation, _)
read_message = |c, written| {
	id = c.next_id()?
	reference = Message.reference(c.topic(), id)
	match written.split_on("\n") {
		[
			head,
			from_line,
			date_line,
			"",
			.. as body,
		] if head == reference and from_line.starts_with("from: ") and date_line.starts_with("date: ") => {
			name = from_line.drop_prefix("from: ")
			date = date_line.drop_prefix("date: ")
			author = Author.from_str(name).map_err(|why| Author(id, why))?
			time = Timestamp.from_str(date).map_err(|why| Time(id, why))?
			c.append({
				author,
				time,
				markdown: Separator.unescape(Str.join_with(body, "\n")),
			})
		}
		_ => Err(BadHead(id))
	}
}
```

### `app/TranscriptSpec.roc`

```
## **TRANSCRIPT'S TESTS**: the file, written and read, byte for byte, and
## each way a transcript is refused, at the first message and the second.
import Conversation
import Sample
import Transcript

TranscriptSpec :: [].{}

## **A RECORD'S LINES, AS A TEST WRITES THEM**: its head, its `from:` and
## `date:` lines, and `gap`, the empty line after them, or not.
Lines : {
	head : Str,
	from : Str,
	date : Str,
	gap : Str,
}

## A record with its lines as given, saying "hi".
record : Lines -> Str
record = |
	{
		head,
		from,
		date,
		gap,
	},
| "-------------\n${head}\n${from}\n${date}\n${gap}hi\n\n"

## Message 1's lines, written well.
first : Lines
first = {
	head: "MSG_plans_1",
	from: "from: Steve",
	date: "date: 2026-11-02T19:11:32Z",
	gap: "\n",
}

## Message 2's lines, written well.
second : Lines
second = {
	head: "MSG_plans_2",
	from: "from: CC",
	date: "date: 2026-11-02T19:12:28Z",
	gap: "\n",
}

## The transcript holding only message 1 as `lines` write it.
one_with = |lines| Transcript.read(Sample.plans, record(lines))

## The transcript holding message 1, written well, then message 2 as
## `lines` write it.
two_with = |lines| Transcript.read(Sample.plans, "${record(first)}${record(lines)}")

## Read, then written again: the text itself, when it is accepted.
again = |text| Transcript.read(Sample.plans, text).map_ok(Transcript.write)

# Written exactly, both ways.
expect Transcript.write(Sample.two) == "-------------\nMSG_plans_1\nfrom: Steve\ndate: 2026-11-02T19:11:32Z\n\nHello\n\n-------------\nMSG_plans_2\nfrom: CC\ndate: 2026-11-02T19:12:28Z\n\nHi!\n\n- one\n- two\n\n"
expect Transcript.read(Sample.plans, Transcript.write(Sample.two)) == Ok(Sample.two)
# No messages: an empty file, both ways.
expect Transcript.write(Conversation.empty(Sample.plans)) == ""
expect Transcript.read(Sample.plans, "") == Ok(Conversation.empty(Sample.plans))
# A store's one record: what `write` adds for the appended message.
expect
	Transcript.append(Conversation.empty(Sample.plans), Sample.hello)
		== Ok({
			conversation: Sample.conversation(Sample.plans, [Sample.hello]),
			record: "-------------\nMSG_plans_1\nfrom: Steve\ndate: 2026-11-02T19:11:32Z\n\nHello\n\n",
		})
expect
	Transcript.append(
		Sample.conversation(Sample.plans, [Sample.hello]),
		Sample.reply,
	).map_ok(|{ conversation, record: added }| (conversation, added))
		== Ok((
			Sample.two,
			"-------------\nMSG_plans_2\nfrom: CC\ndate: 2026-11-02T19:12:28Z\n\nHi!\n\n- one\n- two\n\n",
		))
# The start and the end, each wrong alone.
expect Transcript.read(Sample.plans, "\n") == Err(BadEnds)
expect Transcript.read(
	Sample.plans,
	"MSG_plans_1\nfrom: Steve\ndate: 2026-11-02T19:11:32Z\n\nhi\n\n",
) == Err(BadEnds)
expect Transcript.read(
	Sample.plans,
	"-------------\nMSG_plans_1\nfrom: Steve\ndate: 2026-11-02T19:11:32Z\n\nhi\n",
) == Err(BadEnds)
expect Transcript.read(
	Sample.plans,
	"-------------\nMSG_plans_1\nfrom: Steve\ndate: 2026-11-02T19:11:32Z\n\nhi",
) == Err(BadEnds)
# Each line of message 1's head, bad alone, beside the good one.
expect again(record(first)) == Ok(record(first))
expect one_with({ ..first, head: "MSG_plans_2" }) == Err(BadHead(Sample.first))
expect one_with({ ..first, head: "MSG_other_1" }) == Err(BadHead(Sample.first))
expect one_with({ ..first, from: "frm: Steve" }) == Err(BadHead(Sample.first))
expect one_with({ ..first, date: "dt: 2026-11-02T19:11:32Z" }) == Err(BadHead(Sample.first))
expect one_with({ ..first, gap: "" }) == Err(BadHead(Sample.first))
expect one_with({ ..first, from: "from: " }) == Err(Author(Sample.first, Blank))
expect one_with({ ..first, from: "from:  " }) == Err(Author(Sample.first, Blank))
expect one_with({ ..first, from: "from: Steve\r" }) == Err(Author(Sample.first, ControlByte))
expect one_with({ ..first, date: "date: 2026-11-02" }) == Err(Time(Sample.first, WrongShape))
expect one_with({
	..first,
	date: "date: 2026-13-02T19:11:32Z",
}) == Err(Time(Sample.first, OutOfRange))
# The same at message 2, after a good message 1.
expect again("${record(first)}${record(second)}") == Ok("${record(first)}${record(second)}")
expect two_with({ ..second, head: "MSG_plans_1" }) == Err(BadHead(Sample.second))
expect two_with({ ..second, head: "MSG_plans_3" }) == Err(BadHead(Sample.second))
expect two_with({ ..second, from: "frm: CC" }) == Err(BadHead(Sample.second))
expect two_with({ ..second, date: "dt: 2026-11-02T19:12:28Z" }) == Err(BadHead(Sample.second))
expect two_with({ ..second, gap: "" }) == Err(BadHead(Sample.second))
expect two_with({ ..second, from: "from: " }) == Err(Author(Sample.second, Blank))
expect two_with({ ..second, from: "from: C\u(0)C" }) == Err(Author(Sample.second, ControlByte))
expect two_with({
	..second,
	date: "date: 2026-11-02T19:12:28",
}) == Err(Time(Sample.second, WrongShape))
expect two_with({
	..second,
	date: "date: 2026-02-29T19:12:28Z",
}) == Err(Time(Sample.second, OutOfRange))
# Another topic's transcript is refused by its references.
expect Transcript.read(Sample.other, Transcript.write(Sample.two)) == Err(BadHead(Sample.first))
# A body that holds the separator, or a backslash before it, is written
# with one backslash more, and comes back whole.
forged : Conversation
forged = Sample.conversation(
	Sample.plans,
	[
		Sample.payload({
			author: "Mallory",
			time: "2026-11-02T19:11:32Z",
			markdown: "a\n-------------\nMSG_plans_2\nfrom: Steve",
		}),
		Sample.payload({
			author: "Mallory",
			time: "2026-11-02T19:12:28Z",
			markdown: "\\-------------\n\\\\-------------",
		}),
	],
)
expect Transcript.write(forged) == "-------------\nMSG_plans_1\nfrom: Mallory\ndate: 2026-11-02T19:11:32Z\n\na\n\\-------------\nMSG_plans_2\nfrom: Steve\n\n-------------\nMSG_plans_2\nfrom: Mallory\ndate: 2026-11-02T19:12:28Z\n\n\\\\-------------\n\\\\\\-------------\n\n"
expect Transcript.read(Sample.plans, Transcript.write(forged)) == Ok(forged)
# Near the separator but not it: written as is, read back unchanged.
near : Conversation
near = Sample.conversation(
	Sample.plans,
	[
		Sample.payload({
			author: "Steve",
			time: "2026-11-02T19:11:32Z",
			markdown: "a-------------\n-------------x\n\\x\n------------",
		}),
	],
)
expect Transcript.write(near) == "-------------\nMSG_plans_1\nfrom: Steve\ndate: 2026-11-02T19:11:32Z\n\na-------------\n-------------x\n\\x\n------------\n\n"
expect Transcript.read(Sample.plans, Transcript.write(near)) == Ok(near)
# The most messages a store's `append` takes, at and over: the 65,535th
# message's record, then none. The reader asks the same `next_id`.
expect {
	almost = Sample.almost_full({})
	full = almost.append(Sample.reply) ?? crash "TranscriptSpec: the 65,535th message fits"
	last = Transcript.append(almost, Sample.reply).map_ok(|appended| appended.record)
	wanted = "-------------\nMSG_plans_65535\nfrom: CC\ndate: 2026-11-02T19:12:28Z\n\nHi!\n\n- one\n- two\n\n"
	last == Ok(wanted) and Transcript.append(full, Sample.hello) == Err(Full)
}
```

### `app/main.roc`

```
## **THE DEMO**: a topic's name and its transcript in, its page out. The
## host (host/main.zig) reads the file and writes the page; everything
## else is the pure core. The door: the host's bytes become a Conversation
## or a refusal's tags here, and only here are the tags put into words.
app [page] {
	md: "../../roc-markdown/package/main.roc",
	pf: platform "../platform/main.roc",
}

import Conversation
import Message
import Page
import Topic
import Transcript

## The page for `topic`'s transcript, or a page saying what is wrong with it.
page : List(U8), List(U8) -> List(U8)
page = |topic, transcript| {
	answer =
		match conversation({ topic, transcript }) {
			Ok(c) => Page.conversation(c)
			Err(why) => Page.refused(words(why))
		}
	answer.to_str().to_utf8()
}

## The conversation the host's bytes hold, decoded at the door.
conversation : { topic : List(U8), transcript : List(U8) } -> Try(Conversation, _)
conversation = |{ topic, transcript }| {
	name = Str.from_utf8(topic) ? |_| TopicNotUtf8
	text = Str.from_utf8(transcript) ? |_| TranscriptNotUtf8
	checked = Topic.from_str(name) ? |why| Topic(why)
	Transcript.read(checked, text).map_err(|why| Transcript(why))
}

## **WHY A TRANSCRIPT IS REFUSED, IN WORDS**: the one place a refusal's
## tags become a sentence.
words : [
	TopicNotUtf8,
	TranscriptNotUtf8,
	Topic([Empty, StartsWithNonLetter, TooLong, ForbiddenByte]),
	Transcript(
		[
			BadEnds,
			BadHead(Message.Id),
			Author(Message.Id, [Blank, ControlByte]),
			Time(Message.Id, [WrongShape, OutOfRange]),
			Full,
		],
	),
] -> Str
words = |why|
	match why {
		TopicNotUtf8 => "its topic is not UTF-8"
		TranscriptNotUtf8 => "it is not UTF-8"
		Topic(Empty) => "its topic is empty"
		Topic(StartsWithNonLetter) => "its topic does not start with an ASCII letter"
		Topic(TooLong) => "its topic is longer than ${Topic.longest.to_str()} characters"
		Topic(ForbiddenByte) => "its topic holds more than ASCII letters, digits and -"
		Transcript(BadEnds) => "a transcript starts with the separator and ends with an empty line"
		Transcript(BadHead(id)) => "message ${id.to_str()} does not open with its reference, `from:`, `date:` and an empty line"
		Transcript(Author(id, Blank)) => "message ${id.to_str()} has no author"
		Transcript(Author(id, ControlByte)) => "message ${id.to_str()}'s author holds a control character"
		Transcript(Time(id, WrongShape)) => "message ${id.to_str()}'s date is not YYYY-MM-DDTHH:MM:SSZ"
		Transcript(Time(id, OutOfRange)) => "message ${id.to_str()}'s date is no time a calendar and clock show"
		Transcript(Full) => "it holds more messages than a conversation can"
	}

# ── tests
plans : Topic
plans = Topic.from_str("plans") ?? crash "main's tests: a topic's name"

expect conversation({ topic: "plans".to_utf8(), transcript: [] }) == Ok(Conversation.empty(plans))
expect conversation({ topic: [0xff], transcript: [] }) == Err(TopicNotUtf8)
expect conversation({ topic: "plans".to_utf8(), transcript: [0xff] }) == Err(TranscriptNotUtf8)
# Each refusal of the topic, and of the transcript, through the door.
expect conversation({ topic: "".to_utf8(), transcript: [] }) == Err(Topic(Empty))
expect conversation({ topic: "1a".to_utf8(), transcript: [] }) == Err(Topic(StartsWithNonLetter))
expect conversation({ topic: "a".repeat(61).to_utf8(), transcript: [] }) == Err(Topic(TooLong))
expect conversation({ topic: "a b".to_utf8(), transcript: [] }) == Err(Topic(ForbiddenByte))
expect conversation({
	topic: "plans".to_utf8(),
	transcript: "\n".to_utf8(),
}) == Err(Transcript(BadEnds))
# The order: the topic's bytes, the transcript's, then the topic's name.
expect conversation({ topic: [0xff], transcript: [0xff] }) == Err(TopicNotUtf8)
expect conversation({ topic: "".to_utf8(), transcript: [0xff] }) == Err(TranscriptNotUtf8)
expect conversation({ topic: "".to_utf8(), transcript: "\n".to_utf8() }) == Err(Topic(Empty))
# The page, through the host's bytes: a conversation's, or the refusal's.
expect page(
	"plans".to_utf8(),
	[],
) == Page.conversation(Conversation.empty(plans)).to_str().to_utf8()
expect page("<b>".to_utf8(), [0xff]) == Page.refused("it is not UTF-8").to_str().to_utf8()
# The one test of the wording: every refusal, in words.
expect {
	second = Message.Id.first.next() ?? crash "main's tests: the first id has a next"
	[
		TopicNotUtf8,
		TranscriptNotUtf8,
		Topic(Empty),
		Topic(StartsWithNonLetter),
		Topic(TooLong),
		Topic(ForbiddenByte),
		Transcript(BadEnds),
		Transcript(BadHead(second)),
		Transcript(Author(second, Blank)),
		Transcript(Author(second, ControlByte)),
		Transcript(Time(second, WrongShape)),
		Transcript(Time(second, OutOfRange)),
		Transcript(Full),
	].map(words)
		== [
			"its topic is not UTF-8",
			"it is not UTF-8",
			"its topic is empty",
			"its topic does not start with an ASCII letter",
			"its topic is longer than 60 characters",
			"its topic holds more than ASCII letters, digits and -",
			"a transcript starts with the separator and ends with an empty line",
			"message 2 does not open with its reference, `from:`, `date:` and an empty line",
			"message 2 has no author",
			"message 2's author holds a control character",
			"message 2's date is not YYYY-MM-DDTHH:MM:SSZ",
			"message 2's date is no time a calendar and clock show",
			"it holds more messages than a conversation can",
		]
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
///   zig build test                       roc test, from the app and from app/Specs.roc
///   zig build demo -- <topic> <file>     a transcript's page, to stdout
pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const roc = rocCompiler(b);

    const archive = b.addSystemCommand(&.{ roc, "build", "app/main.roc", "--target=x64musl", "--opt=dev" });
    archive.setCwd(b.path("."));
    for ([_][]const u8{ "app", "platform" }) |folder| rocInputs(b, archive, folder);
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

    const test_step = b.step("test", "roc test, from the app and from app/Specs.roc");
    const roots = [_][]const []const u8{
        &.{ roc, "test", "app/main.roc" },
        &.{ roc, "test", "app/Specs.roc", "--main=app/main.roc" },
    };
    for (roots) |argv| {
        const roc_test = b.addSystemCommand(argv);
        roc_test.setCwd(b.path("."));
        roc_test.has_side_effects = true;
        test_step.dependOn(&roc_test.step);
    }
}

/// **EVERY ROC MODULE IS AN INPUT, FOUND, NEVER LISTED**: each `.roc` in
/// `folder`, so a change to any module builds the archive again.
fn rocInputs(b: *std.Build, run: *std.Build.Step.Run, folder: []const u8) void {
    const io = b.graph.io;
    var dir = b.root.root_dir.handle.openDir(io, folder, .{ .iterate = true }) catch |e|
        std.process.fatal("the Roc: cannot open {s} ({t})", .{ folder, e });
    defer dir.close(io);
    var it = dir.iterate();
    while (it.next(io) catch |e| std.process.fatal("the Roc: cannot list {s} ({t})", .{ folder, e })) |entry| {
        if (entry.kind != .file or !std.mem.endsWith(u8, entry.name, ".roc")) continue;
        run.addFileInput(b.path(b.fmt("{s}/{s}", .{ folder, entry.name })));
    }
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

And the transcript stays readable with `cat`. A body line that looks like the separator gets a backslash on disk, so nobody can forge a message. In a code block, which shows every byte:

```
\-------------
```

That line was escaped on disk and came back whole, with no backslash.

-------------
MSG_gopher-roc_4
from: Steve
date: 2026-11-02T18:06:30Z

Nice. What does rendering cost us?

-------------
MSG_gopher-roc_5
from: LC
date: 2026-11-02T18:07:15Z

One call per message into roc-markdown, through `Html`:

```roc
Html.markdown(payload.markdown)
```

The page is structure and class names; a client styles it. 🎉

~~~~

