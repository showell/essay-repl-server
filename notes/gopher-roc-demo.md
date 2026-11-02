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
<div class="body"><p>And the transcript stays readable with <code>cat</code>. A body line that looks like the separator gets a backslash, so nobody can forge a message:</p>
<p>-------------</p>
<p>That line above was escaped on disk and came back whole.</p>
</div></article>
<article class="message" id="msg-4"><header><span class="author">Steve</span> <time datetime="2026-11-02T18:06:30Z">2026-11-02T18:06:30Z</time> <a class="ref" href="#msg-4">MSG_gopher-roc_4</a></header>
<div class="body"><p>Nice. What does rendering cost us?</p>
</div></article>
<article class="message" id="msg-5"><header><span class="author">LC</span> <time datetime="2026-11-02T18:07:15Z">2026-11-02T18:07:15Z</time> <a class="ref" href="#msg-5">MSG_gopher-roc_5</a></header>
<div class="body"><p>One call per message into roc-markdown:</p>
<pre><code class="language-roc">Md.render(m.markdown().to_utf8(), { uploads: |_| Bool.False })
</code></pre>
<p>The page is structure and class names; a client styles it. 🎉</p>
</div></article>

</div>

## The code

### `app/Author.roc`

```
## **AN AUTHOR**: who wrote a message, by their permanent name, exactly as
## they signed up (names are case-sensitive). Opaque, so `from_str` is the
## only way in: a name is never blank, and never holds a CR or an LF, which
## would end the transcript's `from:` line early.
Author :: Str.{

	## The author named `name`, unless it is blank or breaks a line.
	from_str : Str -> Try(Author, [Blank, LineBreak])
	from_str = |name|
		if (name.trim().is_empty())
			Err(Blank)
		else if (name.contains("\n") or name.contains("\r"))
			Err(LineBreak)
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
expect Author.from_str("Ste\nve") == Err(LineBreak)
expect Author.from_str("Steve\r") == Err(LineBreak)
expect Author.from_str("S").map_ok(Author.to_str) == Ok("S")
expect Author.from_str("Steve Howell").map_ok(Author.to_str) == Ok("Steve Howell")
expect Author.from_str(" Zoë\t").map_ok(Author.to_str) == Ok(" Zoë\t")
```

### `app/Conversation.roc`

