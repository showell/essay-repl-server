# The essay surface, Thursday

Thursday's agent planted one fault in every stage of the full check, watched each one go red, and took it out again. Friday's agent is now at work on the release script.

## The plants found a security hole

A commenter's name went onto the page unescaped. Markup typed into the name field would have run in every reader's page, and all six stages passed it. The planted fault meant to test escaping showed that nothing tested names. `TestEveryCommentFieldEscaped` now covers all five fields the page shows, and it goes red when that fault goes back in.

That's the case for planting faults, made by the week itself. Wednesday's plant found a test whose panic hid twelve others. Thursday's found a hole no test covered.

**Your dogfood server still has that hole,** until Friday's release replaces it. It's reachable only through your tunnel, so you're the only one who can post. I'm leaving it for the real release, which is the Friday story, unless you want it swapped sooner.

## Which stages saw their faults

Every stage caught its planted fault. Fast's unit tests also caught the anchoring, audit and dates plants on their own, but only the full stages showed which real notes were affected. The race detector, the bench and the smoke test caught faults that fast passed. That's the reason the full check exists.

## Reply buttons, checked without a browser

`buttons_test.go` works out the CSS cascade by hand, on the stylesheet the page is actually served with. It checks every place the JavaScript puts a button, at every desktop width the media queries name, in light and dark. `display:none`, `visibility:hidden` or opacity under 0.5 fails the test, and CSS it can't judge stops it. Tuesday's `opacity:0`, put back in, turned it red.

It's honest about its limits: it doesn't run the JavaScript, see clipping or judge contrast, and its header says so. The buttons' 0.6 grey is faint. **Do you want a contrast floor**, or is faint right for a reply button?

## The fixtures kept, and what they cost

Each is data a check reads, with no build of its own:

| Fixtures | What they hold | Cost |
|---|---|---|
| `testdata/buttons/` | five known-bad stylesheets (Tuesday's real one among them), two known-good | 0.02 s inside `go test` |
| `testdata/audit/` | a known-bad page and a known-good one, read before any server starts | under 5 ms each |
| `testdata/fast/go-test-v.txt` | a `go test` output with a failure and a panic | 3 ms |

The ones not kept needed a build of their own (race, bench, dates) or would have needed a blanket exclusion (gofmt, vet). The journal says why for each. Your rule held: fixtures are data, and the cost of each is in the table.

## Your two additions

- **The comments folder:** at start, a missing parent stops the server with one message naming the path, and nothing is created. It has a test and a planted fault.
- **Phones:** the README now says "Phones are out of scope: the pages are made for, and checked in, a desktop browser." The by-hand list is down to one item, the desktop eye test.

## The time

`full.shale` went from 30.9 s to 23.3 s of wall time. Today's additions cost tens of milliseconds. The gain came from a quieter box and from the `git gc` you approved. The anchoring simulation is still 10 to 13 s of it.

## One slip

One planted fault's launch stopped after the fault went in and before it came out. The agent restored the file at once and ran every later plant under `shale --undo-on-stop`. That's the right habit, and it's worth one paragraph in the book.
