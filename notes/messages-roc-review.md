# Messages.roc: a cold review

A cold agent read `app/Messages.roc` and everything it overlaps with. It got the code and your questions, but not my view. Below is its report, lightly trimmed. The one finding I checked myself is marked **[checked]**. I haven't verified the rest line by line.

## Verdict

`Messages.roc` has no subject. Its header says it is "what every topic's routes share", which describes who calls it, not what it is. It holds six unrelated things:

- the JSON shape of a message;
- the page-size arithmetic;
- the agent hop limit, with its HTTP 429;
- the agent stream's bus key, events and resume backlog;
- a stream-holder helper that has nothing to do with messages;
- tests that belong to Render and Uploads.

`Topics.roc` re-implements half of it. Most functions are correct one at a time. The real fault is that the chat's core nouns have no types: message, message id, page, tally, the stream's lead. So code lands wherever its caller happened to be, and crashes stand in for the missing types.

## Your questions

- **Why plural?** In this repo a plural module means routes beside a singular noun (`Topics`/`Topic`, `Channels`/`Channel`). `Messages` is neither, and it holds no messages; `Transcript` does. It should be a singular `Message`.
- **`json_led`?** That names a mechanism: the JSON is "led" by an untyped list of pairs that callers build by hand. There are really two leads: the ref alone, or channel, topic and ref. → `Message.json(message, { ref, heading : [Ref, ChannelTopicRef] }, roster)`. A second `message_json` has no production caller, and `Topics.roc` defines a different function with the same name.
- **`message_most`?** `Limits.roc` calls itself the one home of the numbers. This is the only size cap kept outside it, and its name doesn't say the unit. → `Limits.message_bytes_most`, beside `transcript_bytes_most`.
- **`page_of` not a method?** It takes a bare count. "Empty" is a sentinel (`{first:1, last:0}`) rather than a tag, `Before(900)` silently clamps, and three callers recompute "is there an earlier page" as `first > 1`. → a nominal `Transcript.Tally` with `.page(Newest | Before(MessageId))` and `.next_id()`, and a `Page` type with `.has_earlier()` whose empty case is a tag.
- **`first`/`last` as U64?** That type gap produced the crash below. → a `MessageId` whose constructor refuses 0.
- **`check_hops!` in messages?** Its rule is split across three modules: Mentions has `own_hops` and `is_hop`, this module has the effect and the refusal, and Limits has the numbers. It counts only the newest *page*, so changing the UI page size silently changes a rate limit. → a module named for the rule, `AgentHops`, that reads its own window. `Topics.store_post!` would call it right after `Topic.post`.
- **The agent stream, "plopped"?** Yes. It is spread across four modules:
  - `Messages.roc` has `Source`, the bus key, the event and the backlog;
  - `AgentStream.roc` has the pure rules;
  - `OneStream.roc` has the route;
  - `Topics.roc` builds the sources and fans out posts.

  There are two builders for the `message` event, two gap frames and two resume rules. On a frame that fails, the backlog silently drops the message (`keep_oks`) while publish crashes: opposite policies for the same case. → one `AgentStream` module that owns all of it, with one frame that cannot fail.

## The crash **[checked, fixed]**

`GET /chat/{channel|dm}/…/earlier?before=0` passed the parse (`Stored.count` accepts `0`), and then `page_of` computed `0 - 1` on a U64. The Roc panicked on that request ("Integer subtraction overflowed"); the server survived. Any signed-in reader of a topic could trigger it. The JSON route already refused 0; the page's route didn't, and the e2e test didn't try 0. I added `?before=0` to the e2e test, saw it go red, and guarded the route; it deploys with the next deploy. The fix by construction is the `MessageId` type.

## Proposed layout

| Noun | Module | Holds |
|---|---|---|
| message | `Message.roc` (new) | `Message` (opaque), `MessageId` (refuses 0), `Message.json` |
| transcript | `Transcript.roc` | the line format; `Tally` (nominal) with `.page()`, `.next_id()`; `Page` with `.has_earlier()` and an `Empty` tag |
| a topic's members by name | `Topics.roc` | `Roster` (was `Messages.Who`, which collided with `Viewer.who()`) |
| agent hop limit | `AgentHops.roc` (new) | `room!`, `refused`, `own_hops`, `is_hop` |
| mentions | `Mentions.roc` | `of`, `of_post`, `Named` only |
| agent stream | `AgentStream.roc` | `Source`, `bus_key`, `event`, `backlog!`, `sources!`, `publish!`, and its rules |
| stream frames | `PageFeed`/`Sse` | one gap frame; one JSON frame that cannot fail |
| stream holder | `Account.roc` | `stream_holder(Principal.Bound)`, no crash on SignedOut |
| numbers | `Limits.roc` | `message_bytes_most` |

`Messages.roc` then ends up empty and is deleted. Leftovers: unused `import Messages` in `Home`, `HumanInvites` and `Pages`; a doc comment citing `Messages.post!`, which doesn't exist.

## Sound, or confused?

Function by function, mostly sound:

- the transcript's line format has one spelling and exhaustive round trips;
- `AgentStream`'s resume ordering is careful and tested on both sides;
- `page_of`'s arithmetic is tested at its boundaries.

The structure is what's confused, and renaming alone won't fix it. Crashes stand in for missing types (`Transcript.roc:45`, `Store.roc:525`, `Messages.roc:271`, and the underflow above). Duplicated logic follows opposite failure policies. A rate limit depends on a UI page size. Code is placed by caller, not subject: `Topics.roc` is 1,188 lines of routes, JSON, stream fan-out and Recent publishing. So this is a pattern across the codebase, not one bad file.

The reviewer's judgment: don't start over because of this module. A rename-and-move pass isn't enough either. The fix is a deliberate refactor that introduces about five nominal types (`Message`, `MessageId`, `Transcript.Tally`, `Transcript.Page`, `Roster`) and lets the functions follow their types. Once those types exist, about half the findings go away by construction. If the same caller-driven placement in `Topics.roc` and `TopicPage.roc` makes that refactor look bigger than a rewrite, that's the honest case for starting over. The case would not be that the logic is wrong. It would be that the code never named its nouns.