```
## **A CONVERSATION**: a topic and its messages, in id order. It stands
## alone: no channel, no DM, no reader. Given its transcript, it renders as
## one page of HTML, each message's markdown by roc-markdown; the page
## carries structure and class names, and only enough style to read.
import md.Md
import Html
import Message
import Sample
import Topic
import Transcript

Conversation :: {
	topic : Topic,
	messages : List(Message),
}.{

	## The conversation a transcript holds, its topic named by its file.
	read : Topic, Str -> Try(Conversation, [Malformed(Str)])
	read = |
		topic,
		transcript,
	| Transcript.read(topic, transcript).map_ok(|messages| Conversation.({ topic, messages }))

	## Its topic.
	topic : Conversation -> Topic
	topic = |Conversation.(c)| c.topic

	## Its messages, oldest first.
	messages : Conversation -> List(Message)
	messages = |Conversation.(c)| c.messages

	is_eq : _

	## **THE PAGE**: the topic, then each message under its author and time,
	## with its reference (`MSG_<topic>_<n>`) as a link to itself.
	html : Conversation -> Html
	html = |Conversation.(c)|
		Html.page({
			title: c.topic.to_str(),
			body: Html.join([
				Html.element({
					name: "h1",
					attrs: [],
					inner: Html.text(c.topic.to_str()),
				}),
				Html.markup("\n"),
				if (c.messages.is_empty())
					Html.join([
						Html.element({
							name: "p",
							attrs: [Attr("class", "empty")],
							inner: Html.text("No messages yet."),
						}),
						Html.markup("\n"),
					])
				else
					Html.join(c.messages.map(|m| message_html(c.topic, m))),
			]),
		})
}

## One message: its header, then its markdown rendered.
message_html : Topic, Message -> Html
message_html = |topic, m| {
	n = m.id().to_str()
	time = m.time().to_str()
	rendered = Md.render(m.markdown().to_utf8(), { uploads: |_| Bool.False })
	body = Str.from_utf8(rendered) ?? crash "Conversation: roc-markdown renders UTF-8"
	header = Html.join([
		Html.element({
			name: "span",
			attrs: [Attr("class", "author")],
			inner: Html.text(m.author().to_str()),
		}),
		Html.markup(" "),
		Html.element({
			name: "time",
			attrs: [Attr("datetime", time)],
			inner: Html.text(time),
		}),
		Html.markup(" "),
		Html.element({
			name: "a",
			attrs: [Attr("class", "ref"), Attr("href", "#msg-${n}")],
			inner: Html.text("MSG_${topic.to_str()}_${n}"),
		}),
	])
	article = Html.element({
		name: "article",
		attrs: [Attr("class", "message"), Attr("id", "msg-${n}")],
		inner: Html.join([
			Html.element({
				name: "header",
				attrs: [],
				inner: header,
			}),
			Html.markup("\n"),
			Html.element({
				name: "div",
				attrs: [Attr("class", "body")],
				inner: Html.rendered(body),
			}),
		]),
	})
	Html.join([article, Html.markup("\n")])
}

# ── tests
expect
	message_html(
		Sample.plans,
		Sample.said({
			id: Sample.first,
			author: "Steve",
			markdown: "**hi**",
		}),
	).to_str()
		== "<article class=\"message\" id=\"msg-1\"><header><span class=\"author\">Steve</span> <time datetime=\"2026-11-02T19:11:32Z\">2026-11-02T19:11:32Z</time> <a class=\"ref\" href=\"#msg-1\">MSG_plans_1</a></header>\n<div class=\"body\"><p><strong>hi</strong></p>\n</div></article>\n"
# A name holding markup is text on the page.
expect
	Conversation.read(
		Sample.plans,
		Transcript.write(
			Sample.plans,
			[
				Sample.said({
					id: Sample.first,
					author: "<Eve>",
					markdown: "x",
				}),
			],
		),
	)
		.map_ok(|c| c.html().to_str().contains("<span class=\"author\">&lt;Eve&gt;</span>"))
		== Ok(Bool.True)
# No messages: the page says so, and only then.
expect
	Conversation.read(Sample.plans, "").map_ok(|c| c.html().to_str())
		== Ok(
			Html.page({
				title: "plans",
				body: Html.markup("<h1>plans</h1>\n<p class=\"empty\">No messages yet.</p>\n"),
			}).to_str(),
		)
expect Conversation.read(
	Sample.plans,
	Transcript.write(Sample.plans, Sample.two),
).map_ok(|c| c.html().to_str().contains("No messages yet.")) == Ok(Bool.False)
expect Conversation.read(
	Sample.plans,
	Transcript.write(Sample.plans, Sample.two),
).map_ok(|c| c.messages()) == Ok(Sample.two)
expect Conversation.read(
	Sample.plans,
	"\n",
).map_ok(Conversation.topic) == Err(Malformed("a transcript starts with the separator and ends with an empty line"))
```

### `app/Html.roc`

