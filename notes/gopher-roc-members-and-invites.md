# gopher-roc, step 2b: channel members and human invites

*2026-11-03. Written by the agent that built step 2b. It covers only that work; I can't see what the other agents are doing.*

## Where things stand

Step 2b is done on `feature/members`, in the worktree `~/showell_repos/gopher-roc-members`. It's rebased onto main, past the Hex merge, and not merged. There are two commits:

- **Channel pages.** At `/channels`, Steve sees every channel and can create one. `/channels/<name>` lists a channel's members, with a button to remove each, and a button to add any other user, human or agent. A change rewrites the channel's `.channel` file through `FileSystem`. Removing a member also ends every stream they hold, so a removed agent reconnects and is refused. It doesn't wait for the hour-long stream to expire.
- **Human invites.** Any human invites someone by name at `/invites`. The new account holds the name at once, and the inviter sees a one-time code, good for seven days. Debbie enters that code on the sign-in page, along with the password she chooses. The server spends the invite, stores only the bcrypt hash of her password, and signs her in. Her inviter, or Steve, can invite her again; that gives a new code for the same account, and redeeming it sets a new password. Each human may have at most ten open invites.

The gate is green: 1,314 expects, every hunt at zero, 85 host tests, and an end to end that now drives all of this over HTTP in about two seconds.

The rules mostly come from roc-chat: only the admin changes who is in a channel, and only by session, never with an API key. One rule is new, because humans here sign in with passwords: redeeming an invite sets one.

## What you need to decide

- **The new file formats.** They're an `inviter` file in each invited human's folder, and a `human-invites/<n>/` folder per invite, holding `created`, `expires`, `by`, `state` and `hash`. Each is one small file per fact, the same layout as agents' keys. design.md's storage section lists them all.
- **Account takeover by invite.** Inviting someone again gives the inviter a code that can set the invitee's password. The inviter could redeem it themselves and take over the account. roc-chat had the same property, so I kept it. It's tolerable for a chat of friends. For anything larger, it's the first thing I'd revisit.
- **What I left out of roc-chat's invites:** revoking an invite; the DM and welcome message that came with each invite; choosing another name at redemption; and the cap of 200 invites made in total.

## Reflection

**Most of the pure-module tests passed on the first run. That says more about the codebase than about me.** I could read who may do what in the type signatures:

- an `Admin` value is the only way into a membership change;
- a `SignedIn` names how the user proved who they are;
- `HumanInvite.Admission` is the only thing that can start a session without a password check.

New code that follows those types has few places to go wrong. Writing the session door as a type took one line, and it is still the strongest security decision in the change.

**The gate pushed me to improve design, not just layout.** The hunts flagged lines to stack and names that read badly, and fixing those was mechanical. Two fixes were real design:

- Once `Page.roc` passed 1,000 lines, I split out `PeoplePages`, which builds the new pages from a few general parts that `Page` exposes. That's a better shape than one module holding every page.
- The "one home for a rule" doctrine caught two copies I had made without noticing: the words for a malformed form field, and the hashing of a secret. Both now live in one place.

**Plants proved the tests, and one green count nearly fooled me.** Each new refusal got one planted fault: removed, seen to turn the gate red, then restored.

The count is what nearly fooled me. `zig build test` reported 62 tests where the baseline had 85. The cause was harmless: steps served from the build cache report no counts. I only confirmed that by clearing the cache and seeing 85 again. A green result is only as good as the number of things that actually ran, and I nearly passed that one along without checking.

**The coordinator's notes arrived mid-flight and changed little.** The reviewer warned that user ids must never be reused or deleted. The design already removed only membership, never accounts. The note about bcrypt cost matched the host's default. What it did change is my list of risks: the sign-in fix branch will touch the same function where I now build session cookies, so a merge conflict there is likely.

**One thing I'd do differently: write the end to end first, not last.** I wrote the pure rules first, and the HTTP steps afterwards. The end-to-end steps that are now the proof of the whole change would have been a better guide from the start. Writing them first would have shown earlier, for instance, that redeeming needs an obvious place to land. It lands on `/agents`, which is fine for now but feels arbitrary for someone like Debbie.
