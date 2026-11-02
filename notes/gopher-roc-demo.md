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
<div class="body"><p>One call per message into roc-markdown, through <code>Markdown</code>:</p>
<pre><code class="language-roc">Markdown.render(m.markdown())
</code></pre>
<p>The page is structure and class names; a client styles it. 🎉</p>
</div></article>

</div>

## The code

### `app/Admin.roc`

```
## **AN ADMIN**: proof that the user acting may do what only an admin may,
## for now creating a channel and choosing its members (`Directory`).
## Steve is the only admin, and there are no levels: an admin may do all
## that an admin does. Opaque, so `of` is the rule's one home and the only
## way in, and a function only an admin may call asks for one in its type.
import UserId

Admin :: UserId.{

	## The acting user `id`, as the edge checked it, as an admin; unless
	## they are not one.
	of : UserId -> Try(Admin, [NotAdmin])
	of = |id| if (id == UserId.steve) Ok(Admin.(id)) else Err(NotAdmin)

	is_eq : _
}

# ── tests
## The id `count` after Steve's.
after_steve : U64 -> UserId
after_steve = |count| List.repeat({}, count).fold(
	UserId.steve,
	|at, {}| at.next() ?? crash "Admin's tests: a test's id fits",
)

# Steve is an admin; the id beside his, and the last, are not.
expect Admin.of(UserId.steve) == Ok(Admin.(UserId.steve))
expect [after_steve(1), after_steve(254)].map(Admin.of) == [Err(NotAdmin), Err(NotAdmin)]
```

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
## **AN AUTHOR**: who wrote a message, by their permanent name (`Name`,
## the one home of the rule a name obeys). An author is a user in the role
## of writing, and the transcript records only the name, so an author is
## only the name: the directory says whose it is (`Directory.User.author`,
## `Directory.check`).
import Name

Author :: Name.{

	## The author named `name`, refused as `Name.from_str` refuses it.
	from_str : Str -> Try(Author, [Empty, ForbiddenCharacter, BadSpacing])
	from_str = |name| Name.from_str(name).map_ok(Author.of)

	## The author of that name.
	of : Name -> Author
	of = |given| Author.(given)

	## The permanent name.
	name : Author -> Name
	name = |Author.(given)| given

	## The name, exactly as given.
	to_str : Author -> Str
	to_str = |Author.(given)| given.to_str()

	is_eq : _
}

# ── tests
# Refused as a name is, by each of its refusals; kept exactly as given.
expect
	[
		"",
		"Ste\u(200b)ve",
		" Steve",
	].map(Author.from_str)
		== [
			Err(Empty),
			Err(ForbiddenCharacter),
			Err(BadSpacing),
		]
expect Author.from_str("Zoë Ann").map_ok(Author.to_str) == Ok("Zoë Ann")
expect {
	steve = Name.from_str("Steve") ?? crash "Author's tests: a name"
	(Author.of(steve).name(), Author.of(steve).to_str()) == (steve, "Steve")
}
```

### `app/ChannelName.roc`

```
## **A CHANNEL'S NAME**: it becomes a folder's name and a URL, so it is a
## strict name (`StrictName`), and it lives in the one namespace with the
## users' names, where its place is its key (`Name.Key.of_strict`).
## Opaque, so `from_str` is the only way in. A strict name starts with a
## letter and holds no `_`, so no channel's name is ever a DM's (`7_11`).
import Name
import StrictName

ChannelName :: StrictName.{

	## The channel named `name`, refused as `StrictName.from_str` refuses
	## it.
	from_str : Str -> Try(ChannelName, [Empty, StartsWithNonLetter, TooLong, ForbiddenByte])
	from_str = |name| StrictName.from_str(name).map_ok(|strict| ChannelName.(strict))

	## The name, as a folder's name and a URL take it.
	to_str : ChannelName -> Str
	to_str = |ChannelName.(strict)| strict.to_str()

	## Its place in the namespace it shares with the users.
	key : ChannelName -> Name.Key
	key = |ChannelName.(strict)| Name.Key.of_strict(strict)

	is_eq : _
	to_hash : _
}

# ── tests
# Refused as a strict name is, by each of its refusals.
expect
	[
		"",
		"1plans",
		"a".repeat(61),
		"plans_2",
	].map(ChannelName.from_str)
		== [
			Err(Empty),
			Err(StartsWithNonLetter),
			Err(TooLong),
			Err(ForbiddenByte),
		]
# Kept as given, case and all, at both ends of the length; its key is a
# strict name's.
expect
	[
		"gopher-roc",
		"Gopher-Roc",
		"p",
		"a".repeat(60),
	].map(
		|text| ChannelName.from_str(text).map_ok(|c| c.to_str()),
	)
		== [
			Ok("gopher-roc"),
			Ok("Gopher-Roc"),
			Ok("p"),
			Ok("a".repeat(60)),
		]
expect {
	text = "Gopher-Roc"
	channel = ChannelName.from_str(text) ?? crash "ChannelName's tests: a channel's name"
	strict = StrictName.from_str(text) ?? crash "ChannelName's tests: a strict name"
	channel.key() == Name.Key.of_strict(strict)
}
```

### `app/Conversation.roc`

```
## **A CONVERSATION**: a topic and its messages, in id order. It stands
## alone: no channel, no DM, no reader, no file. Opaque, so it grows only
## by `append`, which numbers each message by `next_id` and refuses one
## dated before the latest, so a conversation whose ids skip, repeat or run
## backwards, or whose times run backwards, can't be built.
import Message
import Topic

Conversation :: {
	topic : Topic,
	messages : List(Message),
}.{

	## A conversation with no messages yet.
	empty : Topic -> Conversation
	empty = |topic| Conversation.({ topic, messages: [] })

	## The conversation with what arrived added as its next message, and
	## that message, numbered by `next_id`; unless it already holds as many
	## as an id can number (`Full`, asked first), or what arrived is dated
	## before its latest message (`Backdated`).
	##
	## **TIMES NEVER GO BACKWARDS**: a message's time is never earlier than
	## its conversation's latest. Equal is allowed: times are to the
	## second, and two messages can share one.
	append : Conversation, Message.Arrival -> Try({ conversation : Conversation, added : Message }, [Full, Backdated])
	append = |conversation, arrival| {
		id = Conversation.next_id(conversation)?
		Conversation.(c) = conversation
		match c.messages.last() {
			Ok(latest) if arrival.time.compare(latest.time()) == Before => Err(Backdated)
			_ => {
				added = Message.numbered({ id, arrival })
				Ok({ conversation: Conversation.({ ..c, messages: c.messages.append(added) }), added })
			}
		}
	}

	## **THE NEXT MESSAGE'S ID, ITS ONE HOME**: 1 for the first, else the
	## one after the latest's, unless the conversation is full. `append`
	## numbers by it, and a reader asks it first, to name the message it is
	## reading in a refusal.
	next_id : Conversation -> Try(Message.Id, [Full])
	next_id = |Conversation.(c)|
		match c.messages.last() {
			Ok(latest) => latest.id().next()
			Err(ListWasEmpty) => Ok(Message.Id.first)
		}

	## **THE ONE NAME OF A MESSAGE**, `MSG_<topic>_<n>`, as a transcript's
	## id line and a page's link write it.
	reference : Conversation, Message.Id -> Str
	reference = |Conversation.(c), id| "MSG_${c.topic.to_str()}_${id.to_str()}"

	## Its topic.
	topic : Conversation -> Topic
	topic = |Conversation.(c)| c.topic

	## Its messages, oldest first, each numbered by `append`.
	messages : Conversation -> List(Message)
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

## Each message's id, author and markdown, as a test compares them.
summary : List(Message) -> List(
	{
		id : Str,
		author : Str,
		markdown : Str,
	},
)
summary = |messages| messages.map(
	|m| {
		id: m.id().to_str(),
		author: m.author().to_str(),
		markdown: m.markdown(),
	},
)

expect Conversation.empty(Sample.plans).messages() == []
expect Conversation.empty(Sample.plans).topic() == Sample.plans
# A message's reference: its conversation's topic and its id, whether or
# not the conversation holds it yet.
expect Conversation.empty(Sample.plans).reference(Sample.first) == "MSG_plans_1"
expect Conversation.empty(Sample.plans).reference(Sample.second) == "MSG_plans_2"
expect Conversation.empty(Sample.other).reference(Sample.second) == "MSG_other_2"
expect Sample.two.reference(Sample.second) == "MSG_plans_2"
expect Conversation.empty(Sample.plans).next_id() == Ok(Sample.first)
# Each append takes the next id, in order, with what arrived.
expect summary(Sample.two.messages()) == [
	{
		id: "1",
		author: "Steve",
		markdown: "Hello",
	},
	{
		id: "2",
		author: "CC",
		markdown: "Hi!\n\n- one\n- two",
	},
]
expect Sample.two.messages().map(Message.time) == [Sample.hello.time, Sample.reply.time]
expect Sample.two.next_id().map_ok(Message.Id.to_str) == Ok("3")
expect Sample.conversation(Sample.plans, [Sample.hello]).next_id() == Ok(Sample.second)
expect Sample.two.topic() == Sample.plans
# `append` gives back the conversation grown by one and the message it
# added, which is that conversation's latest, at the first id and the
# third.
expect
	Conversation.empty(Sample.plans).append(Sample.hello)
		== Ok({
			conversation: Sample.conversation(Sample.plans, [Sample.hello]),
			added: Message.numbered({ id: Sample.first, arrival: Sample.hello }),
		})
expect
	Sample.two.append(Sample.reply).map_ok(
		|{ conversation, added }| {
			added: summary([added]),
			latest: conversation.messages().last() == Ok(added),
			count: conversation.messages().len(),
		},
	)
		== Ok({
			added: [
				{
					id: "3",
					author: "CC",
					markdown: "Hi!\n\n- one\n- two",
				},
			],
			latest: Bool.True,
			count: 3,
		})
# Times never go backwards: at message 2 and message 3, the latest's time
# again, or a second later, is appended; a second earlier is refused.
## Steve's hello at `time`.
hello_at : Str -> Message.Arrival
hello_at = |time|
	Sample.arrival({
		author: "Steve",
		time,
		markdown: "Hello",
	})

## The ids `arrivals` take after `c`'s messages, each appended alone, or
## why each is refused.
appended_alone : Conversation, List(Message.Arrival) -> List(Try(Str, [Full, Backdated]))
appended_alone = |c, arrivals| arrivals.map(|a| c.append(a).map_ok(|grown| grown.added.id().to_str()))

expect
	appended_alone(
		Sample.conversation(Sample.plans, [Sample.hello]),
		[
			hello_at("2026-11-02T19:11:32Z"),
			hello_at("2026-11-02T19:11:33Z"),
			hello_at("2026-11-02T19:11:31Z"),
			hello_at("2025-11-02T19:11:32Z"),
		],
	)
		== [
			Ok("2"),
			Ok("2"),
			Err(Backdated),
			Err(Backdated),
		]
expect
	appended_alone(
		Sample.two,
		[
			hello_at("2026-11-02T19:12:28Z"),
			hello_at("2026-11-02T19:12:29Z"),
			hello_at("2026-11-02T19:12:27Z"),
			hello_at("2026-11-02T19:11:32Z"),
		],
	)
		== [
			Ok("3"),
			Ok("3"),
			Err(Backdated),
			Err(Backdated),
		]
# The first message has no latest to be before.
expect appended_alone(Conversation.empty(Sample.plans), [hello_at("0000-01-01T00:00:00Z")]) == [Ok("1")]
# The last id at, under and over the highest: 65,534 messages take one
# more, the 65,535th, and then none. The refusal past it is `Full`, asked
# before the time: Steve's hello is also dated before CC's reply.
expect {
	almost = Sample.almost_full
	grown = almost.append(Sample.reply) ?? crash "ConversationSpec: the 65,535th message fits"
	full = grown.conversation
	{
		next_of_almost: almost.next_id().map_ok(Message.Id.to_str),
		added: grown.added.id().to_str(),
		count: full.messages().len(),
		next_of_full: full.next_id(),
		appended: full.append(Sample.hello),
	}
		== {
			next_of_almost: Ok("65535"),
			added: "65535",
			count: 65535,
			next_of_full: Err(Full),
			appended: Err(Full),
		}
}
```

### `app/DateTime.roc`

```
## **A DATE AND TIME**: when a message was written, as ISO 8601 in UTC, in
## exactly one form, `YYYY-MM-DDTHH:MM:SSZ`, so two times compare as text
## (`compare`) and a transcript reads the same everywhere. Opaque, so
## `from_str` is the only way in, and every one names a second some
## calendar and clock show.
##
## **WHY IT IS OURS**: the pinned Roc's builtins (Str, List, Num, Dict, Set,
## Iter, Stream, Crypto, Hasher, Encoding and the rest) have no date or time
## type at all, so this module keeps to what the chat needs, the one form
## read and written and the calendar's check, and gives way to the builtins'
## once they have one.
import Ascii

DateTime :: Str.{

	## The time `text` names, or why it is refused: not the form, or a
	## month, day, hour, minute or second no calendar or clock shows (a
	## 31st of April, a 29th of February outside a leap year, a 24th hour).
	from_str : Str -> Try(DateTime, [WrongShape, OutOfRange])
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
				year = number([
					y1,
					y2,
					y3,
					y4,
				])
				month = number([m1, m2])
				day = number([d1, d2])
				in_calendar = month >= 1 and month <= 12 and day >= 1 and day <= days_in({
					year,
					month,
				})
				hour = number([h1, h2])
				minute = number([n1, n2])
				second = number([s1, s2])
				on_clock = hour <= 23 and minute <= 59 and second <= 59
				if (in_calendar and on_clock) Ok(DateTime.(text)) else Err(OutOfRange)
			}
			_ => Err(WrongShape)
		}

	## The time as written.
	to_str : DateTime -> Str
	to_str = |DateTime.(text)| text

	## **WHICH COMES FIRST**: whether `time` is before, at or after
	## `other`. Every time is written in the one form, its fields from the
	## year down to the second, each a fixed width of digits, so the first
	## byte that differs decides, as it does for the times.
	compare : DateTime, DateTime -> [Before, Same, After]
	compare = |DateTime.(time), DateTime.(other)| byte_order(time.to_utf8(), other.to_utf8())

	is_eq : _
}