```
## **A PAGE IS AN `Html`, AND AN `Html` IS SAFE BY CONSTRUCTION**: opaque
## (`::`), so outside this module nothing makes one from a `Str`. The ways
## in: `text` (anything a person, an agent or a file supplied: a topic, a
## name, a time), `markup` (markup written in the code, a string literal,
## holding no `${...}`), `rendered` (roc-markdown's HTML for a message, the
## one HTML this chat does not write), `element` (a tag, its attributes
## escaped as they go in) and `page` (the skeleton every page shares).
## `to_str` is the one way out.
Html :: Str.{

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

	## **MARKUP WRITTEN IN THE CODE**: a string literal, never one built from
	## data (anything computed goes through `text` or `element`).
	markup : Str -> Html
	markup = |literal| Html.(literal)

	## **roc-markdown's HTML FOR A MESSAGE**, as is: the renderer's output and
	## nothing else.
	rendered : Str -> Html
	rendered = |html| Html.(html)

	## **AN ELEMENT**: `<name a="v">inner</name>`, each attribute's value
	## escaped as text and quoted, so no value is ever spliced into a tag.
	## Names are code: lowercase letters, digits and `-`.
	element : {
		name : Str,
		attrs : List([Attr(Str, Str)]),
		inner : Html,
	} -> Html
	element = |
		{
			name,
			attrs,
			inner,
		},
	| {
		open = Str.join_with(
			attrs.map(
				|Attr(attr, value)| {
					quoted = Html.text(value).to_str()
					" ${code_name(attr)}=\"${quoted}\""
				},
			),
			"",
		)
		tag = code_name(name)
		Html.("<${tag}${open}>${inner.to_str()}</${tag}>")
	}

	## The pieces, in order.
	join : List(Html) -> Html
	join = |pieces| Html.(Str.join_with(pieces.map(Html.to_str), ""))

	## **A WHOLE PAGE**: the doctype, the charset, `title` as its title, the
	## style every page shares, then `body`.
	page : { title : Str, body : Html } -> Html
	page = |{ title, body }|
		Html.join([
			Html.markup(
				\\<!doctype html>
				\\<meta charset=utf-8>
				\\
			),
			Html.element({
				name: "title",
				attrs: [],
				inner: Html.text(title),
			}),
			Html.markup("\n"),
			Html.markup(style),
			body,
		])

	## The page's text, once, for the host.
	to_str : Html -> Str
	to_str = |Html.(s)| s

	is_eq : _
}

## A tag's or an attribute's name, which the code writes: lowercase letters,
## digits and `-`, never data.
code_name : Str -> Str
code_name = |name|
	if (!name.is_empty() and name.to_utf8().all(|b| (b >= 'a' and b <= 'z') or (b >= '0' and b <= '9') or b == '-'))
		name
	else
		crash "Html.code_name: a tag or attribute name is code"

## Only enough style to read; a client styles the rest.
style : Str
style =
	\\<style>
	\\body{font:16px/1.4 system-ui,sans-serif;max-width:46rem;margin:2rem auto;padding:0 1rem}
	\\.message{border-top:1px solid #ccc;padding:.5rem 0}
	\\.author{font-weight:600}
	\\time,.ref{color:#777;font-size:.85em}
	\\.ref{float:right}
	\\</style>
	\\

# ── tests
expect Html.text("Bea <i>x</i> & \"co\" 'q'").to_str() == "Bea &lt;i&gt;x&lt;/i&gt; &amp; &quot;co&quot; &#39;q&#39;"
expect Html.text("&lt;").to_str() == "&amp;lt;"
expect Html.text("café 🎉").to_str() == "café 🎉"
# A value holding a quote and a script is text inside its attribute.
expect
	Html.element({
		name: "b",
		attrs: [Attr("data-name", "<script>\"")],
		inner: Html.text("<i>"),
	}).to_str()
		== "<b data-name=\"&lt;script&gt;&quot;\">&lt;i&gt;</b>"
expect
	Html.element({
		name: "time",
		attrs: [Attr("datetime", "1"), Attr("class", "x")],
		inner: Html.markup(""),
	}).to_str()
		== "<time datetime=\"1\" class=\"x\"></time>"
expect Html.join([
	Html.markup("<p>"),
	Html.text("a&b"),
	Html.markup("</p>"),
]).to_str() == "<p>a&amp;b</p>"
expect Html.page({
	title: "<T>",
	body: Html.markup("<p>hi</p>\n"),
}).to_str() == "<!doctype html>\n<meta charset=utf-8>\n<title>&lt;T&gt;</title>\n${style}<p>hi</p>\n"
expect code_name("h1") == "h1"
expect code_name("data-name") == "data-name"
```

### `app/Message.roc`

```
## **A MESSAGE**: who wrote it, when, and what, with the id its
## conversation gave it. Immutable: an edit is a new message. A message
## knows nothing of who may write where; that is the conversation's.
import Author
import Timestamp

Message :: {
	id : Message.Id,
	author : Author,
	time : Timestamp,
	markdown : Str,
}.{

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

		## The id as the transcript and the page write it.
		to_str : Message.Id -> Str
		to_str = |Message.Id.(n)| n.to_str()

		is_eq : _
	}

	## A message from its parts, each already checked by its own type.
	new : {
		id : Message.Id,
		author : Author,
		time : Timestamp,
		markdown : Str,
	} -> Message
	new = |m| Message.(m)

	## Its id in its conversation.
	id : Message -> Message.Id
	id = |Message.(m)| m.id

	## Who wrote it.
	author : Message -> Author
	author = |Message.(m)| m.author

	## When it was written.
	time : Message -> Timestamp
	time = |Message.(m)| m.time

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
```

