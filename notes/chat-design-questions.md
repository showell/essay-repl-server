# Chat design questions from the sweep

*2026-11-05. The cold agent that ran Shale's recipes over the chat code left seven items for you. One has already been settled, so six need an answer. Each has my pick first. The code calls this project gopher-roc until the rename lands.*

Everything here is about reading quality. Nothing is broken, and every check passes today.

## 1. Six type names that appear in two modules

`Addition`, `Admission`, `Admitted`, `Claim`, `Created` and `NewHuman` are each declared in more than one module. The recipe holds this count at 6 rather than zero, because each case is a design question and not something a tool can settle.

The clearest case is `Claim`. `GitHubSignUp.Claim` and `GitHubState.Claim` are the same shape, `{ payload : Str, mac : List(U8) }`, and `Session.Claim` is a third one, with fields I haven't compared.

- **A (my pick):** have an agent go through all six. Any two that are really the same thing share one module, and any that only look alike keep their two-part names and get recorded as fine.
- **B:** fix only the `Claim` pair now and leave the rest.
- **C:** leave them all. Two-part names like `GitHubState.Claim` read fine as they are.

## 2. Nesting depth

Calls nested four deep are held at zero. Three deep, like `f(g(h(x)))`, has 51 findings. Each fix needs a named step in the middle, which is sometimes clearer and sometimes just longer.

- **A (my pick):** leave the rule at four, and fix a three-deep call only when someone is already reading that code.
- **B:** sweep all 51 and hold three at zero.

## 3. How an `if` hangs off a lambda

`roc fmt` allows `|x| if … {` on one line, and 17 places or fewer in the chat use that form. Safari nearly always puts the body on its own line, 32 to 3.

- **A (my pick):** match safari: the `if` starts its own line, and a recipe holds it.
- **B:** allow both.

## 4. `now : I64`

The time is a bare `I64` in all 59 places it appears, and `expires` and `created` are too in places. The style guide says to give each domain number a nominal type, and safari just went through this for its own time.

- **A (my pick):** add a `Timestamp` type, in the same way safari did its units. This touches types across the app, so it's a real stage, but it's the kind of bug-preventing change you've wanted elsewhere: seconds and milliseconds couldn't mix.
- **B:** only `expires` and `created`, for now.
- **C:** leave it. It's a chat, and the times are simple.

## 5. The host's GitHub `id : U64`

`github_id` would read better than `id`, but this field crosses the platform seam, so the change reaches into the Zig host.

- **A (my pick):** rename it, since the rename is touching this seam's names anyway.
- **B:** leave it. It's clear enough in context.

## 6. `unauthorized_refusal`

The agent renamed a function to this while clearing a lint, and flagged the choice because the name took some judgment. It answers a 401.

- **A (my pick):** keep it.
- **B:** you suggest something better.

## Already settled

The agent also flagged that the style guide had no rule that an `if` takes braces. That rule has since landed, at `docs/roc-style.md:897`, and you've decided it applies to every project.