## The order of two forms' bytes, by the first that differs.
byte_order : List(U8), List(U8) -> [Before, Same, After]
byte_order = |bytes, others|
	match (bytes, others) {
		([byte, .. as rest], [other, .. as rest_of_others]) if byte == other => byte_order(rest, rest_of_others)
		([byte, ..], [other, ..]) => if (byte < other) Before else After
		_ => Same
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
ok = |text| DateTime.from_str(text).map_ok(DateTime.to_str)

expect ok("2026-11-02T19:11:32Z") == Ok("2026-11-02T19:11:32Z")
expect DateTime.from_str("") == Err(WrongShape)
expect DateTime.from_str("2026-11-02T19:11:32") == Err(WrongShape)
expect DateTime.from_str("2026-11-02T19:11:32z") == Err(WrongShape)
expect DateTime.from_str("2026-11-02 19:11:32Z") == Err(WrongShape)
expect DateTime.from_str("2026-11-02T19:11:32.5Z") == Err(WrongShape)
expect DateTime.from_str("2026-11-02T19:11:32+00:00") == Err(WrongShape)
expect DateTime.from_str("2026-1-02T19:11:32Z") == Err(WrongShape)
expect DateTime.from_str("2026-11-02T19:11:3xZ") == Err(WrongShape)
expect DateTime.from_str("2026-11-02T19:11:32Z\n") == Err(WrongShape)
expect DateTime.from_str("２026-11-02T19:11:32Z") == Err(WrongShape)
expect DateTime.from_str("2026/11-02T19:11:32Z") == Err(WrongShape)
# A digit's neighbours, in a digit's place.
expect DateTime.from_str("202/-11-02T19:11:32Z") == Err(WrongShape)
expect DateTime.from_str("202:-11-02T19:11:32Z") == Err(WrongShape)
# Each field at, and just past, each end of its range.
expect DateTime.from_str("2026-00-02T19:11:32Z") == Err(OutOfRange)
expect ok("2026-01-02T19:11:32Z") == Ok("2026-01-02T19:11:32Z")
expect ok("2026-12-02T19:11:32Z") == Ok("2026-12-02T19:11:32Z")
expect DateTime.from_str("2026-13-02T19:11:32Z") == Err(OutOfRange)
expect DateTime.from_str("2026-11-00T19:11:32Z") == Err(OutOfRange)
expect ok("2026-11-01T19:11:32Z") == Ok("2026-11-01T19:11:32Z")
expect ok("2026-11-02T00:00:00Z") == Ok("2026-11-02T00:00:00Z")
expect ok("2026-11-02T23:59:59Z") == Ok("2026-11-02T23:59:59Z")
expect DateTime.from_str("2026-11-02T24:11:32Z") == Err(OutOfRange)
expect DateTime.from_str("2026-11-02T19:60:32Z") == Err(OutOfRange)
expect DateTime.from_str("2026-11-02T19:11:60Z") == Err(OutOfRange)
expect ok("0000-01-01T00:00:00Z") == Ok("0000-01-01T00:00:00Z")
expect ok("9999-12-31T23:59:59Z") == Ok("9999-12-31T23:59:59Z")
expect DateTime.from_str("2026-99-99T99:99:99Z") == Err(OutOfRange)
# Each month's last day, and the day after it.
expect ok("2026-01-31T19:11:32Z") == Ok("2026-01-31T19:11:32Z")
expect DateTime.from_str("2026-01-32T19:11:32Z") == Err(OutOfRange)
expect ok("2026-04-30T19:11:32Z") == Ok("2026-04-30T19:11:32Z")
expect DateTime.from_str("2026-04-31T19:11:32Z") == Err(OutOfRange)
expect DateTime.from_str("2026-06-31T19:11:32Z") == Err(OutOfRange)
expect DateTime.from_str("2026-09-31T19:11:32Z") == Err(OutOfRange)
expect ok("2026-11-30T19:11:32Z") == Ok("2026-11-30T19:11:32Z")
expect DateTime.from_str("2026-11-31T19:11:32Z") == Err(OutOfRange)
expect ok("2026-12-31T19:11:32Z") == Ok("2026-12-31T19:11:32Z")
expect DateTime.from_str("2026-12-32T19:11:32Z") == Err(OutOfRange)
# February: 28 days, 29 in a leap year, by all three of the rule's parts.
expect ok("2026-02-28T19:11:32Z") == Ok("2026-02-28T19:11:32Z")
expect DateTime.from_str("2026-02-29T19:11:32Z") == Err(OutOfRange)
expect ok("2024-02-29T19:11:32Z") == Ok("2024-02-29T19:11:32Z")
expect DateTime.from_str("2024-02-30T19:11:32Z") == Err(OutOfRange)
expect DateTime.from_str("1900-02-29T19:11:32Z") == Err(OutOfRange)
expect ok("2000-02-29T19:11:32Z") == Ok("2000-02-29T19:11:32Z")
expect is_leap(2024) and is_leap(2000) and is_leap(0)
# The order: the same time, and a second either side of it, within a
# field and across each field's rollover, both ways round.
## Each pair's order, both ways round, from the pair's text.
orders : List((Str, Str)) -> List(([Before, Same, After], [Before, Same, After]))
orders = |pairs|
	pairs.map(
		|(earlier, later)| {
			first = DateTime.from_str(earlier) ?? crash "DateTime's tests: a time"
			second = DateTime.from_str(later) ?? crash "DateTime's tests: a time"
			(first.compare(second), second.compare(first))
		},
	)

expect orders([("2026-11-02T19:11:32Z", "2026-11-02T19:11:32Z")]) == [(Same, Same)]
expect
	orders([
		("2026-11-02T19:11:31Z", "2026-11-02T19:11:32Z"),
		("2026-11-02T19:11:59Z", "2026-11-02T19:12:00Z"),
		("2026-11-02T19:59:59Z", "2026-11-02T20:00:00Z"),
		("2026-11-02T23:59:59Z", "2026-11-03T00:00:00Z"),
		("2026-10-31T23:59:59Z", "2026-11-01T00:00:00Z"),
		("2025-12-31T23:59:59Z", "2026-01-01T00:00:00Z"),
		("0999-12-31T23:59:59Z", "1000-01-01T00:00:00Z"),
	])
		== List.repeat((Before, After), 7)
expect !is_leap(2026) and !is_leap(1900) and !is_leap(2100)
```

### `app/Directory.roc`

```
## **THE DIRECTORY**: every user and every channel, in one namespace, the
## one home of who and what exists. Opaque, so it grows only by its own
## functions: `founded_by` starts it with Steve, id 1; `add_human` and
## `add_agent` number each user by the next id; `create_channel` names a
## channel; and each refuses a name already taken, in any case, by a human,
## an agent or a channel (`Name.key`). So a directory with two users of one
## id, two names alike but for case, or an agent whose owner is not one of
## its humans, can't be built.
##
## **WHAT IT HANDS OUT IS UNFORGEABLE**: a `User` and a `Channel` are views
## only this module makes, so holding one is proof a directory made it.
## Names, ids and roles are permanent, so a user's view never goes stale.
## What comes in from outside is an id, or an id with a name, which `check`
## holds to match.
##
## **ONLY AN ADMIN SHAPES A CHANNEL**: creating one, and admitting or
## removing a member, each asks for an `Admin`, the proof `Admin.of` alone
## makes.
import Admin
import Author
import ChannelName
import Name
import UserId
import UserStem

Directory :: {
	users : List(Directory.User),
	channels : List(Directory.Channel),
	keys : Set(Name.Key),
}.{

	## **A USER**: a human or an agent whose identity the edge has checked,
	## as this directory numbered and named them.
	User :: {
		id : UserId,
		name : Name,
		role : Directory.Role,
	}.{

		## Its id.
		id : Directory.User -> UserId
		id = |Directory.User.(u)| u.id

		## Its permanent name.
		name : Directory.User -> Name
		name = |Directory.User.(u)| u.name

		## A human, or an agent and its owner.
		role : Directory.User -> Directory.Role
		role = |Directory.User.(u)| u.role

		## The user in the role of writing, as a message records them.
		author : Directory.User -> Author
		author = |Directory.User.(u)| Author.of(u.name)

		## Its files' stem (`UserStem`).
		stem : Directory.User -> Str
		stem = |Directory.User.(u)| UserStem.of({ name: u.name, id: u.id })

		is_eq : _
	}

	## **A HUMAN, OR AN AGENT AND ITS OWNER**: every agent has exactly one
	## owner, always a human in the same directory.
	Role : [Human, Agent({ owner : UserId })]

	## **A CHANNEL**: its name and its members, humans and agents.
	Channel :: {
		name : ChannelName,
		members : Set(UserId),
	}.{

		## Its name.
		name : Directory.Channel -> ChannelName
		name = |Directory.Channel.(c)| c.name

		## Its members' ids, lowest first.
		members : Directory.Channel -> List(UserId)
		members = |Directory.Channel.(c)| c.members.to_list().sort_with(UserId.compare)

		## Is `id` one of its members?
		has_member : Directory.Channel, UserId -> Bool
		has_member = |Directory.Channel.(c), id| c.members.contains(id)

		is_eq : _
	}

	## **A USER JOINED**: the directory they joined, and the user.
	Joined : { directory : Directory, added : Directory.User }

	## **A CHANNEL CREATED**: the directory that holds it, and the channel.
	Created : { directory : Directory, created : Directory.Channel }

	## **A NAME AND AN ID, TOGETHER**, as a URL, a file's stem or a
	## session gives them: `check` holds them to match.
	Identity : { id : UserId, name : Name }

	## **A CHANGE TO A CHANNEL'S MEMBERS**, by an admin: who joins or
	## leaves which channel.
	Membership : {
		by : Admin,
		channel : ChannelName,
		member : UserId,
	}

	## **A DIRECTORY'S START: STEVE, ALWAYS ID 1**, named `name`, a human,
	## and no channels.
	founded_by : Name -> Directory
	founded_by = |name|
		Directory.(
			{
				users: [
					Directory.User.(
						{
							id: UserId.steve,
							name,
							role: Human,
						},
					),
				],
				channels: [],
				keys: Set.empty().insert(name.key()),
			},
		)

	## The directory with the human named `name` added, at the next id, and
	## that user; unless every id is taken (`Full`, asked first), or the
	## name is, in any case (`NameTaken`).
	add_human : Directory, Name -> Try(Directory.Joined, [Full, NameTaken])
	add_human = |directory, name|
		added({
			directory,
			name,
			role: Human,
		})

	## The directory with the agent named `name`, owned by `owner`, added at
	## the next id, and that user; unless, in this order, the owner is no
	## user (`NoSuchOwner`) or is an agent (`OwnerIsAgent`), or the agent
	## can't be added as a human can't (`Full`, `NameTaken`).
	add_agent : Directory, { name : Name, owner : UserId } -> Try(Directory.Joined, _)
	add_agent = |directory, { name, owner }| {
		found = directory.user(owner) ? |NoSuchUser| NoSuchOwner
		match found.role() {
			Agent(_) => Err(OwnerIsAgent)
			Human =>
				added({
					directory,
					name,
					role: Agent({ owner: owner }),
				}).map_err(
					|why|
						match why {
							Full => Full
							NameTaken => NameTaken
						},
				)
		}
	}

	## The user `id`, unless there is none.
	user : Directory, UserId -> Try(Directory.User, [NoSuchUser])
	user = |Directory.(d), id|
		match d.users.find_first(|Directory.User.(u)| u.id == id) {
			Ok(found) => Ok(found)
			Err(NotFound) => Err(NoSuchUser)
		}

	## **WHERE A NAME AND AN ID COME TOGETHER, THEY MATCH**: the user `id`,
	## if `name` is theirs exactly (names are case-sensitive); unless there
	## is no such user, or the name is another's spelling.
	check : Directory, Directory.Identity -> Try(Directory.User, [NoSuchUser, NameMismatch])
	check = |directory, { id, name }| {
		found = directory.user(id)?
		if (found.name() == name) Ok(found) else Err(NameMismatch)
	}

	## Every user, in id order.
	users : Directory -> List(Directory.User)
	users = |Directory.(d)| d.users

	## The directory with an empty channel named `name`, and that channel,
	## created by an admin; unless the name is taken, in any case, by a
	## user or a channel.
	create_channel : Directory, { by : Admin, name : ChannelName } -> Try(Directory.Created, [NameTaken])
	create_channel = |Directory.(d), { by: _, name }| {
		key = name.key()
		if (d.keys.contains(key))
			Err(NameTaken)
		else {
			created = Directory.Channel.({ name, members: Set.empty() })
			Ok({
				directory: Directory.(
					{
						..d,
						channels: d.channels.append(created),
						keys: d.keys.insert(key),
					},
				),
				created,
			})
		}
	}

	## The channel named `name`, exactly, unless there is none.
	channel : Directory, ChannelName -> Try(Directory.Channel, [NoSuchChannel])
	channel = |Directory.(d), name|
		match d.channels.find_first(|Directory.Channel.(c)| c.name == name) {
			Ok(found) => Ok(found)
			Err(NotFound) => Err(NoSuchChannel)
		}

	## The directory with the user `member` admitted to `channel` by an
	## admin; unless, in this order, there is no such channel, no such
	## user, or they are already a member.
	admit : Directory, Directory.Membership -> Try(Directory, _)
	admit = |directory, change| {
		Directory.Channel.(c) = directory.channel(change.channel)?
		member = directory.user(change.member)?.id()
		if (c.members.contains(member))
			Err(AlreadyMember)
		else
			Ok(
				with_channel(
					directory,
					Directory.Channel.({ ..c, members: c.members.insert(member) }),
				),
			)
	}

	## The directory with the user `member` removed from `channel` by an
	## admin; unless, in this order, there is no such channel, no such
	## user, or they are not a member.
	remove : Directory, Directory.Membership -> Try(Directory, _)
	remove = |directory, change| {
		Directory.Channel.(c) = directory.channel(change.channel)?
		member = directory.user(change.member)?.id()
		if (c.members.contains(member))
			Ok(
				with_channel(
					directory,
					Directory.Channel.({ ..c, members: c.members.remove(member) }),
				),
			)
		else
			Err(NotMember)
	}

	is_eq : _
}

## `directory` with `changed` in place of its channel of that name, which
## it holds: `admit` and `remove` found it there.
with_channel : Directory, Directory.Channel -> Directory
with_channel = |Directory.(d), changed| {
	name = changed.name()
	Directory.({ ..d, channels: d.channels.map(|c| if (c.name() == name) changed else c) })
}

## **THE ONE WAY A USER JOINS**: `directory` with the user named `name`,
## in `role`, at the next id, and that user; unless every id is taken
## (`Full`), or the name is, in any case (`NameTaken`).
added : {
	directory : Directory,
	name : Name,
	role : Directory.Role,
} -> Try(Directory.Joined, [Full, NameTaken])
added = |
	{
		directory: Directory.(d),
		name,
		role,
	},
| {
	latest = d.users.last() ?? crash "Directory.added: Steve, its first user, is in every directory"
	id = latest.id().next()?
	key = name.key()
	if (d.keys.contains(key))
		Err(NameTaken)
	else {
		user = Directory.User.(
			{
				id,
				name,
				role,
			},
		)
		Ok({
			directory: Directory.(
				{
					..d,
					users: d.users.append(user),
					keys: d.keys.insert(key),
				},
			),
			added: user,
		})
	}
}
```

### `app/DirectorySpec.roc`

```
## **DIRECTORY'S TESTS**: users numbered and named in one namespace with
## the channels, agents owned only by humans, a name and an id held to
## match, and channels shaped by an admin.
import Admin
import ChannelName
import Directory
import Sample
import UserId

DirectorySpec :: [].{}

## A user's id, name and role, as a test compares them.
summary : Directory.User -> {
	id : Str,
	name : Str,
	role : Str,
}
summary = |u| {
	id: u.id().to_str(),
	name: u.name().to_str(),
	role: role_of(u),
}

## A user's role, in words.
role_of : Directory.User -> Str
role_of = |u|
	match u.role() {
		Human => "human"
		Agent({ owner }) => "agent of ${owner.to_str()}"
	}

## The id `count` after Steve's.
after_steve : U64 -> UserId
after_steve = |count| List.repeat({}, count).fold(
	UserId.steve,
	|at, {}| at.next() ?? crash "DirectorySpec: a test's id fits",
)

## The sample directory's first id that is no user's.
stranger : UserId
stranger = after_steve(3)

## The channel named `text`, which a test's always is.
channel_name : Str -> ChannelName
channel_name = |text| ChannelName.from_str(text) ?? crash "DirectorySpec: a test's channel name is one"

## Steve, as an admin.
admin : Admin
admin = Admin.of(UserId.steve) ?? crash "DirectorySpec: Steve is an admin"

## The sample directory with an empty channel, `plans`.
with_plans : Directory
with_plans = (
	Sample.directory.create_channel({
		by: admin,
		name: channel_name("plans"),
	}) ?? crash "DirectorySpec: plans is free"
).directory

## Who `text` would be, added as a human to `directory`, or why not.
human_added : Directory,
Str -> Try(
	{
		id : Str,
		name : Str,
		role : Str,
	},
	[Full, NameTaken],
)
human_added = |
	directory,
	text,
| directory.add_human(Sample.name(text)).map_ok(|grown| summary(grown.added))

## Who `text` would be, added to `directory` as an agent of `owner`, or why
## not.
agent_added : Directory,
{ name : Str, owner : UserId } -> Try(
	{
		id : Str,
		name : Str,
		role : Str,
	},
	[
		NoSuchOwner,
		OwnerIsAgent,
		Full,
		NameTaken,
	],
)
agent_added = |directory, { name, owner }| directory.add_agent({
	name: Sample.name(name),
	owner,
}).map_ok(|grown| summary(grown.added))

# Steve starts every directory, a human, id 1.
expect Directory.founded_by(Sample.name("Steve Howell")).users().map(summary) == [
	{
		id: "1",
		name: "Steve Howell",
		role: "human",
	},
]
# Each user takes the next id, humans and agents in one count.
expect
	Sample.directory.users().map(summary)
		== [
			{
				id: "1",
				name: "Steve",
				role: "human",
			},
			{
				id: "2",
				name: "Apoorva",
				role: "human",
			},
			{
				id: "3",
				name: "CC",
				role: "agent of 1",
			},
		]
expect human_added(Sample.directory, "Damian") == Ok({
	id: "4",
	name: "Damian",
	role: "human",
})
expect agent_added(Sample.directory, { name: "LC", owner: UserId.steve }) == Ok({
	id: "4",
	name: "LC",
	role: "agent of 1",
})
# A name taken by a human or an agent, in any case, is refused; a name
# that differs by more than case is not.
expect
	[
		"Apoorva",
		"apoorva",
		"APOORVA",
		"CC",
		"cC",
		"sTEVE",
	].map(|text| human_added(Sample.directory, text))
		== List.repeat(Err(NameTaken), 6)
expect
	[
		"Apoorvaa",
		"Apoorv",
		"C C",
	].map(|text| human_added(Sample.directory, text).map_ok(|added| added.name))
		== [
			Ok("Apoorvaa"),
			Ok("Apoorv"),
			Ok("C C"),
		]
expect agent_added(Sample.directory, { name: "apoorva", owner: UserId.steve }) == Err(NameTaken)
# A channel's name is in the same namespace: a user can't take it, in any
# case, and a channel can't take a user's.
expect
	["plans", "Plans", "PLANS"].map(|text| human_added(with_plans, text))
		== [
			Err(NameTaken),
			Err(NameTaken),
			Err(NameTaken),
		]
expect agent_added(with_plans, { name: "Plans", owner: UserId.steve }) == Err(NameTaken)
expect human_added(with_plans, "Plansy") == Ok({
	id: "4",
	name: "Plansy",
	role: "human",
})
expect
	[
		"Steve",
		"steve",
		"apoorva",
		"cc",
	].map(
		|text| Sample.directory.create_channel({
			by: admin,
			name: channel_name(text),
		}).map_ok(|grown| grown.created.name()),
	)
		== List.repeat(Err(NameTaken), 4)
expect
	["plans", "Plans"].map(
		|text| with_plans.create_channel({
			by: admin,
			name: channel_name(text),
		}).map_ok(|grown| grown.created.name()),
	)
		== [Err(NameTaken), Err(NameTaken)]
expect
	with_plans.create_channel({
		by: admin,
		name: channel_name("general"),
	}).map_ok(|grown| grown.created.name().to_str())
		== Ok("general")
# An agent's owner is a user, and a human, checked before its name.
expect
	agent_added(Sample.directory, { name: "Bot", owner: Sample.user("Apoorva").id() })
		== Ok({
			id: "4",
			name: "Bot",
			role: "agent of 2",
		})
expect agent_added(Sample.directory, { name: "Bot", owner: stranger }) == Err(NoSuchOwner)
expect agent_added(
	Sample.directory,
	{ name: "Bot", owner: Sample.user("CC").id() },
) == Err(OwnerIsAgent)
expect agent_added(
	Sample.directory,
	{ name: "CC", owner: Sample.user("CC").id() },
) == Err(OwnerIsAgent)
expect agent_added(Sample.directory, { name: "CC", owner: stranger }) == Err(NoSuchOwner)
# The last id at, under and over the highest: 254 users take one more,
# the 255th, and then none, human or agent. `Full` is asked before the
# name and after the owner.
expect {
	almost = Sample.crowded(251)
	full = (almost.add_human(Sample.name("Last")) ?? crash "DirectorySpec: the 255th user fits").directory
	{
		count: almost.users().len(),
		last: human_added(almost, "Last"),
		full_count: full.users().len(),
		human: human_added(full, "Zoë"),
		agent: agent_added(full, { name: "Bot", owner: UserId.steve }),
		taken: human_added(full, "Steve"),
		no_owner: agent_added(full, { name: "Bot", owner: Sample.user("CC").id() }),
	}
		== {
			count: 254,
			last: Ok({
				id: "255",
				name: "Last",
				role: "human",
			}),
			full_count: 255,
			human: Err(Full),
			agent: Err(Full),
			taken: Err(Full),
			no_owner: Err(OwnerIsAgent),
		}
}
# A user found by id, or none.
expect [
	UserId.steve,
	after_steve(2),
].map(|id| Sample.directory.user(id).map_ok(summary).map_ok(|s| s.name)) == [Ok("Steve"), Ok("CC")]
expect Sample.directory.user(stranger) == Err(NoSuchUser)
# A name and an id together: theirs exactly, or refused, case included.
expect Sample.directory.check({ id: UserId.steve, name: Sample.name("Steve") }) == Ok(Sample.steve)
expect
	[
		Sample.name("steve"),
		Sample.name("Apoorva"),
		Sample.name("Steve Howell"),
	].map(|name| Sample.directory.check({ id: UserId.steve, name }))
		== List.repeat(Err(NameMismatch), 3)
expect Sample.directory.check({ id: stranger, name: Sample.name("Steve") }) == Err(NoSuchUser)
# A user as an author, and their files' stem.
expect Sample.directory.users().map(|u| (u.author().to_str(), u.stem())) == [
	("Steve", "steve-1"),
	("Apoorva", "apoorva-2"),
	("CC", "cc-3"),
]
# A channel starts empty, and is found by its exact name.
expect
	Sample.directory.create_channel({ by: admin, name: channel_name("plans") }).map_ok(
		|grown| (
			grown.created.name().to_str(),
			grown.created.members(),
		),
	)
		== Ok(("plans", []))
expect with_plans.channel(channel_name("plans")).map_ok(|c| c.name().to_str()) == Ok("plans")
expect with_plans.channel(channel_name("Plans")) == Err(NoSuchChannel)
expect Sample.directory.channel(channel_name("plans")) == Err(NoSuchChannel)
# Admitting: humans and agents, each once; the members in id order.
## `directory`'s `plans` with each of `ids` admitted in turn.
admitted : Directory, List(UserId) -> Directory
admitted = |directory, ids|
	ids.fold(
		directory,
		|so_far, member| so_far.admit({
			by: admin,
			channel: channel_name("plans"),
			member,
		}) ?? crash "DirectorySpec: a test's member is admitted",
	)

## The sample's `plans`, with all three of its users.
everyone : Directory
everyone = admitted(
	with_plans,
	[
		after_steve(2),
		after_steve(1),
		UserId.steve,
	],
)

## The ids of `directory`'s `plans`'s members.
members_of : Directory -> Try(List(Str), [NoSuchChannel])
members_of = |directory| directory.channel(channel_name("plans")).map_ok(|c| c.members().map(UserId.to_str))

expect members_of(everyone) == Ok(["1", "2", "3"])
expect members_of(admitted(with_plans, [after_steve(2)])) == Ok(["3"])
expect
	everyone.channel(channel_name("plans")).map_ok(
		|c| (
			c.has_member(UserId.steve),
			c.has_member(stranger),
		),
	)
		== Ok((Bool.True, Bool.False))
expect
	[
		everyone.admit({
			by: admin,
			channel: channel_name("plans"),
			member: UserId.steve,
		}),
		with_plans.admit({
			by: admin,
			channel: channel_name("general"),
			member: UserId.steve,
		}),
		with_plans.admit({
			by: admin,
			channel: channel_name("plans"),
			member: stranger,
		}),
		with_plans.admit({
			by: admin,
			channel: channel_name("general"),
			member: stranger,
		}),
	].map(|answer| answer.map_ok(members_of))
		== [
			Err(AlreadyMember),
			Err(NoSuchChannel),
			Err(NoSuchUser),
			Err(NoSuchChannel),
		]
# Removing: a member goes, once; the rest stay.
expect
	everyone.remove({
		by: admin,
		channel: channel_name("plans"),
		member: after_steve(1),
	}).map_ok(members_of)
		== Ok(Ok(["1", "3"]))
expect
	[
		with_plans.remove({
			by: admin,
			channel: channel_name("plans"),
			member: UserId.steve,
		}),
		everyone.remove({
			by: admin,
			channel: channel_name("general"),
			member: UserId.steve,
		}),
		everyone.remove({
			by: admin,
			channel: channel_name("plans"),
			member: stranger,
		}),
		everyone.remove({
			by: admin,
			channel: channel_name("general"),
			member: stranger,
		}),
	].map(|answer| answer.map_ok(members_of))
		== [
			Err(NotMember),
			Err(NoSuchChannel),
			Err(NoSuchUser),
			Err(NoSuchChannel),
		]
```

### `app/Dm.roc`

```
## **A DM**: a place for exactly one or two humans, never an agent, named
## by its pair of user ids in numeric order: `7_11`, never `11_7`, and one
## human alone, in their own DM, `5_5`. A DM's name starts with a digit and
## holds a `_`, and a channel's never does (`StrictName`), so the two never
## collide.
##
## **A DM BEGINS WITH ITS FIRST MESSAGE**: opaque, so `start` is the only
## way in, and it gives the DM together with its first conversation,
## holding that message. A DM with no message, or with an agent in it,
## can't be built.
import Conversation
import DateTime
import Directory
import Topic
import UserId

Dm :: { low : UserId, high : UserId }.{

	## **WHAT STARTING A DM NEEDS**: who writes the first message (`from`),
	## who it is to (`to`; `from` again for one's own DM), the topic, and
	## the message's markdown and time. Both are the directory's users, so
	## each is known to be a human or an agent.
	Start : {
		from : Directory.User,
		to : Directory.User,
		topic : Topic,
		markdown : Str,
		time : DateTime,
	}

	## The DM between `from` and `to`, and its conversation under `topic`,
	## whose first message `from` wrote; unless `from` is an agent, or else
	## `to` is (`Agent`, naming them).
	start : Dm.Start -> Try({ dm : Dm, conversation : Conversation }, [Agent(UserId)])
	start = |
		{
			from,
			to,
			topic,
			markdown,
			time,
		},
	| {
		human_only(from)?
		human_only(to)?
		pair =
			match from.id().compare(to.id()) {
				After => { low: to.id(), high: from.id() }
				_ => { low: from.id(), high: to.id() }
			}
		grown = Conversation.empty(topic).append({
			payload: { author: from.author(), markdown },
			time,
		}) ?? crash "Dm.start: an empty conversation takes its first message"
		Ok({ dm: Dm.(pair), conversation: grown.conversation })
	}

	## Its members' ids, lowest first: two, or one for one's own DM.
	members : Dm -> List(UserId)
	members = |Dm.({ low, high })| if (low == high) [low] else [low, high]

	## **ITS NAME**, as a folder's name and a URL take it: the ids, lowest
	## first, joined by `_`.
	to_str : Dm -> Str
	to_str = |Dm.({ low, high })| "${low.to_str()}_${high.to_str()}"

	is_eq : _
}

## Nothing, if `user` is a human; else the refusal naming them.
human_only : Directory.User -> Try({}, [Agent(UserId)])
human_only = |user|
	match user.role() {
		Human => Ok({})
		Agent(_) => Err(Agent(user.id()))
	}
```

### `app/DmSpec.roc`

```
## **DM'S AND PLACE'S TESTS**: a DM starts with its first message, between
## humans only, named by its pair in numeric order; and no DM's name is a
## channel's.
import ChannelName
import Directory
import DateTime
import Dm
import Message
import Place
import Sample
import UserId

DmSpec :: [].{}

## Noon on the day of the samples.
noon : DateTime
noon = DateTime.from_str("2026-11-02T12:00:00Z") ?? crash "DmSpec: a time"

## **WHO A TEST'S DM IS BETWEEN**: its first message's writer, and who it
## is to.
Ends : { from : Directory.User, to : Directory.User }

## A DM started from `from` to `to`, in `plans`, saying hello at noon.
started : Ends -> Try({ dm : Dm, conversation : _ }, [Agent(UserId)])
started = |{ from, to }|
	Dm.start({
		from,
		to,
		topic: Sample.plans,
		markdown: "hello",
		time: noon,
	})

## A started DM's name and members, as a test compares them.
named : Ends -> Try({ name : Str, members : List(Str) }, [Agent(UserId)])
named = |pair|
	started(pair).map_ok(
		|{ dm, conversation: _ }| {
			name: dm.to_str(),
			members: dm.members().map(UserId.to_str),
		},
	)

## The users the crowded sample numbers 9 and 10.
nine_and_ten : { nine : Directory.User, ten : Directory.User }
nine_and_ten = {
	users = Sample.crowded(7).users()
	when_found = |at| users.get(at) ?? crash "DmSpec: the crowded sample has ten users"
	{ nine: when_found(8), ten: when_found(9) }
}

# Two humans, either one starting: one DM, lowest id first.
expect named({
	from: Sample.steve,
	to: Sample.user("Apoorva"),
}) == Ok({ name: "1_2", members: ["1", "2"] })
expect named({
	from: Sample.user("Apoorva"),
	to: Sample.steve,
}) == Ok({ name: "1_2", members: ["1", "2"] })
expect
	started({ from: Sample.steve, to: Sample.user("Apoorva") }).map_ok(|s| s.dm)
		== started({ from: Sample.user("Apoorva"), to: Sample.steve }).map_ok(|s| s.dm)
# The order is numeric, not the names' text: 9 before 10, both ways.
expect named({
	from: nine_and_ten.ten,
	to: nine_and_ten.nine,
}) == Ok({ name: "9_10", members: ["9", "10"] })
expect named({
	from: nine_and_ten.nine,
	to: nine_and_ten.ten,
}) == Ok({ name: "9_10", members: ["9", "10"] })
# One human alone: their own DM, one member.
expect named({
	from: Sample.user("Apoorva"),
	to: Sample.user("Apoorva"),
}) == Ok({ name: "2_2", members: ["2"] })
# An agent, as either side or both, is refused by id, the sender asked
# first.
expect
	[
		named({ from: Sample.user("CC"), to: Sample.steve }),
		named({ from: Sample.steve, to: Sample.user("CC") }),
		named({ from: Sample.user("CC"), to: Sample.user("CC") }),
	]
		== List.repeat(Err(Agent(Sample.user("CC").id())), 3)
# The DM begins with its first message: the sender's, numbered 1, under
# the topic, at its time.
expect
	started({ from: Sample.user("Apoorva"), to: Sample.steve }).map_ok(
		|{ dm: _, conversation }| {
			topic: conversation.topic(),
			messages: conversation.messages().map(
				|m| (
					m.id(),
					m.author().to_str(),
					m.time(),
					m.markdown(),
				),
			),
		},
	)
		== Ok({
			topic: Sample.plans,
			messages: [
				(
					Message.Id.first,
					"Apoorva",
					noon,
					"hello",
				),
			],
		})
# A place's name: a channel's own, or a DM's pair.
expect {
	plans = ChannelName.from_str("plans") ?? crash "DmSpec: plans is a channel's name"
	dm = (
		started({
			from: Sample.steve,
			to: Sample.user("Apoorva"),
		}) ?? crash "DmSpec: two humans start a DM"
	).dm
	[Place.(Channel(plans)).to_str(), Place.(Dm(dm)).to_str()] == ["plans", "1_2"]
}
# No DM's name is a channel's: each is refused as one, by its first byte.
expect
	["1_2", "2_2", "9_10", "255_255"].map(ChannelName.from_str)
		== List.repeat(Err(StartsWithNonLetter), 4)
```

### `app/Escape.roc`

```
## **TEXT, ESCAPED ONCE, ON ITS WAY IN**: the door for every `Str` a page
## shows, from a person, an agent or a file. It vouches (`TrustedHtml`)
## only for what it has just escaped, so no text it is given is ever
## markup, in an element or an attribute.
import TrustedHtml

Escape :: [].{

	## `s`, escaped, as markup a page can hold.
	text : Str -> TrustedHtml
	text = |s| TrustedHtml.dangerously_trust(escape(s))
}

## **THE ESCAPE**: `&`, `<`, `>`, `"` and `'` as entities. `&` goes first,
## so no entity this writes is escaped again.
escape : Str -> Str
escape = |s|
	s
		.replace_each("&", "&amp;")
		.replace_each("<", "&lt;")
		.replace_each(">", "&gt;")
		.replace_each("\"", "&quot;")
		.replace_each("'", "&#39;")

# ── tests
expect Escape.text("Bea <i>x</i> & \"co\" 'q'").to_utf8() == "Bea &lt;i&gt;x&lt;/i&gt; &amp; &quot;co&quot; &#39;q&#39;".to_utf8()
expect Escape.text("café 🎉").to_utf8() == "café 🎉".to_utf8()
expect Escape.text("").to_utf8() == []
# Text is escaped exactly once: `&amp;` as text is `&amp;amp;`, and that
# fragment, joined into another, comes out unchanged.
expect {
	once = Escape.text("&amp;")
	[
		once.to_utf8(),
		TrustedHtml.join([once]).to_utf8(),
		TrustedHtml.join([TrustedHtml.join([once]), once]).to_utf8(),
	]
		== [
			"&amp;amp;".to_utf8(),
			"&amp;amp;".to_utf8(),
			"&amp;amp;&amp;amp;".to_utf8(),
		]
}
expect TrustedHtml.join([Escape.text("a&b"), Escape.text("<")]).to_utf8() == "a&amp;b&lt;".to_utf8()
```

### `app/HtmlElement.roc`

```
## **AN HTML ELEMENT, BUILT ONLY FROM SAFE PARTS**: `tag` writes
## `<name a="v">inner</name>`, and vouches (`TrustedHtml`) for the two tags
## it writes around `inner`, which is already trusted. Each part of a tag
## is safe by its type, so nothing is escaped and nothing needs to be:
##
## - a name is from a closed set (`Name`), so a tag's name is never data;
## - an attribute's name is its tag (`Attribute`), so a name and its value
##   can't be swapped;
## - every value is a `Token` (ASCII letters, digits and `-`, checked by
##   `Token.from_str`) or a `DateTime` (its one form, digits and `-:TZ`),
##   so no value holds a quote, `&`, `<`, a space or a `:`.
##
## **NO LINK LEAVES THE PAGE**: `Href` always writes `#` and a token, a
## fragment of this page, and a token can't spell a scheme or a path.
## **NO CLASS IS FREE TEXT**: a class is a token, never a sentence or a
## list; which classes a page uses is the page's closed set (`Page.Class`).
import Ascii
import DateTime
import TrustedHtml

HtmlElement :: [].{

	## **AN ELEMENT A PAGE USES**: a closed set, so a tag's name is never data.
	Name : [A, Article, Div, H1, Header, P, Span, Time, Title]

	## **A STRICT TOKEN**: one or more ASCII letters, digits and `-`, so it
	## can stand in an attribute's quotes, and after a `#`, as it is.
	Token :: Str.{

		## The token `text` spells, or why it is refused.
		from_str : Str -> Try(HtmlElement.Token, [Empty, ForbiddenByte])
		from_str = |text|
			if (text.is_empty())
				Err(Empty)
			else if (text.to_utf8().all(is_token_byte))
				Ok(HtmlElement.Token.(text))
			else
				Err(ForbiddenByte)

		## The token as written.
		to_str : HtmlElement.Token -> Str
		to_str = |HtmlElement.Token.(text)| text

		is_eq : _
	}

	## **AN ATTRIBUTE, ITS NAME BY ITS TAG**: a class, an id and a link to
	## an id on this page, each a token, and a time.
	Attribute : [
		Class(HtmlElement.Token),
		Id(HtmlElement.Token),
		Href(HtmlElement.Token),
		DateTime(DateTime),
	]

	## **AN ELEMENT**: `<name a="v">inner</name>`, `inner` as it is,
	## already trusted.
	tag : {
		name : HtmlElement.Name,
		attrs : List(HtmlElement.Attribute),
		inner : TrustedHtml,
	} -> TrustedHtml
	tag = |
		{
			name,
			attrs,
			inner,
		},
	| {
		written = name_of(name)
		opened = Str.join_with(attrs.map(attribute), "")
		TrustedHtml.join([
			TrustedHtml.dangerously_trust("<${written}${opened}>"),
			inner,
			TrustedHtml.dangerously_trust("</${written}>"),
		])
	}
}

is_token_byte : U8 -> Bool
is_token_byte = |b| Ascii.is_letter(b) or Ascii.is_digit(b) or b == '-'

name_of : HtmlElement.Name -> Str
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
attribute : HtmlElement.Attribute -> Str
attribute = |attr|
	match attr {
		Class(token) => " class=\"${token.to_str()}\""
		Id(token) => " id=\"${token.to_str()}\""
		Href(token) => " href=\"#${token.to_str()}\""
		DateTime(time) => " datetime=\"${time.to_str()}\""
	}

# ── tests
## The token `text` spells, which a test knows is one.
token : Str -> HtmlElement.Token
token = |text| HtmlElement.Token.from_str(text) ?? crash "HtmlElement's tests: a token"

# A token: letters, digits and `-`, and the bytes beside each range refused.
expect HtmlElement.Token.from_str("aAzZ09-").map_ok(HtmlElement.Token.to_str) == Ok("aAzZ09-")
expect HtmlElement.Token.from_str("-").map_ok(HtmlElement.Token.to_str) == Ok("-")
expect HtmlElement.Token.from_str("msg-1").map_ok(HtmlElement.Token.to_str) == Ok("msg-1")
expect HtmlElement.Token.from_str("") == Err(Empty)
expect
	[
		"a/",
		"a:",
		"a@",
		"a[",
		"a`",
		"a{",
		"a,",
		"a.",
		"a b",
		"a\"b",
		"a'b",
		"a&b",
		"a<b",
		"a#b",
		"é",
	].map(HtmlElement.Token.from_str)
		== List.repeat(Err(ForbiddenByte), 15)
# No link leaves the page: a scheme, a path or another origin is no token.
expect
	[
		"javascript:alert(1)",
		"https://evil.example",
		"//evil.example",
		"/etc",
	].map(HtmlElement.Token.from_str)
		== List.repeat(Err(ForbiddenByte), 4)
# Every attribute, as an open tag writes it: a link is always `#` and a
# token.
expect
	[
		Class(token("author")),
		Id(token("msg-1")),
		Href(token("msg-1")),
		Href(token("msg-2")),
	].map(attribute)
		== [
			" class=\"author\"",
			" id=\"msg-1\"",
			" href=\"#msg-1\"",
			" href=\"#msg-2\"",
		]
expect
	DateTime.from_str("2026-11-02T19:11:32Z").map_ok(|time| attribute(DateTime(time)))
		== Ok(" datetime=\"2026-11-02T19:11:32Z\"")
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
# An element: its attributes in order, `inner` as it is, never escaped
# again.
expect
	HtmlElement.tag({
		name: A,
		attrs: [Class(token("ref")), Href(token("msg-1"))],
		inner: TrustedHtml.dangerously_trust("&lt;i&gt;"),
	}).to_utf8()
		== "<a class=\"ref\" href=\"#msg-1\">&lt;i&gt;</a>".to_utf8()
expect
	HtmlElement.tag({
		name: P,
		attrs: [],
		inner: TrustedHtml.join([]),
	}).to_utf8()
		== "<p></p>".to_utf8()
```

### `app/Markdown.roc`

```
## **A MESSAGE'S MARKDOWN, RENDERED**: the one entry to roc-markdown (the
## `md` package), and the only module that imports it. Its dialect is
## "Steve flavor" markdown, roc-markdown's own, held byte for byte to the
## Zig chat's renderer. roc-markdown takes and gives bytes; this module
## takes a `Str` and gives `TrustedHtml`, so the rest of the chat never
## handles the renderer's bytes.
##
## **WHY ITS OUTPUT IS VOUCHED FOR** (`TrustedHtml`): roc-markdown escapes
## every byte of a member's text through its one escape, lets through only
## the markup its own allowlist rebuilds, refuses a `javascript:` link, and
## shows media only from a source the uploads rule passes. That rule is
## `SecureImageTag.is_conversation_upload`, chosen here and nowhere else.
import md.Md
import SecureImageTag
import TrustedHtml

Markdown :: [].{

	## `markdown`, exactly as written, as markup a page can hold.
	render : Str -> TrustedHtml
	render = |markdown| {
		rendered = Md.render(markdown.to_utf8(), { uploads: SecureImageTag.is_conversation_upload })
		TrustedHtml.dangerously_trust(Str.from_utf8(rendered) ?? crash "Markdown.render: roc-markdown returned bytes that are not UTF-8, from UTF-8 input")
	}
}

# ── tests
# Its own markup kept, the text in it escaped.
expect Markdown.render("**hi** <b>").to_utf8() == "<p><strong>hi</strong> &lt;b&gt;</p>\n".to_utf8()
expect Markdown.render("a & <b>").to_utf8() == "<p>a &amp; &lt;b&gt;</p>\n".to_utf8()
# Rendered markup is trusted as it is: joined, its entities stay single.
expect
	TrustedHtml.join([TrustedHtml.dangerously_trust("&amp;"), Markdown.render("a & <b>")]).to_utf8()
		== "&amp;<p>a &amp; &lt;b&gt;</p>\n".to_utf8()
# No upload is known (SecureImageTag), so an image is its link; a
# `javascript:` link is text.
expect Markdown.render("![x](a.png)").to_utf8() == "<p><a href=\"a.png\">x</a></p>\n".to_utf8()
expect Markdown.render("[x](javascript:alert(1))").to_utf8() == "<p>[x](javascript:alert(1))</p>\n".to_utf8()
```

### `app/Message.roc`

```
## **A MESSAGE**: who wrote it, when, and what, with the id its
## conversation gives it. Immutable: an edit is a new message. A message
## knows nothing of who may write where; that is the conversation's.
##
## Opaque, so its parts are read, never changed. A message keeps no order
## of its own: `numbered` takes whatever id it is given. The order is
## kept by `Conversation`, which is opaque too, and whose `append` is the
## only way a message joins one, numbered by `Conversation.next_id`.
import Author
import DateTime

Message :: {
	id : Message.Id,
	author : Author,
	time : DateTime,
	markdown : Str,
}.{

	## **WHAT ARRIVES**: who wrote it and the markdown, exactly as written.
	## The message, with its id and time, is made from it as early as
	## possible.
	Payload : {
		author : Author,
		markdown : Str,
	}

	## **A PAYLOAD AND ITS TIME**: what a conversation appends, so the id and
	## the time are added in one place.
	Arrival : {
		payload : Message.Payload,
		time : DateTime,
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

	## The message numbered `id`, from what arrived.
	numbered : { id : Message.Id, arrival : Message.Arrival } -> Message
	numbered = |{ id, arrival: { payload, time } }|
		Message.(
			{
				id,
				author: payload.author,
				time,
				markdown: payload.markdown,
			},
		)

	## Its id.
	id : Message -> Message.Id
	id = |Message.(m)| m.id

	## Who wrote it.
	author : Message -> Author
	author = |Message.(m)| m.author

	## When.
	time : Message -> DateTime
	time = |Message.(m)| m.time

	## Its markdown, exactly as written.
	markdown : Message -> Str
	markdown = |Message.(m)| m.markdown

	is_eq : _
}

# ── tests
steve : Author
steve = Author.from_str("Steve") ?? crash "Message's tests: an author's name"

noon : DateTime
noon = DateTime.from_str("2026-11-02T12:00:00Z") ?? crash "Message's tests: a time"

hello : Message.Arrival
hello = { payload: { author: steve, markdown: "hello" }, time: noon }

cc : Author
cc = Author.from_str("CC") ?? crash "Message's tests: an author's name"

later : DateTime
later = DateTime.from_str("2026-11-02T12:01:00Z") ?? crash "Message's tests: a time"

## A second arrival, every part unlike `hello`'s, so a message is seen to
## carry its own.
reply : Message.Arrival
reply = { payload: { author: cc, markdown: "hi" }, time: later }

## A message's parts, as a test compares them.
parts : Message -> {
	id : Str,
	author : Author,
	time : DateTime,
	markdown : Str,
}
parts = |m| {
	id: m.id().to_str(),
	author: m.author(),
	time: m.time(),
	markdown: m.markdown(),
}

expect Message.Id.first.to_str() == "1"
expect Message.Id.first.next().map_ok(Message.Id.to_str) == Ok("2")
# The last id at, under and over the highest.
expect Message.Id.(65534).next().map_ok(Message.Id.to_str) == Ok("65535")
expect Message.Id.(65535).next() == Err(Full)
# A message numbered with the id it is given, each part what arrived.
expect parts(Message.numbered({ id: Message.Id.first, arrival: hello })) == {
	id: "1",
	author: steve,
	time: noon,
	markdown: "hello",
}
expect parts(Message.numbered({ id: Message.Id.(65535), arrival: reply })) == {
	id: "65535",
	author: cc,
	time: later,
	markdown: "hi",
}
```

### `app/Name.roc`

```
## **A PERMANENT NAME**: a human's, an agent's or a channel's, exactly as
## given, the one home of the rule every name obeys. Names are permanent
## and case-sensitive: someone who signs up as "Steve Howell" is never shown
## as "steve howell". Opaque, so `from_str` is the only way in.
##
## **LETTERS, AND SINGLE SPACES BETWEEN WORDS**: every character is a
## letter of the name's alphabet (`NameAlphabet`, an allowlist: ASCII's
## letters and the accented Latin ones) or a space, and the spaces fall
## only between words, one at a time. So no name holds a digit,
## punctuation, an emoji, a control byte that could end a transcript's
## `from:` line, or an invisible character that could draw it as another
## name, and a permanent name looks like itself.
##
## **ONE NAMESPACE, UNIQUE REGARDLESS OF CASE**: humans, agents and
## channels share it, so no two of them have names that differ only in
## case. `key` is the one spelling that uniqueness compares.
import NameAlphabet
import StrictName

Name :: Str.{

	## The name `name`, or the first reason, in this order, it is refused:
	## empty, a character outside the alphabet that is no space, or a space
	## at either end or beside another.
	from_str : Str -> Try(Name, [Empty, ForbiddenCharacter, BadSpacing])
	from_str = |name|
		if (name.is_empty())
			Err(Empty)
		else if (!NameAlphabet.is_written_in(name))
			Err(ForbiddenCharacter)
		else if (name.starts_with(" ") or name.ends_with(" ") or name.contains("  "))
			Err(BadSpacing)
		else
			Ok(Name.(name))

	## The name, exactly as given.
	to_str : Name -> Str
	to_str = |Name.(name)| name

	## **WHAT UNIQUENESS COMPARES**: two names are the same name in the
	## namespace exactly when their keys are equal. Opaque, so a key is only
	## ever a name's, and is never shown.
	Key :: Str.{

		## **A CHANNEL'S PLACE IN THE NAMESPACE**: a strict name's key, its
		## letters folded as a name's are, so a channel `plans` and a user
		## `Plans` share one. A strict name is ASCII, and its digits and `-`,
		## which no name holds, are kept as they are.
		of_strict : StrictName -> Name.Key
		of_strict = |strict| Name.Key.(NameAlphabet.folded(strict.to_str()))

		is_eq : _
		to_hash : _
	}

	## **THE NAME'S KEY**: its letters case-folded (`NameAlphabet.folded`),
	## so `Zoë` and `ZOË` are one name.
	key : Name -> Name.Key
	key = |Name.(name)| Name.Key.(NameAlphabet.folded(name))

	is_eq : _
}

# ── tests
## The name `text`, as given, or why it is refused.
named : Str -> Try(Str, [Empty, ForbiddenCharacter, BadSpacing])
named = |text| Name.from_str(text).map_ok(Name.to_str)

# Names of letters, with single spaces between words, kept as given.
expect
	["Steve Howell", "Zoë", "Élodie", "CC", "S", "Zoë Ann Smith", "sTeVe"].map(named)
		== [
			Ok("Steve Howell"),
			Ok("Zoë"),
			Ok("Élodie"),
			Ok("CC"),
			Ok("S"),
			Ok("Zoë Ann Smith"),
			Ok("sTeVe"),
		]
expect named("") == Err(Empty)
# Anything outside the alphabet, anywhere: a digit, punctuation, an emoji,
# a control byte, a format character, a space that isn't ASCII's.
expect
	[
		"Steve!",
		"R2D2",
		"Steve 😀",
		"Ste\nve",
		"Steve\u(202e)llewoH",
		"\u(200b)",
		"Ste\u(200d)ve",
		"\u(feff)Steve",
		"Steve\u(a0)Howell",
		"Steve-Howell",
		"O'Brien",
		"\t",
	].map(named)
		== List.repeat(Err(ForbiddenCharacter), 12)
# Spaces: one between words kept; two together, or one at either end, or
# a name of spaces alone, refused.
expect
	[
		"Steve  Howell",
		" Zoë",
		"Zoë ",
		" ",
		"  ",
	].map(named)
		== List.repeat(Err(BadSpacing), 5)
# The order: a forbidden character is named before bad spacing.
expect named(" Steve!") == Err(ForbiddenCharacter)
# The key: names that differ only in case share one, accented letters
# included; any other difference keeps them apart.
## The key of the name `text`, which a test's text always is.
key_of : Str -> Name.Key
key_of = |text| (Name.from_str(text) ?? crash "Name's tests: a test's name is a name").key()

expect key_of("Steve Howell") == key_of("sTeVe hoWEll")
expect key_of("CC") == key_of("cc")
expect key_of("Zoë") == key_of("ZOË")
expect key_of("Élodie") == key_of("élodie")
expect key_of("ſteve") == key_of("Steve")
expect key_of("Steve Howell") != key_of("Steve Howel")
expect key_of("Steve Howell") != key_of("SteveHowell")
expect key_of("Zoë") != key_of("Zoe")
# A strict name's key: a user's of the same letters in any case, and no
# user's while it holds a digit or `-`.
## The key of the strict name `text`, which a test's always is.
strict_key_of : Str -> Name.Key
strict_key_of = |text| Name.Key.of_strict(StrictName.from_str(text) ?? crash "Name's tests: a test's strict name is one")

expect strict_key_of("Plans") == key_of("plans")
expect strict_key_of("plans") == key_of("PLANS")
expect strict_key_of("gopher-roc") != key_of("gopherroc")
expect strict_key_of("gopher-roc") == strict_key_of("Gopher-Roc")
# The name keeps its case; only the key folds it.
expect Name.from_str("Steve") != Name.from_str("steve")
```

### `app/NameAlphabet.roc`

```
## **THE ALPHABET A NAME IS WRITTEN IN**: an allowlist, the one home of
## which letters a permanent name may hold (`Name`), and of how their case
## folds. The letters are ASCII's `A`-`Z` and `a`-`z`, and the accented
## Latin ones: Latin-1's (U+00C0 to U+00FF, but for `×` and `÷`) and Latin
## Extended-A's (U+0100 to U+017F). Anything else (a digit, punctuation,
## an emoji, a control character, an invisible format character such as
## U+202E or U+200B) is refused by not being listed.
##
## **BYTE BY BYTE**: every accented letter is two UTF-8 bytes, a lead of
## 0xC3, 0xC4 or 0xC5 and one more, so both rules match on bytes, and a
## `Str`, always valid UTF-8, needs no decoder.
import Ascii

NameAlphabet :: [].{

	## Is every character of `text` a letter of the alphabet or a space?
	is_written_in : Str -> Bool
	is_written_in = |text| is_all_letters_or_spaces(text.to_utf8())

	## **THE CASE-FOLDED SPELLING**: each letter of `text`, which is written
	## in the alphabet or is ASCII, folded by Unicode's simple case folding, so names
	## that differ only in case, `ZOË` and `Zoë`, fold alike. `ſ` folds to
	## `s`, and `ß`, `ĸ`, `ŉ`, `ı` and `İ` stay as they are.
	folded : Str -> Str
	folded = |text|
		Str.from_utf8(
			folded_onto({
				out: [],
				bytes: text.to_utf8(),
			}),
		) ?? crash "NameAlphabet.folded: a letter folds to a letter, and letters are UTF-8"
}

## Is every character `bytes` hold a letter or a space?
is_all_letters_or_spaces : List(U8) -> Bool
is_all_letters_or_spaces = |bytes|
	match bytes {
		[] => Bool.True
		[b, .. as rest] if b == ' ' or Ascii.is_letter(b) => is_all_letters_or_spaces(rest)
		[
			0xC3,
			b,
			.. as rest,
		] if b >= 0x80 and b != 0x97 and b != 0xB7 => is_all_letters_or_spaces(rest)
		[lead, _, .. as rest] if lead == 0xC4 or lead == 0xC5 => is_all_letters_or_spaces(rest)
		_ => Bool.False
	}

## `out` with each character of `bytes`, which are written in the
## alphabet, folded.
folded_onto : { out : List(U8), bytes : List(U8) } -> List(U8)
folded_onto = |{ out, bytes }|
	match bytes {
		[] => out
		[lead, b, .. as rest] if lead >= 0xC3 and lead <= 0xC5 => {
			point = (lead - 0xC0).to_u32() * 64 + (b - 0x80).to_u32()
			folded_onto({ out: out.concat(encoded(fold(point))), bytes: rest })
		}
		[b, .. as rest] => {
			point = b.to_u32()
			folded_onto({ out: out.concat(encoded(fold(point))), bytes: rest })
		}
	}

## **ONE LETTER'S FOLD**: its lower case, where it has one by Unicode's
## simple case folding.
fold : U32 -> U32
fold = |point|
	if (point >= 'A' and point <= 'Z')
		point + 32
	else if (point >= 0xC0 and point <= 0xDE and point != 0xD7)
		point + 0x20
	else if (point == 0x178)
		0xFF
	else if (point == 0x17F)
		's'
	else if (is_upper_of_pair(point))
		point + 1
	else
		point

## **LATIN EXTENDED-A'S CASE PAIRS**: each capital is followed by its small
## letter, from an even code point in three runs and an odd one in two.
is_upper_of_pair : U32 -> Bool
is_upper_of_pair = |point| {
	is_even = point % 2 == 0
	(point >= 0x100 and point <= 0x12F and is_even)
		or (point >= 0x132 and point <= 0x137 and is_even)
		or (point >= 0x139 and point <= 0x148 and !is_even)
		or (point >= 0x14A and point <= 0x177 and is_even)
		or (point >= 0x179 and point <= 0x17E and !is_even)
}

## A code point below U+0800 as UTF-8: one byte below 0x80, else two.
encoded : U32 -> List(U8)
encoded = |point|
	if (point < 0x80)
		[point.to_u8_wrap()]
	else
		[(0xC0 + point // 64).to_u8_wrap(), (0x80 + point % 64).to_u8_wrap()]

# ── tests
# Each end of every listed range kept, and the character beside it, past
# the list, refused: ASCII's letters, Latin-1's (around `×` and `÷`) and
# Latin Extended-A's.
expect
	[
		"A",
		"Z",
		"a",
		"z",
		" ",
		"À",
		"Ö",
		"Ø",
		"ö",
		"ø",
		"ÿ",
		"Ā",
		"ſ",
		"Élodie",
		"Zoë Ann",
	].all(NameAlphabet.is_written_in)
expect
	[
		"@",
		"[",
		"`",
		"{",
		"¿",
		"×",
		"÷",
		"ƀ",
		"0",
		"9",
		"!",
		"-",
		"'",
		".",
		"\t",
		"\u(0)",
		"\u(a0)",
		"\u(202e)",
		"\u(200b)",
		"\u(feff)",
		"😀",
		"李",
	].all(|text| !NameAlphabet.is_written_in(text))
# One stray character anywhere refuses the whole text.
expect !NameAlphabet.is_written_in("Steve!")
expect !NameAlphabet.is_written_in("R2D2")
expect NameAlphabet.is_written_in("")
# The fold: each run's capitals to their small letters, at each run's
# ends; small letters and the uncased ones as they are.
expect
	[
		"AZ",
		"ÀÖ",
		"ØÞ",
		"ĀĮ",
		"ĲĶ",
		"ĹŇ",
		"ŊŶ",
		"ŹŽ",
		"Ÿ",
		"ſ",
		"ZOË Ann",
	].map(NameAlphabet.folded)
		== ["az", "àö", "øþ", "āį", "ĳķ", "ĺň", "ŋŷ", "źž", "ÿ", "s", "zoë ann"]
expect
	["azàöøþÿ", "āįĳķĺňŋŷźž", "ßĸŉıİ", " "].map(NameAlphabet.folded)
		== ["azàöøþÿ", "āįĳķĺňŋŷźž", "ßĸŉıİ", " "]
```

### `app/Page.roc`

```
## **THE PAGES**: a conversation's, and the one that says why there is
## none. Every page is the same skeleton (the doctype, its title, the style
## sheet, then its body); the page carries structure and class names, and
## only enough style to read, so a client can style the rest.
##
## **THE PAGE'S VOCABULARY LIVES HERE**: its classes (`Class`, a closed set,
## so no class is free text), the one anchor rule (`msg-<n>`, which an
## element's id and a link's `#` both write) and the CSS that styles them.
##
## **WHAT IS TRUSTED, AND WHO VOUCHES**: every `Str` a page shows goes in
## through `Escape.text`, a message's markdown through `Markdown.render`,
## and every element through `HtmlElement.tag`. This module vouches
## (`TrustedHtml.dangerously_trust`) for two constants only: the doctype
## and the style sheet, both written here, the CSS holding no `<`.
import Conversation
import HtmlElement
import Escape
import Markdown
import Message
import TrustedHtml

Page :: [].{

	## **A CLASS A PAGE USES**: a closed set, so a class is never data.
	Class : [Author, Body, Empty, Message, Ref]

	## The class attribute for `class`, its one spelling.
	class : Page.Class -> HtmlElement.Attribute
	class = |chosen| Class(token(class_name(chosen)))

	## **A CONVERSATION'S PAGE**: the topic, then each message under its
	## author and time, with its reference (`Conversation.reference`) as a
	## link to itself.
	conversation : Conversation -> TrustedHtml
	conversation = |c| {
		topic = c.topic()
		heading = HtmlElement.tag({
			name: H1,
			attrs: [],
			inner: Escape.text(topic.to_str()),
		})
		messages =
			if (c.messages().is_empty())
				TrustedHtml.join([
					HtmlElement.tag({
						name: P,
						attrs: [Page.class(Empty)],
						inner: Escape.text("No messages yet."),
					}),
					newline,
				])
			else
				TrustedHtml.join(c.messages().map(|m| message(c, m)))
		whole({
			title: topic.to_str(),
			body: TrustedHtml.join([
				heading,
				newline,
				messages,
			]),
		})
	}

	## **THE PAGE FOR A REFUSED TRANSCRIPT**, saying why in `why`'s words.
	refused : Str -> TrustedHtml
	refused = |why|
		whole({
			title: "Not a transcript",
			body: HtmlElement.tag({
				name: P,
				attrs: [],
				inner: Escape.text("Not a transcript: ${why}."),
			}),
		})
}

## One message: its header, then its markdown rendered.
message : Conversation, Message -> TrustedHtml
message = |c, m| {
	id = m.id()
	header = TrustedHtml.join([
		HtmlElement.tag({
			name: Span,
			attrs: [Page.class(Author)],
			inner: Escape.text(m.author().to_str()),
		}),
		space,
		HtmlElement.tag({
			name: Time,
			attrs: [DateTime(m.time())],
			inner: Escape.text(m.time().to_str()),
		}),
		space,
		HtmlElement.tag({
			name: A,
			attrs: [Page.class(Ref), Href(anchor(id))],
			inner: Escape.text(c.reference(id)),
		}),
	])
	article = HtmlElement.tag({
		name: Article,
		attrs: [Page.class(Message), Id(anchor(id))],
		inner: TrustedHtml.join([
			HtmlElement.tag({
				name: Header,
				attrs: [],
				inner: header,
			}),
			newline,
			HtmlElement.tag({
				name: Div,
				attrs: [Page.class(Body)],
				inner: Markdown.render(m.markdown()),
			}),
		]),
	})
	TrustedHtml.join([article, newline])
}

## **THE SKELETON EVERY PAGE SHARES**: the doctype and charset, `title` as
## its title, the style sheet, then `body`.
whole : { title : Str, body : TrustedHtml } -> TrustedHtml
whole = |{ title, body }|
	TrustedHtml.join([
		doctype,
		HtmlElement.tag({
			name: Title,
			attrs: [],
			inner: Escape.text(title),
		}),
		newline,
		stylesheet,
		body,
	])

## The doctype and the charset, which every page opens with: a constant,
## vouched for here.
doctype : TrustedHtml
doctype = TrustedHtml.dangerously_trust("<!doctype html>\n<meta charset=utf-8>\n")

## **THE STYLE SHEET EVERY PAGE CARRIES**: only enough to read, so a client
## styles the rest. Vouched for here: `css` is this module's constant, and
## holds no `<`, so it can't close its element early.
stylesheet : TrustedHtml
stylesheet = TrustedHtml.dangerously_trust("<style>\n${css}</style>\n")

## The style sheet's rules, for the classes in `Class`. CSS is code, never
## data.
css : Str
css =
	\\body{font:16px/1.4 system-ui,sans-serif;max-width:46rem;margin:2rem auto;padding:0 1rem}
	\\.message{border-top:1px solid #ccc;padding:.5rem 0}
	\\.author{font-weight:600}
	\\time,.ref{color:#777;font-size:.85em}
	\\.ref{float:right}
	\\

class_name : Page.Class -> Str
class_name = |chosen|
	match chosen {
		Author => "author"
		Body => "body"
		Empty => "empty"
		Message => "message"
		Ref => "ref"
	}

## **A MESSAGE'S ANCHOR**, `msg-<n>`: the one home of its spelling, which
## an element's id and a link's `#` both write.
anchor : Message.Id -> HtmlElement.Token
anchor = |id| token("msg-${id.to_str()}")

## The token `text` spells, for a name this module writes: one that isn't
## is this module's bug.
token : Str -> HtmlElement.Token
token = |text| HtmlElement.Token.from_str(text) ?? crash "Page.token: \"${text}\" is a name this module writes, and not a token"

newline : TrustedHtml
newline = Escape.text("\n")

space : TrustedHtml
space = Escape.text(" ")

# ── tests
## An element `attrs` alone opens, as a test reads it.
opened : List(HtmlElement.Attribute) -> List(U8)
opened = |attrs|
	HtmlElement.tag({
		name: P,
		attrs,
		inner: TrustedHtml.join([]),
	}).to_utf8()

# Every class, each its one spelling.
expect [Author, Body, Empty, Message, Ref].map(|chosen| opened([Page.class(chosen)])) == [
	"<p class=\"author\"></p>".to_utf8(),
	"<p class=\"body\"></p>".to_utf8(),
	"<p class=\"empty\"></p>".to_utf8(),
	"<p class=\"message\"></p>".to_utf8(),
	"<p class=\"ref\"></p>".to_utf8(),
]
# A message's anchor as an id and as a link, at the first id and the next.
expect {
	second = Message.Id.first.next() ?? crash "Page's tests: the first id has a next"
	[
		opened([Id(anchor(Message.Id.first))]),
		opened([Href(anchor(Message.Id.first))]),
		opened([Id(anchor(second))]),
		opened([Href(anchor(second))]),
	]
		== [
			"<p id=\"msg-1\"></p>".to_utf8(),
			"<p href=\"#msg-1\"></p>".to_utf8(),
			"<p id=\"msg-2\"></p>".to_utf8(),
			"<p href=\"#msg-2\"></p>".to_utf8(),
		]
}
expect doctype.to_utf8() == "<!doctype html>\n<meta charset=utf-8>\n".to_utf8()
expect stylesheet.to_utf8() == "<style>\n${css}</style>\n".to_utf8()
expect !css.contains("<")
```

### `app/PageSpec.roc`

```
## **PAGE'S TESTS**: each page, byte for byte.
import Conversation
import Page
import Sample

PageSpec :: [].{}

## What every page opens with, titled `title` (already escaped). Its style
## sheet is a frozen answer, copied from `Page`'s style sheet, so a change to
## the style shows here as a deliberate re-freeze.
head : Str -> Str
head = |title|
	"<!doctype html>\n<meta charset=utf-8>\n<title>${title}</title>\n<style>\nbody{font:16px/1.4 system-ui,sans-serif;max-width:46rem;margin:2rem auto;padding:0 1rem}\n.message{border-top:1px solid #ccc;padding:.5rem 0}\n.author{font-weight:600}\ntime,.ref{color:#777;font-size:.85em}\n.ref{float:right}\n</style>\n"

# No messages: the page says so, and only then.
expect Page.conversation(Conversation.empty(Sample.plans)).to_utf8() == "${head("plans")}<h1>plans</h1>\n<p class=\"empty\">No messages yet.</p>\n".to_utf8()
expect
	Page.conversation(Sample.two).to_utf8()
		== "${head("plans")}<h1>plans</h1>\n<article class=\"message\" id=\"msg-1\"><header><span class=\"author\">Steve</span> <time datetime=\"2026-11-02T19:11:32Z\">2026-11-02T19:11:32Z</time> <a class=\"ref\" href=\"#msg-1\">MSG_plans_1</a></header>\n<div class=\"body\"><p>Hello</p>\n</div></article>\n<article class=\"message\" id=\"msg-2\"><header><span class=\"author\">CC</span> <time datetime=\"2026-11-02T19:12:28Z\">2026-11-02T19:12:28Z</time> <a class=\"ref\" href=\"#msg-2\">MSG_plans_2</a></header>\n<div class=\"body\"><p>Hi!</p>\n<ul>\n<li>one</li>\n<li>two</li>\n</ul>\n</div></article>\n".to_utf8()
# The markdown's own markup kept, and markup typed in it shown as text. A
# name can hold no markup (`Name`), and is escaped as all text is.
expect
	Page.conversation(
		Sample.conversation(
			Sample.plans,
			[
				Sample.arrival({
					author: "Eve",
					time: "2026-11-02T19:11:32Z",
					markdown: "**hi** <b>",
				}),
			],
		),
	).to_utf8()
		== "${head("plans")}<h1>plans</h1>\n<article class=\"message\" id=\"msg-1\"><header><span class=\"author\">Eve</span> <time datetime=\"2026-11-02T19:11:32Z\">2026-11-02T19:11:32Z</time> <a class=\"ref\" href=\"#msg-1\">MSG_plans_1</a></header>\n<div class=\"body\"><p><strong>hi</strong> &lt;b&gt;</p>\n</div></article>\n".to_utf8()
# A refusal's words are text on its page.
expect Page.refused("it <is> not UTF-8").to_utf8() == "${head("Not a transcript")}<p>Not a transcript: it &lt;is&gt; not UTF-8.</p>".to_utf8()
```

### `app/Place.roc`

```
## **WHERE A CONVERSATION LIVES**: a channel or a DM. A topic is unique
## only within its place, so a conversation's identity is its place and its
## topic; the conversation itself stands alone, knowing neither
## (`Conversation`).
##
## **A PLACE'S NAME** is a folder's and a URL's: a channel's name, or a
## DM's pair. A channel's starts with a letter and holds no `_`; a DM's
## starts with a digit and holds one; so no two places share a name.
import ChannelName
import Dm

Place := [Channel(ChannelName), Dm(Dm)].{

	## Its name, as a folder's name and a URL take it.
	to_str : Place -> Str
	to_str = |Place.(place)|
		match place {
			Channel(name) => name.to_str()
			Dm(dm) => dm.to_str()
		}

	is_eq : _
}
```

### `app/Sample.roc`

```
## **SAMPLES FOR THE SPECS**: the topics, payloads and conversation the
## `*Spec.roc` modules share, so each test reads as what it checks. Only a
## Spec imports it; no production module does.
import Author
import Conversation
import Directory
import Message
import DateTime
import Name
import Topic
import UserId

Sample :: [].{

	## The topic the samples are written under.
	plans : Topic
	plans = Topic.from_str("plans") ?? crash "Sample.plans: a topic's name"

	## Another topic, whose transcript is not `plans`'s.
	other : Topic
	other = Topic.from_str("other") ?? crash "Sample.other: a topic's name"

	## What arrives, from its parts' text, each a test's own and accepted.
	arrival : {
		author : Str,
		time : Str,
		markdown : Str,
	} -> Message.Arrival
	arrival = |
		{
			author,
			time,
			markdown,
		},
	|
		{
			payload: {
				author: Author.from_str(author) ?? crash "Sample.arrival: a test's author is a name",
				markdown,
			},
			time: DateTime.from_str(time) ?? crash "Sample.arrival: a test's time is a time",
		}

	## Steve's hello.
	hello : Message.Arrival
	hello = Sample.arrival({
		author: "Steve",
		time: "2026-11-02T19:11:32Z",
		markdown: "Hello",
	})

	## CC's reply, a minute later, with a list in its markdown.
	reply : Message.Arrival
	reply = Sample.arrival({
		author: "CC",
		time: "2026-11-02T19:12:28Z",
		markdown: "Hi!\n\n- one\n- two",
	})

	## `topic`'s conversation of `arrivals`, appended in order; a test's
	## conversation is never full, and its times never go backwards.
	conversation : Topic, List(Message.Arrival) -> Conversation
	conversation = |topic, arrivals|
		arrivals.fold(
			Conversation.empty(topic),
			|c, a| (c.append(a) ?? crash "Sample.conversation: a test's conversation is neither full nor backdated").conversation,
		)

	## `plans`'s hello and reply.
	two : Conversation
	two = Sample.conversation(Sample.plans, [Sample.hello, Sample.reply])

	## **A CONVERSATION ONE MESSAGE SHORT OF FULL**: 65,534 of Steve's hello.
	## A constant, so the specs that need it share one, built once: the
	## build is about a second of a cold run. Only the tests of the most a
	## conversation holds use it.
	almost_full : Conversation
	almost_full = filled({ so_far: Conversation.empty(Sample.plans), count: 65534 })

	## The first message's id.
	first : Message.Id
	first = Message.Id.first

	## The second message's id.
	second : Message.Id
	second = Message.Id.first.next() ?? crash "Sample.second: the first id has a next"

	## The third message's id.
	third : Message.Id
	third = Sample.second.next() ?? crash "Sample.third: the second id has a next"

	## The permanent name `text`, which a test's always is.
	name : Str -> Name
	name = |text| Name.from_str(text) ?? crash "Sample.name: a test's name is a name"

	## **THE SAMPLE DIRECTORY**: Steve (1) and Apoorva (2), humans, and CC
	## (3), Steve's agent.
	directory : Directory
	directory = {
		founded = Directory.founded_by(Sample.name("Steve"))
		with_apoorva = (founded.add_human(Sample.name("Apoorva")) ?? crash "Sample.directory: Apoorva's name is free").directory
		with_cc = with_apoorva.add_agent({
			name: Sample.name("CC"),
			owner: UserId.steve,
		}) ?? crash "Sample.directory: CC's name is free"
		with_cc.directory
	}

	## **THE SAMPLE DIRECTORY, CROWDED**: with `count` more humans, each
	## named for their place in letters (`Filler aa`, `Filler ab`...).
	crowded : U64 -> Directory
	crowded = |count|
		List.from_iter(U64.until(0, count)).fold(
			Sample.directory,
			|so_far, at| (so_far.add_human(Sample.name("Filler ${place_in_letters(at)}")) ?? crash "Sample.crowded: a filler's name is free").directory,
		)

	## Steve, in the sample directory.
	steve : Directory.User
	steve = Sample.user("Steve")

	## The sample directory's user named `text`, which it holds.
	user : Str -> Directory.User
	user = |text|
		Sample.directory.users().find_first(|u| u.name().to_str() == text) ?? crash "Sample.user: the sample directory holds ${text}"
}

## `at`, below 676, as two letters: 0 is `aa`, 1 `ab`, 26 `ba`.
place_in_letters : U64 -> Str
place_in_letters = |at|
	Str.from_utf8(['a' + (at // 26).to_u8_wrap(), 'a' + (at % 26).to_u8_wrap()]) ?? crash "Sample.place_in_letters: letters are UTF-8"

## `so_far` with `count` more of Steve's hello.
filled : { so_far : Conversation, count : U64 } -> Conversation
filled = |{ so_far, count }|
	if (count == 0)
		so_far
	else
		filled({
			so_far: (so_far.append(Sample.hello) ?? crash "Sample.filled: the conversation has room").conversation,
			count: count - 1,
		})
```

### `app/SecureImageTag.roc`

```
## **SECURE IMAGE TAGS: WHICH IMAGES A MESSAGE MAY SHOW**, the one home of
## that rule. A message's markdown may hold an image (`![alt](src)` or an
## `<img>`, and a `<video>` too, which roc-markdown rules the same way);
## `Markdown.render` hands roc-markdown `is_conversation_upload` as its
## uploads rule, and roc-markdown shows as media only a source that passes
## it, after judging the source safe as a same-origin URL itself. A source
## that fails is left as text: an image becomes a plain link.
##
## **THE RULE** (`docs/design.md`, "Images"): an uploaded image belongs to
## one conversation, and exactly that conversation's readers can see it.
## So a message may show an image only from its own conversation's
## uploads, and every other source is refused.
##
## **WHAT ISN'T BUILT YET: UPLOADS.** No conversation has an upload, so
## today every source is refused, on purpose, not by oversight. When
## uploads exist, this rule asks the conversation for its own.
##
## What the renderer's output becomes on a page is vouched for at
## `TrustedHtml`'s one door; see its header for the others. Text from
## outside comes in only through `UnvalidatedString`.
SecureImageTag :: [].{

	## Is `source` one of the message's conversation's uploads? No
	## conversation has any yet, so no source is.
	is_conversation_upload : List(U8) -> Bool
	is_conversation_upload = |_source| Bool.False
}

# ── tests
# Every kind of source refused: relative, absolute, another origin, `data:`
# and `javascript:`, and the empty one.
expect
	[
		"a.png",
		"/user_uploads/a.png",
		"https://evil.example/a.png",
		"data:image/png;base64,AAAA",
		"javascript:alert(1)",
		"",
	]
		.map(|source| SecureImageTag.is_conversation_upload(source.to_utf8()))
		== List.repeat(Bool.False, 6)
```

### `app/SecureImageTagSpec.roc`

```
## **SECURE IMAGE TAGS' TESTS, THROUGH THE RENDERER**: every image a
## message's markdown can hold, by every kind of source, comes out as the
## frozen rendering that is no image, since no conversation has an upload
## yet (`SecureImageTag`).
import Markdown

SecureImageTagSpec :: [].{}

## `markdown` rendered, as a test reads it.
shown : Str -> Str
shown = |markdown| Str.from_utf8(Markdown.render(markdown).to_utf8()) ?? crash "SecureImageTagSpec: a render is UTF-8"

# `![alt](src)`: a relative, an absolute, another origin's, a `data:` and
# a `javascript:` source. Each is a plain link, or text, never an image.
expect shown("![x](a.png)") == "<p><a href=\"a.png\">x</a></p>\n"
expect shown("![x](/user_uploads/a.png)") == "<p><a href=\"/user_uploads/a.png\">x</a></p>\n"
expect shown("![x](https://evil.example/a.png)") == "<p><a href=\"https://evil.example/a.png\" target=\"_blank\" rel=\"noopener\">x</a></p>\n"
expect shown("![x](data:image/png;base64,AAAA)") == "<p><a href=\"data:image/png;base64,AAAA\">x</a></p>\n"
expect shown("![x](javascript:alert(1))") == "<p>![x](javascript:alert(1))</p>\n"
# An `<img>` tag, the same four sources: each is text, escaped.
expect shown("<img src=\"a.png\">") == "&lt;img src=&quot;a.png&quot;&gt;"
expect shown("<img src=\"/user_uploads/a.png\">") == "&lt;img src=&quot;/user_uploads/a.png&quot;&gt;"
expect shown("<img src=\"data:image/png;base64,AAAA\">") == "&lt;img src=&quot;data:image/png;base64,AAAA&quot;&gt;"
expect shown("<img src=\"javascript:alert(1)\">") == "&lt;img src=&quot;javascript:alert(1)&quot;&gt;"
```

### `app/Separator.roc`

```
## **THE SEPARATOR, AND A MESSAGE THAT CAN'T FORGE ONE**: a transcript
## opens each message with the line `-------------`. A markdown line that is
## the separator, after any backslashes, is written with one backslash
## more, and read back with one fewer, so no message's markdown is ever a
## separator on disk, and every markdown comes back exactly as written. A
## written body holding the bare separator is one no writer made, so the
## reader refuses it rather than accept a file it could never write back.
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

	## The markdown a transcript holds, as it was written, unless a line of
	## it is the bare separator, which `escape` never writes.
	unescape : Str -> Try(Str, [BareSeparator])
	unescape = |written| {
		lines = written.split_on("\n")
		if (lines.any(|l| l == Separator.line))
			Err(BareSeparator)
		else
			Ok(Str.join_with(lines.map(|l| if (is_separator_like(l)) l.drop_prefix("\\") else l), "\n"))
	}
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
expect Separator.unescape("a\n\\-------------\n\\\\-------------\nb") == Ok("a\n-------------\n\\-------------\nb")
# A lone backslash, or one before a near miss, is no escape.
expect Separator.unescape("\\\n\\------------") == Ok("\\\n\\------------")
# The bare separator refused, alone, last or first; escaped, or one dash
# short, kept.
expect Separator.unescape("-------------") == Err(BareSeparator)
expect Separator.unescape("a\n-------------") == Err(BareSeparator)
expect Separator.unescape("-------------\na") == Err(BareSeparator)
expect Separator.unescape("\\-------------") == Ok("-------------")
expect Separator.unescape("------------") == Ok("------------")
# Escaping, then unescaping, gives the markdown back, separators and all.
expect
	[
		"",
		"plain",
		"-------------",
		"\\-------------\n\\\\-------------",
		"a\n-------------\nMSG_x_2\nfrom: Steve",
	].all(|md| Separator.unescape(Separator.escape(md)) == Ok(md))
# No escaped line is the separator.
expect !Separator.escape("-------------\nx\n-------------").split_on("\n").any(|l| l == Separator.line)
```

### `app/Specs.roc`

```
## **THE SPECS' ROOT**: every `*Spec.roc`, imported so one `roc test` runs
## them all (`roc test app/Specs.roc --main=app/main.roc`, which the gate
## runs beside `roc test app/main.roc`). A Spec left out of this list never
## runs, so the gate checks that every `app/*Spec.roc` is imported here.
import ConversationSpec
import DirectorySpec
import DmSpec
import PageSpec
import SecureImageTagSpec
import TranscriptSpec

Specs :: [].{}
```

### `app/StrictName.roc`

```
## **A STRICT NAME**: one that becomes a file name and a URL, the one home
## of that rule, which a topic (`Topic`) and a channel's name
## (`ChannelName`) obey: ASCII letters, digits and `-`, starting with a
## letter, at most `longest` bytes. Opaque, so `from_str` is the only way
## in; no space, CR, LF, `/`, `.` or `_` ever reaches a path, a URL or a
## transcript's id line. With no `_` and a letter first, no strict name is
## ever a DM's (`7_11`), and a reference's `_`s (`MSG_<topic>_<n>`)
## are never a topic's.
import Ascii

StrictName :: Str.{

	## The strict name `name`, or the first reason, in this order, it is
	## refused.
	from_str : Str -> Try(StrictName, [Empty, StartsWithNonLetter, TooLong, ForbiddenByte])
	from_str = |name| {
		bytes = name.to_utf8()
		match bytes {
			[] => Err(Empty)
			[first, ..] if !Ascii.is_letter(first) => Err(StartsWithNonLetter)
			_ if bytes.len() > StrictName.longest => Err(TooLong)
			_ if !bytes.all(is_allowed) => Err(ForbiddenByte)
			_ => Ok(StrictName.(name))
		}
	}

	## The longest name, in bytes; every byte is ASCII, so in characters too.
	longest : U64
	longest = 60

	## The name, as a file name and a URL take it.
	to_str : StrictName -> Str
	to_str = |StrictName.(name)| name

	is_eq : _
	to_hash : _
}

is_allowed : U8 -> Bool
is_allowed = |b| Ascii.is_letter(b) or Ascii.is_digit(b) or b == '-'

# ── tests
expect StrictName.from_str("") == Err(Empty)
expect StrictName.from_str(" ") == Err(StartsWithNonLetter)
expect StrictName.from_str("\t") == Err(StartsWithNonLetter)
expect StrictName.from_str("\n") == Err(StartsWithNonLetter)
expect StrictName.from_str("\r") == Err(StartsWithNonLetter)
expect StrictName.from_str("1plans") == Err(StartsWithNonLetter)
expect StrictName.from_str("-plans") == Err(StartsWithNonLetter)
expect StrictName.from_str("_plans") == Err(StartsWithNonLetter)
# The bytes beside the letters' ranges, first.
expect StrictName.from_str("@a") == Err(StartsWithNonLetter)
expect StrictName.from_str("[a") == Err(StartsWithNonLetter)
expect StrictName.from_str("`a") == Err(StartsWithNonLetter)
expect StrictName.from_str("{a") == Err(StartsWithNonLetter)
# The bytes beside every allowed range, after the first.
expect StrictName.from_str("aAzZ09-").map_ok(StrictName.to_str) == Ok("aAzZ09-")
expect StrictName.from_str("a/") == Err(ForbiddenByte)
expect StrictName.from_str("a:") == Err(ForbiddenByte)
expect StrictName.from_str("a@") == Err(ForbiddenByte)
expect StrictName.from_str("a[") == Err(ForbiddenByte)
expect StrictName.from_str("a`") == Err(ForbiddenByte)
expect StrictName.from_str("a{") == Err(ForbiddenByte)
expect StrictName.from_str("a,") == Err(ForbiddenByte)
expect StrictName.from_str("a.") == Err(ForbiddenByte)
expect StrictName.from_str("plans\nnext") == Err(ForbiddenByte)
expect StrictName.from_str("plans\r") == Err(ForbiddenByte)
expect StrictName.from_str("plans ") == Err(ForbiddenByte)
expect StrictName.from_str("plans_2") == Err(ForbiddenByte)
expect StrictName.from_str("café") == Err(ForbiddenByte)
# The length at, under and over the longest.
expect StrictName.from_str("a".repeat(61)) == Err(TooLong)
expect StrictName.from_str("a".repeat(60)).map_ok(StrictName.to_str) == Ok("a".repeat(60))
expect StrictName.from_str("a".repeat(59)).map_ok(StrictName.to_str) == Ok("a".repeat(59))
expect StrictName.longest == 60
# The order of refusals: the first byte, then the length, then the bytes.
expect StrictName.from_str("1${"a".repeat(60)}") == Err(StartsWithNonLetter)
expect StrictName.from_str("a${"a".repeat(59)} ") == Err(TooLong)
expect StrictName.from_str("a b") == Err(ForbiddenByte)
expect StrictName.from_str("p").map_ok(StrictName.to_str) == Ok("p")
expect StrictName.from_str("Z").map_ok(StrictName.to_str) == Ok("Z")
expect StrictName.from_str("gopher-roc-2").map_ok(StrictName.to_str) == Ok("gopher-roc-2")
```

### `app/Topic.roc`

```
## **A TOPIC**: a conversation's name, which becomes a file name and a URL,
## so it is a strict name (`StrictName`, the one home of that rule). A
## topic is unique only within its channel or DM. Opaque, so `from_str` is
## the only way in, and a topic is never mistaken for a channel's name.
import StrictName

Topic :: StrictName.{

	## The topic named `name`, refused as `StrictName.from_str` refuses it.
	from_str : Str -> Try(Topic, [Empty, StartsWithNonLetter, TooLong, ForbiddenByte])
	from_str = |name| StrictName.from_str(name).map_ok(|strict| Topic.(strict))

	## The name, as a file name and a URL take it.
	to_str : Topic -> Str
	to_str = |Topic.(strict)| strict.to_str()

	is_eq : _
}

# ── tests
# Refused as a strict name is, by each of its refusals; kept as given.
expect
	[
		"",
		"1plans",
		"a".repeat(61),
		"plans_2",
	].map(Topic.from_str)
		== [
			Err(Empty),
			Err(StartsWithNonLetter),
			Err(TooLong),
			Err(ForbiddenByte),
		]
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
## (`Conversation.reference`), its author, its time, an empty line, its markdown
## and an empty line. A conversation with no messages is an empty file. No
## message's markdown can forge the start of another, and a body holding
## the bare separator, which no writer makes, is refused (Separator).
import Author
import Conversation
import Message
import Separator
import DateTime
import Topic

Transcript :: [].{

	## The transcript of the whole conversation.
	write : Conversation -> Str
	write = |conversation| Str.join_with(conversation.messages().map(|m| record(conversation, m)), "")

	## `topic`'s conversation, each message appended in turn, or the first
	## thing wrong with the transcript, as tags inferred from the body
	## (main's `Refusal` is the one list of them, and puts them in words).
	read : Topic, Str -> Try(Conversation, _)
	read = |topic, text|
		if (text.is_empty())
			Ok(Conversation.empty(topic))
		else if (!text.starts_with("${Separator.line}\n") or !text.ends_with("\n\n"))
			Err(BadEnds)
		else {
			records = text.drop_prefix("${Separator.line}\n").drop_suffix("\n\n").split_on("\n\n${Separator.line}\n")
			read_onto(Conversation.empty(topic), records)
		}
}

## One message as the transcript writes it.
record : Conversation, Message -> Str
record = |conversation, message|
	\\${Separator.line}
	\\${conversation.reference(message.id())}
	\\from: ${message.author().to_str()}
	\\date: ${message.time().to_str()}
	\\
	\\${Separator.escape(message.markdown())}
	\\
	\\

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
	reference = c.reference(id)
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
			time = DateTime.from_str(date).map_err(|why| DateTime(id, why))?
			markdown = Separator.unescape(Str.join_with(body, "\n")).map_err(|BareSeparator| BadBody(id))?
			grown = c.append({ payload: { author, markdown }, time }).map_err(
				|why|
					match why {
						Full => Full
						Backdated => Backdated(id)
					},
			)?
			Ok(grown.conversation)
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
import Message
import Sample
import Transcript

TranscriptSpec :: [].{}

## **A RECORD'S LINES, AS A TEST WRITES THEM**: its head, its `from:` and
## `date:` lines, `gap`, the empty line after them, or not, and its body as
## written on disk.
Lines : {
	head : Str,
	from : Str,
	date : Str,
	gap : Str,
	body : Str,
}

## A record with its lines as given.
record : Lines -> Str
record = |
	{
		head,
		from,
		date,
		gap,
		body,
	},
| "-------------\n${head}\n${from}\n${date}\n${gap}${body}\n\n"

## Message 1's lines, written well.
first : Lines
first = {
	head: "MSG_plans_1",
	from: "from: Steve",
	date: "date: 2026-11-02T19:11:32Z",
	gap: "\n",
	body: "hi",
}

## Message 2's lines, written well.
second : Lines
second = {
	head: "MSG_plans_2",
	from: "from: CC",
	date: "date: 2026-11-02T19:12:28Z",
	gap: "\n",
	body: "hi",
}

## The transcript holding only message 1 as `lines` write it.
one_with = |lines| Transcript.read(Sample.plans, record(lines))

## The transcript holding message 1, written well, then message 2 as
## `lines` write it.
two_with = |lines| Transcript.read(Sample.plans, "${record(first)}${record(lines)}")

## Message 3's lines, written well.
third : Lines
third = {
	head: "MSG_plans_3",
	from: "from: Steve",
	date: "date: 2026-11-02T19:13:05Z",
	gap: "\n",
	body: "hi",
}

## The transcript holding messages 1 and 2, written well, then message 3
## as `lines` write it.
three_with = |lines| Transcript.read(Sample.plans, "${record(first)}${record(second)}${record(lines)}")

## Read, then written again: the text itself, when it is accepted.
again = |text| Transcript.read(Sample.plans, text).map_ok(Transcript.write)

## Is `text` read, and written again, exactly as it is?
is_round_trip : Str -> Bool
is_round_trip = |text| again(text) == Ok(text)

# Written exactly, both ways.
expect Transcript.write(Sample.two) == "-------------\nMSG_plans_1\nfrom: Steve\ndate: 2026-11-02T19:11:32Z\n\nHello\n\n-------------\nMSG_plans_2\nfrom: CC\ndate: 2026-11-02T19:12:28Z\n\nHi!\n\n- one\n- two\n\n"
expect Transcript.read(Sample.plans, Transcript.write(Sample.two)) == Ok(Sample.two)
# No messages: an empty file, both ways.
expect Transcript.write(Conversation.empty(Sample.plans)) == ""
expect Transcript.read(Sample.plans, "") == Ok(Conversation.empty(Sample.plans))
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
expect one_with({ ..first, from: "from: " }) == Err(Author(Sample.first, Empty))
expect one_with({ ..first, from: "from:  " }) == Err(Author(Sample.first, BadSpacing))
expect one_with({ ..first, from: "from: Steve\r" }) == Err(Author(Sample.first, ForbiddenCharacter))
expect one_with({ ..first, from: "from:  Steve" }) == Err(Author(Sample.first, BadSpacing))
expect one_with({
	..first,
	from: "from: Ste\u(202e)ve",
}) == Err(Author(Sample.first, ForbiddenCharacter))
expect one_with({ ..first, date: "date: 2026-11-02" }) == Err(DateTime(Sample.first, WrongShape))
expect one_with({
	..first,
	date: "date: 2026-13-02T19:11:32Z",
}) == Err(DateTime(Sample.first, OutOfRange))
# A body line that is the bare separator, which no writer makes, beside
# the escaped one a writer does.
expect one_with({ ..first, body: "a\n-------------" }) == Err(BadBody(Sample.first))
# A bare separator right after a blank line ends the record there, so
# what follows it is the next message's head, which is no reference: that
# message is refused as `BadHead`. Escaped, it is the body's own line.
expect one_with({ ..first, body: "a\n\n-------------\nb" }) == Err(BadHead(Sample.second))
expect is_round_trip(record({ ..first, body: "a\n\n\\-------------\nb" }))
expect again(record({ ..first, body: "a\n\\-------------" })) == Ok(record({ ..first, body: "a\n\\-------------" }))
# The same at message 2, after a good message 1.
expect again("${record(first)}${record(second)}") == Ok("${record(first)}${record(second)}")
expect two_with({ ..second, head: "MSG_plans_1" }) == Err(BadHead(Sample.second))
expect two_with({ ..second, head: "MSG_plans_3" }) == Err(BadHead(Sample.second))
expect two_with({ ..second, from: "frm: CC" }) == Err(BadHead(Sample.second))
expect two_with({ ..second, date: "dt: 2026-11-02T19:12:28Z" }) == Err(BadHead(Sample.second))
expect two_with({ ..second, gap: "" }) == Err(BadHead(Sample.second))
expect two_with({ ..second, from: "from: " }) == Err(Author(Sample.second, Empty))
expect two_with({ ..second, from: "from: C\u(0)C" }) == Err(Author(Sample.second, ForbiddenCharacter))
expect two_with({ ..second, from: "from: CC " }) == Err(Author(Sample.second, BadSpacing))
expect two_with({
	..second,
	date: "date: 2026-11-02T19:12:28",
}) == Err(DateTime(Sample.second, WrongShape))
expect two_with({
	..second,
	date: "date: 2026-02-29T19:12:28Z",
}) == Err(DateTime(Sample.second, OutOfRange))
expect two_with({ ..second, body: "a\n-------------" }) == Err(BadBody(Sample.second))
expect two_with({ ..second, body: "a\n\n-------------\nb" }) == Err(BadHead(Sample.third))
expect
	again("${record(first)}${record({ ..second, body: "a\n\\-------------" })}")
		== Ok("${record(first)}${record({ ..second, body: "a\n\\-------------" })}")
# Times never go backwards: message 2 and message 3 at the time above
# them, or a second later, read; a second earlier is refused by its id.
expect is_round_trip("${record(first)}${record({ ..second, date: "date: 2026-11-02T19:11:32Z" })}")
expect is_round_trip("${record(first)}${record({ ..second, date: "date: 2026-11-02T19:11:33Z" })}")
expect two_with({ ..second, date: "date: 2026-11-02T19:11:31Z" }) == Err(Backdated(Sample.second))
expect is_round_trip("${record(first)}${record(second)}${record({ ..third, date: "date: 2026-11-02T19:12:28Z" })}")
expect is_round_trip("${record(first)}${record(second)}${record({ ..third, date: "date: 2026-11-02T19:12:29Z" })}")
expect three_with({ ..third, date: "date: 2026-11-02T19:12:27Z" }) == Err(Backdated(Sample.third))
# Another topic's transcript is refused by its references.
expect Transcript.read(Sample.other, Transcript.write(Sample.two)) == Err(BadHead(Sample.first))
# A body that holds the separator, or a backslash before it, is written
# with one backslash more, and comes back whole.
forged : Conversation
forged = Sample.conversation(
	Sample.plans,
	[
		Sample.arrival({
			author: "Mallory",
			time: "2026-11-02T19:11:32Z",
			markdown: "a\n-------------\nMSG_plans_2\nfrom: Steve",
		}),
		Sample.arrival({
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
		Sample.arrival({
			author: "Steve",
			time: "2026-11-02T19:11:32Z",
			markdown: "a-------------\n-------------x\n\\x\n------------",
		}),
	],
)
expect Transcript.write(near) == "-------------\nMSG_plans_1\nfrom: Steve\ndate: 2026-11-02T19:11:32Z\n\na-------------\n-------------x\n\\x\n------------\n\n"
expect Transcript.read(Sample.plans, Transcript.write(near)) == Ok(near)
# Markdown that is empty, or ends in one or two newlines, comes back
# exactly; the empty one's record is written byte for byte.
edges : List(Str)
edges = [
	"",
	"\n",
	"\n\n",
	"a\n",
	"a\n\n",
]

## Steve's message saying `markdown`.
said : Str -> Message.Arrival
said = |markdown|
	Sample.arrival({
		author: "Steve",
		time: "2026-11-02T19:11:32Z",
		markdown,
	})

edged : Conversation
edged = Sample.conversation(Sample.plans, edges.map(said))

expect edged.messages().map(Message.markdown) == edges
expect Transcript.read(Sample.plans, Transcript.write(edged)) == Ok(edged)
expect
	Transcript.write(Sample.conversation(Sample.plans, [said("")]))
		== "-------------\nMSG_plans_1\nfrom: Steve\ndate: 2026-11-02T19:11:32Z\n\n\n\n"
# The reader at and over the most, in one read: a full conversation's
# transcript and one record more is refused as `Full`, which the reader
# reaches only at the 65,536th record, after reading the 65,535 before it.
expect {
	full = Sample.almost_full.append(Sample.reply).map_ok(|grown| grown.conversation) ?? crash "TranscriptSpec: the 65,535th message fits"
	over = "${Transcript.write(full)}-------------\nMSG_plans_65536\nfrom: CC\ndate: 2026-11-02T19:12:28Z\n\nHi!\n\n"
	Transcript.read(Sample.plans, over) == Err(Full)
}
```

### `app/TrustedHtml.roc`

```
## **MARKUP SOME CODE HAS VOUCHED FOR**: a `TrustedHtml` is a string that
## code in this program has decided is ready to deliver as HTML. A `Str` is
## text, never markup. The type says which a value is, so text can't reach
## a page unescaped, and markup can't be escaped a second time.
##
## **THE ONE DOOR IS `dangerously_trust`, AND ITS CALLERS ARE THE AUDIT**,
## named to be seen at every call: each
## vouches only for HTML it built or escaped itself. They are few, and
## each is small: `Escape.text` (text, escaped), `HtmlElement.tag` (an
## element's tags, from closed sets and strict tokens), `Markdown.render`
## (roc-markdown's output, whose images `SecureImageTag` rules: the other
## trust boundary a security reader wants), and
## `Page`'s fixed head and style sheet. `join` builds only from what is
## already vouched for, so it vouches for nothing new.
##
## **THE OTHER TRUST BOUNDARIES**: `UnvalidatedString`, the way text from
## outside comes in, and `SecureImageTag`, which images a message may show.
##
## **THE WAY OUT IS BYTES**: `to_utf8`, for the host. There is no way back
## to a `Str`, so trusted markup can't be handed to `Escape.text` and
## escaped again without a deliberate, fallible `Str.from_utf8`.
TrustedHtml :: Str.{

	## **THE DOOR, AND IT IS DANGEROUS**: `html`, delivered as it is, with
	## nothing escaped. The caller promises that its own code built or
	## escaped every byte of `html`, so no text a person, an agent or a file
	## supplied is in it unescaped. A wrong promise is an injection.
	dangerously_trust : Str -> TrustedHtml
	dangerously_trust = |html| TrustedHtml.(html)

	## The pieces, in order, each as it is.
	join : List(TrustedHtml) -> TrustedHtml
	join = |pieces| TrustedHtml.(Str.join_with(pieces.map(|TrustedHtml.(html)| html), ""))

	## The page's bytes, for the host: the one way out.
	to_utf8 : TrustedHtml -> List(U8)
	to_utf8 = |TrustedHtml.(html)| html.to_utf8()
}

# ── tests
expect TrustedHtml.dangerously_trust("<p>é</p>").to_utf8() == "<p>é</p>".to_utf8()
# Joined in order, each piece as it is, with nothing between them.
expect
	TrustedHtml.join([
		TrustedHtml.dangerously_trust("<p>"),
		TrustedHtml.dangerously_trust("&amp;"),
		TrustedHtml.dangerously_trust("</p>"),
	]).to_utf8()
		== "<p>&amp;</p>".to_utf8()
expect TrustedHtml.join([]).to_utf8() == []
```

### `app/UnvalidatedString.roc`

```
## **TEXT FROM THE WIRE, NOT YET CHECKED**: whatever arrives from outside
## (a request, a file the host read) is an `UnvalidatedString` until a
## checking door says what it is. Opaque, with one way in, `from_utf8`, at
## main's door, and no way back to a `Str`: the only ways out are the
## checking doors below, each giving a checked type or a refusal's tags.
## So no `Name`, `Topic`, `DateTime` or `Conversation` is ever built from
## outside text that skipped its check.
##
## **ONE OF THE TRUST BOUNDARIES**: this is the way in; `TrustedHtml` is
## the way out to a page, and `SecureImageTag` rules which images a
## message may show. A security reader starts at any of the three.
import Conversation
import DateTime
import Name
import Topic
import Transcript

UnvalidatedString :: Str.{

	## **THE WAY IN**: the host's `bytes`, unless they are not UTF-8.
	from_utf8 : List(U8) -> Try(UnvalidatedString, [NotUtf8])
	from_utf8 = |bytes|
		match Str.from_utf8(bytes) {
			Ok(text) => Ok(UnvalidatedString.(text))
			Err(_) => Err(NotUtf8)
		}

	## The permanent name it spells, checked by `Name.from_str`.
	name : UnvalidatedString -> Try(Name, [Empty, ForbiddenCharacter, BadSpacing])
	name = |UnvalidatedString.(text)| Name.from_str(text)

	## The topic it names, checked by `Topic.from_str`.
	topic : UnvalidatedString -> Try(Topic, [Empty, StartsWithNonLetter, TooLong, ForbiddenByte])
	topic = |UnvalidatedString.(text)| Topic.from_str(text)

	## The time it writes, checked by `DateTime.from_str`.
	date_time : UnvalidatedString -> Try(DateTime, [WrongShape, OutOfRange])
	date_time = |UnvalidatedString.(text)| DateTime.from_str(text)

	## The conversation under `named`, as the transcript it is, checked by
	## `Transcript.read`, its refusals as that reader names them.
	conversation : UnvalidatedString, Topic -> Try(Conversation, _)
	conversation = |UnvalidatedString.(text), named| Transcript.read(named, text)
}

# ── tests
## The text `bytes` hold, from the wire, which a test's always are.
wire : List(U8) -> UnvalidatedString
wire = |bytes| UnvalidatedString.from_utf8(bytes) ?? crash "UnvalidatedString's tests: a test's bytes are UTF-8"

# Only UTF-8 comes in: a stray byte, and a character cut short, refused.
## Whether `bytes` come in, or why not.
comes_in : List(U8) -> Try({}, [NotUtf8])
comes_in = |bytes| UnvalidatedString.from_utf8(bytes).map_ok(|_| {})

expect [
	[0xFF],
	[0xC3],
	"Zoë".to_utf8(),
	[],
].map(comes_in) == [
	Err(NotUtf8),
	Err(NotUtf8),
	Ok({}),
	Ok({}),
]
# Each way out checks, both sides.
expect wire("Zoë".to_utf8()).name().map_ok(Name.to_str) == Ok("Zoë")
expect wire("Zoë!".to_utf8()).name() == Err(ForbiddenCharacter)
expect wire("plans".to_utf8()).topic().map_ok(Topic.to_str) == Ok("plans")
expect wire("plans_2".to_utf8()).topic() == Err(ForbiddenByte)
expect wire("2026-11-02T19:11:32Z".to_utf8()).date_time().map_ok(DateTime.to_str) == Ok("2026-11-02T19:11:32Z")
expect wire("2026-11-02".to_utf8()).date_time() == Err(WrongShape)
expect {
	plans = Topic.from_str("plans") ?? crash "UnvalidatedString's tests: a topic"
	[wire([]).conversation(plans), wire("\n".to_utf8()).conversation(plans)]
		== [Ok(Conversation.empty(plans)), Err(BadEnds)]
}
```

### `app/UserId.roc`

```
## **A USER'S ID**: a human's or an agent's number, unique and permanent,
## handy in a URL and in a file's name (`UserStem`). Steve is always 1.
##
## **ONE COUNT FOR HUMANS AND AGENTS**, as they share one namespace: an id
## alone says who, with no kind beside it to keep in step, and `apoorva-2`
## and an agent's `cc-3` are never the same number.
##
## **WHY U8**: the chat is a small group of humans and their agents, and
## 255 is many times that. Every id that lasts is written as its decimal
## digits (a file's name, a URL, a DM's name), so a wider type later moves
## no byte on disk.
UserId :: U8.{

	## Steve's id, always: the first user, and the admin (`Admin`).
	steve : UserId
	steve = UserId.(1)

	## The id after this one, unless this is the last a chat holds.
	next : UserId -> Try(UserId, [Full])
	next = |UserId.(n)| if (n == U8.highest) Err(Full) else Ok(UserId.(n + 1))

	## The number, as a URL, a file's name and a DM's name write it.
	to_str : UserId -> Str
	to_str = |UserId.(n)| n.to_str()

	## **WHICH COMES FIRST**, by number: a DM's pair and a channel's
	## members are written in this order.
	compare : UserId, UserId -> [Before, Same, After]
	compare = |
		UserId.(n),
		UserId.(other),
	| if (n < other) Before else if (n == other) Same else After

	is_eq : _
	to_hash : _
}

# ── tests
expect UserId.steve.to_str() == "1"
expect UserId.steve.next().map_ok(UserId.to_str) == Ok("2")
# The last id at, under and over the highest.
expect UserId.(254).next().map_ok(UserId.to_str) == Ok("255")
expect UserId.(255).next() == Err(Full)
# The order, both ways round, and the same id.
expect
	[
		UserId.steve.compare(UserId.(2)),
		UserId.(2).compare(UserId.steve),
		UserId.(2).compare(UserId.(2)),
		UserId.(9).compare(UserId.(10)),
	]
		== [Before, After, Same, Before]
```

### `app/UserStem.roc`

```
## **A USER'S FILE STEM**: `apoorva-2`, from a user's name and id, the one
## home of that spelling. A user's files are named from it
## (`apoorva-2.info`); what each holds is not decided here.
##
## **STRICT, SO SAFE AS A FILE'S NAME AND IN A URL**: each word of the name
## (`Name`: letters, single spaces between words) as its ASCII letters in
## lower case, its accented letters left out, the words joined by `-`; then
## `-` and the id. A word with no ASCII letter is left out, and a name with
## none is the id alone. The id makes a stem unique, so the name's part is
## only for a reader finding the file.
import Ascii
import Name
import UserId

UserStem :: [].{

	## The stem of the user `id`, named `name`.
	of : { name : Name, id : UserId } -> Str
	of = |{ name, id }| {
		words = name.to_str().with_ascii_lowercased().split_on(" ").map(ascii_only).drop_if(Str.is_empty)
		if (words.is_empty()) id.to_str() else "${Str.join_with(words, "-")}-${id.to_str()}"
	}
}

## `word`'s ASCII letters, in order.
ascii_only : Str -> Str
ascii_only = |word|
	Str.from_utf8(word.to_utf8().keep_if(Ascii.is_letter)) ?? crash "UserStem.ascii_only: ASCII letters are UTF-8"

# ── tests
## The stem of `text`'s user, whose id is the one after `count` others'.
stem : Str, U64 -> Str
stem = |text, count| {
	name = Name.from_str(text) ?? crash "UserStem's tests: a test's name is a name"
	id = List.repeat({}, count).fold(
		UserId.steve,
		|at, {}| at.next() ?? crash "UserStem's tests: a test's id fits",
	)
	UserStem.of({ name, id })
}

expect stem("Steve", 0) == "steve-1"
expect stem("apoorva", 1) == "apoorva-2"
expect stem("Steve Howell", 0) == "steve-howell-1"
expect stem("CC", 2) == "cc-3"
# Accented letters left out, and a word left with none.
expect stem("Zoë Ann", 3) == "zo-ann-4"
expect stem("Élodie", 4) == "lodie-5"
expect stem("Zoë Ő Ann", 5) == "zo-ann-6"
# No ASCII letter at all: the id alone, at the first id and the last.
expect stem("Éé", 0) == "1"
expect stem("Ő Ű", 254) == "255"
expect stem("Zoë", 254) == "zo-255"
```

### `app/main.roc`

```
## **THE DEMO**: a topic's name and its transcript in, its page out. The
## host (host/main.zig) reads the file and writes the page; everything
## else is the pure core. The door: the host's bytes become unchecked text
## (`UnvalidatedString`), then a Conversation or a refusal's tags, here,
## and only here are the tags put into words.
app [page] {
	md: "../../roc-markdown/package/main.roc",
	pf: platform "../platform/main.roc",
}

import Conversation
import Message
import Page
import StrictName
import Topic
import UnvalidatedString

## The page for `topic`'s transcript, or a page saying what is wrong with it.
page : List(U8), List(U8) -> List(U8)
page = |topic, transcript| {
	answer =
		match conversation({ topic, transcript }) {
			Ok(c) => Page.conversation(c)
			Err(why) => Page.refused(words(why))
		}
	answer.to_utf8()
}

## The conversation the host's bytes hold, decoded at the door.
conversation : { topic : List(U8), transcript : List(U8) } -> Try(Conversation, _)
conversation = |{ topic, transcript }| {
	name = UnvalidatedString.from_utf8(topic) ? |NotUtf8| TopicNotUtf8
	text = UnvalidatedString.from_utf8(transcript) ? |NotUtf8| TranscriptNotUtf8
	checked = name.topic() ? |why| Topic(why)
	text.conversation(checked).map_err(|why| Transcript(why))
}

## **EVERY WAY THE DOOR REFUSES**: what `words` takes, each module's tags
## under the step that met them. A handler's input, so `conversation`'s
## own error stays inferred from its body.
Refusal : [
	TopicNotUtf8,
	TranscriptNotUtf8,
	Topic([Empty, StartsWithNonLetter, TooLong, ForbiddenByte]),
	Transcript(
		[
			BadEnds,
			BadHead(Message.Id),
			Author(Message.Id, [Empty, ForbiddenCharacter, BadSpacing]),
			DateTime(Message.Id, [WrongShape, OutOfRange]),
			BadBody(Message.Id),
			Backdated(Message.Id),
			Full,
		],
	),
]

## **WHY A TRANSCRIPT IS REFUSED, IN WORDS**: the one place a refusal's
## tags become a sentence.
words : Refusal -> Str
words = |why|
	match why {
		TopicNotUtf8 => "its topic is not UTF-8"
		TranscriptNotUtf8 => "it is not UTF-8"
		Topic(Empty) => "its topic is empty"
		Topic(StartsWithNonLetter) => "its topic does not start with an ASCII letter"
		Topic(TooLong) => "its topic is longer than ${StrictName.longest.to_str()} characters"
		Topic(ForbiddenByte) => "its topic holds more than ASCII letters, digits and -"
		Transcript(BadEnds) => "a transcript starts with the separator and ends with an empty line"
		Transcript(Full) => "it holds more messages than a conversation can"
		Transcript(BadHead(id)) => "message ${id.to_str()} does not open with its reference, `from:`, `date:` and an empty line"
		Transcript(BadBody(id)) => "message ${id.to_str()} holds the separator, unescaped, on a line of its own"
		Transcript(Backdated(id)) => "message ${id.to_str()} is dated before the message above it"
		Transcript(Author(id, fault)) => {
			said =
				match fault {
					Empty => " has no author"
					ForbiddenCharacter => "'s author holds a character that is no letter or space"
					BadSpacing => "'s author has a space at either end, or two together"
				}
			"message ${id.to_str()}${said}"
		}
		Transcript(DateTime(id, fault)) => {
			said =
				match fault {
					WrongShape => "is not YYYY-MM-DDTHH:MM:SSZ"
					OutOfRange => "is no time a calendar and clock show"
				}
			"message ${id.to_str()}'s date ${said}"
		}
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
) == Page.conversation(Conversation.empty(plans)).to_utf8()
expect page("<b>".to_utf8(), [0xff]) == Page.refused("it is not UTF-8").to_utf8()
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
		Transcript(Author(second, Empty)),
		Transcript(Author(second, ForbiddenCharacter)),
		Transcript(Author(second, BadSpacing)),
		Transcript(DateTime(second, WrongShape)),
		Transcript(DateTime(second, OutOfRange)),
		Transcript(BadBody(second)),
		Transcript(Backdated(second)),
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
			"message 2's author holds a character that is no letter or space",
			"message 2's author has a space at either end, or two together",
			"message 2's date is not YYYY-MM-DDTHH:MM:SSZ",
			"message 2's date is no time a calendar and clock show",
			"message 2 holds the separator, unescaped, on a line of its own",
			"message 2 is dated before the message above it",
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
/// by the pinned Roc (roc-version), linked into host/main.zig. The tests
/// are the gate's alone (tools/verify.shale), the one list of their roots.
///
///   zig build demo -- <topic> <file>     a transcript's page, to stdout
pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const roc = rocCompiler(b);

    const archive = b.addSystemCommand(&.{ roc, "build", "app/main.roc", "--target=x64musl", "--opt=dev" });
    archive.setCwd(b.path("."));
    for ([_][]const u8{ "app", "platform", markdown_package }) |folder| rocInputs(b, archive, folder);
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
}

/// **THE MARKDOWN PACKAGE app/main.roc IMPORTS** (`md`), roc-markdown
/// checked out beside this repo, from the build's root.
const markdown_package = "../roc-markdown/package";

/// **EVERY ROC MODULE IS AN INPUT, FOUND, NEVER LISTED**: each `.roc` in
/// `folder`, so a change to any module, ours or the markdown package's,
/// builds the archive again.
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

One call per message into roc-markdown, through `Markdown`:

```roc
Markdown.render(m.markdown())
```

The page is structure and class names; a client styles it. 🎉

~~~~