### `app/Sample.roc`

```
## **SAMPLES FOR THE TESTS**: the messages, ids, topic and time the
## modules' `expect`s share, so each test reads as what it checks. It exists
## for the tests; nothing else calls it.
import Author
import Message
import Timestamp
import Topic

Sample :: [].{

	## A message from `author`, written at `time`.
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
		Message.new({
			id,
			author: Author.from_str(author) ?? crash "Sample.said: a test's author is a name",
			time: Sample.time,
			markdown,
		})

	## The time every sample message was written.
	time : Timestamp
	time = Timestamp.from_str("2026-11-02T19:11:32Z") ?? crash "Sample.time: a real time"

	## The topic the samples are written under.
	plans : Topic
	plans = Topic.from_str("plans") ?? crash "Sample.plans: a topic's name"

	## Another topic, whose transcript is not `plans`'s.
	other : Topic
	other = Topic.from_str("other") ?? crash "Sample.other: a topic's name"

	## The first message's id.
	first : Message.Id
	first = Message.Id.first

	## The second message's id.
	second : Message.Id
	second = Message.Id.first.next() ?? crash "Sample.second: the first id has a next"

	## Two messages, the second with a list in its markdown.
	two : List(Message)
	two = [
		Sample.said({
			id: Sample.first,
			author: "Steve",
			markdown: "Hello",
		}),
		Sample.said({
			id: Sample.second,
			author: "CC",
			markdown: "Hi!\n\n- one\n- two",
		}),
	]
}

# ── tests
expect Sample.said({
	id: Sample.first,
	author: "Steve",
	markdown: "Hello",
}).author().to_str() == "Steve"
expect Sample.time.to_str() == "2026-11-02T19:11:32Z"
expect Sample.second.to_str() == "2"
```

### `app/Timestamp.roc`

```
## **A TIMESTAMP**: when a message was written, as ISO 8601 in UTC, in
## exactly one form, `YYYY-MM-DDTHH:MM:SSZ`, so two times compare as text
## and a transcript reads the same everywhere. Opaque, so `from_str` is the
## only way in.
Timestamp :: Str.{

	## The time `text` names, or why it is refused: not the form, or a month,
	## day, hour, minute or second no clock shows.
	from_str : Str -> Try(Timestamp, [WrongShape, OutOfRange])
	from_str = |text| {
		bytes = text.to_utf8()
		shape = bytes.map(|b| if (b >= '0' and b <= '9') '9' else b)
		if (shape != "9999-99-99T99:99:99Z".to_utf8())
			Err(WrongShape)
		else {
			month = two_digits(bytes, 5)
			day = two_digits(bytes, 8)
			hour = two_digits(bytes, 11)
			minute = two_digits(bytes, 14)
			second = two_digits(bytes, 17)
			if (month >= 1 and month <= 12 and day >= 1 and day <= 31 and hour <= 23 and minute <= 59 and second <= 59)
				Ok(Timestamp.(text))
			else
				Err(OutOfRange)
		}
	}

	## The time as written.
	to_str : Timestamp -> Str
	to_str = |Timestamp.(text)| text

	is_eq : _
}

## The number written by the two digits at `at`; the shape has put digits
## there.
two_digits : List(U8), U64 -> U8
two_digits = |bytes, at| {
	tens = bytes.get(at) ?? crash "Timestamp.two_digits: the shape has a digit here"
	ones = bytes.get(at + 1) ?? crash "Timestamp.two_digits: the shape has a digit here"
	(tens - '0') * 10 + (ones - '0')
}

# ── tests
ok : Str -> Try(Str, [WrongShape, OutOfRange])
ok = |text| Timestamp.from_str(text).map_ok(Timestamp.to_str)

expect ok("2026-11-02T19:11:32Z") == Ok("2026-11-02T19:11:32Z")
expect ok("") == Err(WrongShape)
expect ok("2026-11-02T19:11:32") == Err(WrongShape)
expect ok("2026-11-02T19:11:32z") == Err(WrongShape)
expect ok("2026-11-02 19:11:32Z") == Err(WrongShape)
expect ok("2026-11-02T19:11:32.5Z") == Err(WrongShape)
expect ok("2026-11-02T19:11:32+00:00") == Err(WrongShape)
expect ok("2026-1-02T19:11:32Z") == Err(WrongShape)
expect ok("2026-11-02T19:11:3xZ") == Err(WrongShape)
expect ok("2026-11-02T19:11:32Z\n") == Err(WrongShape)
expect ok("２026-11-02T19:11:32Z") == Err(WrongShape)
# Each field at, and just past, each end of its range.
expect ok("2026-00-02T19:11:32Z") == Err(OutOfRange)
expect ok("2026-01-02T19:11:32Z") == Ok("2026-01-02T19:11:32Z")
expect ok("2026-12-02T19:11:32Z") == Ok("2026-12-02T19:11:32Z")
expect ok("2026-13-02T19:11:32Z") == Err(OutOfRange)
expect ok("2026-11-00T19:11:32Z") == Err(OutOfRange)
expect ok("2026-11-01T19:11:32Z") == Ok("2026-11-01T19:11:32Z")
expect ok("2026-10-31T19:11:32Z") == Ok("2026-10-31T19:11:32Z")
expect ok("2026-10-32T19:11:32Z") == Err(OutOfRange)
expect ok("2026-11-02T00:00:00Z") == Ok("2026-11-02T00:00:00Z")
expect ok("2026-11-02T23:59:59Z") == Ok("2026-11-02T23:59:59Z")
expect ok("2026-11-02T24:11:32Z") == Err(OutOfRange)
expect ok("2026-11-02T19:60:32Z") == Err(OutOfRange)
expect ok("2026-11-02T19:11:60Z") == Err(OutOfRange)
expect ok("0000-11-02T19:11:32Z") == Ok("0000-11-02T19:11:32Z")
expect ok("2026-99-99T99:99:99Z") == Err(OutOfRange)
```

### `app/Topic.roc`

```
## **A TOPIC**: a conversation's name, which becomes a file name and a URL,
## so it is strictly named: ASCII letters, digits and `-`, starting with a
## letter, at most 60 characters. Opaque, so `from_str` is the only way in;
## no space, CR or LF ever reaches a path, a URL or a transcript's id line.
Topic :: Str.{

	## The topic named `name`, or why the name is refused.
	from_str : Str -> Try(Topic, [Empty, TooLong, StartsWithNonLetter, ForbiddenByte])
	from_str = |name| {
		bytes = name.to_utf8()
		match bytes {
			[] => Err(Empty)
			[first, ..] if !is_letter(first) => Err(StartsWithNonLetter)
			_ if bytes.len() > longest => Err(TooLong)
			_ if !bytes.all(|b| is_letter(b) or (b >= '0' and b <= '9') or b == '-') => Err(ForbiddenByte)
			_ => Ok(Topic.(name))
		}
	}

	## The name, as a file name and a URL take it.
	to_str : Topic -> Str
	to_str = |Topic.(name)| name

	is_eq : _
}

## The longest name, in bytes; every byte is ASCII, so in characters too.
longest : U64
longest = 60

is_letter : U8 -> Bool
is_letter = |b| (b >= 'a' and b <= 'z') or (b >= 'A' and b <= 'Z')

# ── tests
expect Topic.from_str("") == Err(Empty)
expect Topic.from_str(" ") == Err(StartsWithNonLetter)
expect Topic.from_str("\t") == Err(StartsWithNonLetter)
expect Topic.from_str("\n") == Err(StartsWithNonLetter)
expect Topic.from_str("\r") == Err(StartsWithNonLetter)
expect Topic.from_str("1plans") == Err(StartsWithNonLetter)
expect Topic.from_str("-plans") == Err(StartsWithNonLetter)
expect Topic.from_str("plans\nnext") == Err(ForbiddenByte)
expect Topic.from_str("plans\r") == Err(ForbiddenByte)
expect Topic.from_str("plans ") == Err(ForbiddenByte)
expect Topic.from_str("plans_2") == Err(ForbiddenByte)
expect Topic.from_str("plans/2") == Err(ForbiddenByte)
expect Topic.from_str("café") == Err(ForbiddenByte)
expect Topic.from_str("a".repeat(61)) == Err(TooLong)
expect Topic.from_str("a".repeat(60)).map_ok(Topic.to_str) == Ok("a".repeat(60))
expect Topic.from_str("a".repeat(59)).map_ok(Topic.to_str) == Ok("a".repeat(59))
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
## Each message opens with the separator, then its id (`MSG_`, the topic,
## `_`, its number), its author, its time, an empty line, its markdown and
## an empty line. Ids count up from the first (Message.Id), so the file's
## order is the conversation's. A conversation with no messages is an empty
## file. A markdown line that is the separator, after any backslashes, is
## written with one backslash more, and read back with one fewer, so no
## message can forge the start of another.
import Author
import Message
import Sample
import Timestamp
import Topic

Transcript := [].{

	## The transcript of `topic`'s messages.
	write : Topic, List(Message) -> Str
	write = |topic, messages| Str.join_with(messages.map(|m| as_written(topic, m)), "")

	## `topic`'s messages, or the first thing wrong with the transcript.
	read : Topic, Str -> Try(List(Message), [Malformed(Str)])
	read = |topic, text|
		if (text.is_empty())
			Ok([])
		else if (!text.starts_with("${separator}\n") or !text.ends_with("\n\n"))
			Err(Malformed("a transcript starts with the separator and ends with an empty line"))
		else
			read_onto({
				topic,
				written: text.drop_prefix("${separator}\n").drop_suffix("\n\n").split_on("\n\n${separator}\n"),
				id: Message.Id.first,
				so_far: [],
			})
}

separator : Str
separator = "-------------"

## One message as the transcript writes it.
as_written : Topic, Message -> Str
as_written = |topic, m|
	"${separator}\nMSG_${topic.to_str()}_${m.id().to_str()}\nfrom: ${m.author().to_str()}\ndate: ${m.time().to_str()}\n\n${escape(m.markdown())}\n\n"

## Each message as written, in order, `id` the first one's, onto `so_far`.
read_onto : {
	topic : Topic,
	written : List(Str),
	id : Message.Id,
	so_far : List(Message),
} -> Try(List(Message), [Malformed(Str)])
read_onto = |
	{
		topic,
		written,
		id,
		so_far,
	},
|
	match written {
		[] => Ok(so_far)
		# The last message never asks for a next id, which would refuse falsely at id 65,535.
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
			read_onto({
				topic,
				written: rest,
				id: next,
				so_far: so_far.append(m),
			})
		}
	}

## Message `id` of `topic`, as written.
read_message : {
	topic : Topic,
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
		] if id_line == "MSG_${topic.to_str()}_${n}" and from_line.starts_with("from: ") and date_line.starts_with("date: ") => {
			author = Author.from_str(from_line.drop_prefix("from: ")).map_err(
				|why|
					match why {
						Blank => Malformed("message ${n} has no author")
						LineBreak => Malformed("message ${n}'s author breaks a line")
					},
			)?
			time = Timestamp.from_str(date_line.drop_prefix("date: ")).map_err(
				|why|
					match why {
						WrongShape => Malformed("message ${n}'s date is not YYYY-MM-DDTHH:MM:SSZ")
						OutOfRange => Malformed("message ${n}'s date is no time a clock shows")
					},
			)?
			Ok(
				Message.new({
					id,
					author,
					time,
					markdown: unescape(Str.join_with(body, "\n")),
				}),
			)
		}
		_ => Err(Malformed("message ${n} is not `MSG_${topic.to_str()}_${n}`, `from:`, `date:` and an empty line"))
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
plans : Topic
plans = Sample.plans

## A transcript of one message from Steve, with `from` and `date` lines as
## given.
one_with : { from : Str, date : Str } -> Str
one_with = |{ from, date }| "-------------\nMSG_plans_1\n${from}\n${date}\n\nhi\n\n"

expect Transcript.write(
	plans,
	[
		Sample.said({
			id: Sample.first,
			author: "Steve",
			markdown: "Hello",
		}),
	],
) == "-------------\nMSG_plans_1\nfrom: Steve\ndate: 2026-11-02T19:11:32Z\n\nHello\n\n"
expect Transcript.read(plans, Transcript.write(plans, Sample.two)) == Ok(Sample.two)
# No messages: an empty file, both ways.
expect Transcript.write(plans, []) == ""
expect Transcript.read(plans, "") == Ok([])
expect Transcript.read(plans, Transcript.write(plans, [])) == Ok([])
# The start and the end, each wrong alone.
expect Transcript.read(
	plans,
	"\n",
) == Err(Malformed("a transcript starts with the separator and ends with an empty line"))
expect Transcript.read(
	plans,
	"MSG_plans_1\nfrom: Steve\ndate: 2026-11-02T19:11:32Z\n\nhi\n\n",
) == Err(Malformed("a transcript starts with the separator and ends with an empty line"))
expect Transcript.read(
	plans,
	"-------------\nMSG_plans_1\nfrom: Steve\ndate: 2026-11-02T19:11:32Z\n\nhi\n",
) == Err(Malformed("a transcript starts with the separator and ends with an empty line"))
expect Transcript.read(
	plans,
	"-------------\nMSG_plans_1\nfrom: Steve\ndate: 2026-11-02T19:11:32Z\n\nhi",
) == Err(Malformed("a transcript starts with the separator and ends with an empty line"))
# Each line of the head, bad alone, beside the good one.
expect Transcript.read(
	plans,
	one_with({ from: "from: Steve", date: "date: 2026-11-02T19:11:32Z" }),
).is_ok()
expect Transcript.read(
	plans,
	one_with({ from: "frm: Steve", date: "date: 2026-11-02T19:11:32Z" }),
) == Err(Malformed("message 1 is not `MSG_plans_1`, `from:`, `date:` and an empty line"))
expect Transcript.read(
	plans,
	one_with({ from: "from: Steve", date: "dt: 2026-11-02T19:11:32Z" }),
) == Err(Malformed("message 1 is not `MSG_plans_1`, `from:`, `date:` and an empty line"))
expect Transcript.read(
	plans,
	one_with({ from: "from: ", date: "date: 2026-11-02T19:11:32Z" }),
) == Err(Malformed("message 1 has no author"))
expect Transcript.read(
	plans,
	one_with({ from: "from:  ", date: "date: 2026-11-02T19:11:32Z" }),
) == Err(Malformed("message 1 has no author"))
expect Transcript.read(
	plans,
	one_with({ from: "from: Steve\r", date: "date: 2026-11-02T19:11:32Z" }),
) == Err(Malformed("message 1's author breaks a line"))
expect Transcript.read(
	plans,
	one_with({ from: "from: Steve", date: "date: 2026-11-02" }),
) == Err(Malformed("message 1's date is not YYYY-MM-DDTHH:MM:SSZ"))
expect Transcript.read(
	plans,
	one_with({ from: "from: Steve", date: "date: 2026-13-02T19:11:32Z" }),
) == Err(Malformed("message 1's date is no time a clock shows"))
# A body that holds the separator, or a backslash before it, comes back whole.
forged : List(Message)
forged = [
	Sample.said({
		id: Sample.first,
		author: "Mallory",
		markdown: "a\n-------------\nMSG_plans_2\nfrom: Steve",
	}),
	Sample.said({
		id: Sample.second,
		author: "Mallory",
		markdown: "\\-------------\n\\\\-------------",
	}),
]
expect Transcript.read(plans, Transcript.write(plans, forged)) == Ok(forged)
expect Transcript.write(plans, forged).split_on("\n${separator}\n").len() == 2
# Near the separator but not it: written as is, read back unchanged.
near : List(Message)
near = [
	Sample.said({
		id: Sample.first,
		author: "Steve",
		markdown: "a-------------\n-------------x\n\\x",
	}),
]
expect Transcript.read(plans, Transcript.write(plans, near)) == Ok(near)
expect Transcript.write(plans, near).contains("\n\na-------------\n-------------x\n\\x\n\n")
expect is_separator_like("-------------")
expect is_separator_like("\\-------------")
expect is_separator_like("\\\\-------------")
expect !is_separator_like("a-------------")
expect !is_separator_like("-------------x")
expect !is_separator_like("\\x")
expect !is_separator_like("------------")
# Out of order, or another topic's: refused by number.
expect Transcript.read(
	plans,
	Transcript.write(
		plans,
		[
			Sample.said({
				id: Sample.second,
				author: "Steve",
				markdown: "x",
			}),
		],
	),
) == Err(Malformed("message 1 is not `MSG_plans_1`, `from:`, `date:` and an empty line"))
expect Transcript.read(
	Sample.other,
	Transcript.write(plans, Sample.two),
) == Err(Malformed("message 1 is not `MSG_other_1`, `from:`, `date:` and an empty line"))
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
import Html
import Topic

## The page for `topic`'s transcript, or a page saying what is wrong with it.
page : List(U8), List(U8) -> List(U8)
page = |topic, transcript| {
	answer =
		match conversation({ topic, transcript }) {
			Ok(c) => c.html()
			Err(Malformed(why)) =>
				Html.page({
					title: "Not a transcript",
					body: Html.element({
						name: "p",
						attrs: [],
						inner: Html.text("Not a transcript: ${why}."),
					}),
				})
		}
	answer.to_str().to_utf8()
}

## The conversation the host's bytes hold, decoded at the door.
conversation : { topic : List(U8), transcript : List(U8) } -> Try(Conversation, [Malformed(Str)])
conversation = |{ topic, transcript }| {
	name = Str.from_utf8(topic) ? |_| Malformed("its topic is not UTF-8")
	text = Str.from_utf8(transcript) ? |_| Malformed("it is not UTF-8")
	checked = Topic.from_str(name) ? |why| Malformed(topic_refused(why))
	Conversation.read(checked, text)
}

## Why a topic's name is refused, in words.
topic_refused : [Empty, TooLong, StartsWithNonLetter, ForbiddenByte] -> Str
topic_refused = |why|
	match why {
		Empty => "its topic is empty"
		TooLong => "its topic is longer than 60 characters"
		StartsWithNonLetter => "its topic does not start with an ASCII letter"
		ForbiddenByte => "its topic holds more than ASCII letters, digits and -"
	}

# ── tests
expect page("plans".to_utf8(), "".to_utf8()) == Html.page({
	title: "plans",
	body: Html.markup("<h1>plans</h1>\n<p class=\"empty\">No messages yet.</p>\n"),
}).to_str().to_utf8()
expect conversation({ topic: [0xff], transcript: [] }) == Err(Malformed("its topic is not UTF-8"))
expect conversation({
	topic: "plans".to_utf8(),
	transcript: [0xff],
}) == Err(Malformed("it is not UTF-8"))
expect conversation({
	topic: [0xff],
	transcript: [0xff],
}) == Err(Malformed("its topic is not UTF-8"))
expect conversation({ topic: "plans".to_utf8(), transcript: [] }).is_ok()
expect conversation({ topic: "".to_utf8(), transcript: [] }) == Err(Malformed("its topic is empty"))
expect conversation({
	topic: "a".repeat(61).to_utf8(),
	transcript: [],
}) == Err(Malformed("its topic is longer than 60 characters"))
expect conversation({
	topic: "1a".to_utf8(),
	transcript: [],
}) == Err(Malformed("its topic does not start with an ASCII letter"))
expect conversation({
	topic: "a b".to_utf8(),
	transcript: [],
}) == Err(Malformed("its topic holds more than ASCII letters, digits and -"))
expect conversation({
	topic: "plans".to_utf8(),
	transcript: "\n".to_utf8(),
}) == Err(Malformed("a transcript starts with the separator and ends with an empty line"))
expect page("<b>".to_utf8(), [0xff]) == Html.page({
	title: "Not a transcript",
	body: Html.markup("<p>Not a transcript: it is not UTF-8.</p>"),
}).to_str().to_utf8()
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

    const roc_test = b.addSystemCommand(&.{ roc, "test", "app/main.roc" });
    roc_test.setCwd(b.path("."));
    roc_test.has_side_effects = true;
    b.step("test", "roc test app/main.roc").dependOn(&roc_test.step);
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

