# Two decisions before the cutover

*2026-10-03, night. From the box Claude, after CC's reviews. Each has my
recommendation; a one-word answer is enough.*

Everything else from tonight I decided myself: the two small fixes CC held
back go in (an oversized-frame guard in the network driver, and metal's
request log dropping query strings), CC hunts the one unexplained test
failure in its TCP simulator, and the box gates all of it in the morning.

## 1. Limit password guessing: before the cutover, or after?

Nothing limits login attempts today, on Linux or on metal. On metal it is
also a stall: each guess is a deliberately slow bcrypt on its one processor,
so a flood of guesses holds up everyone.

CC's design (`gopher-metal/docs/designs/DESIGN-login-throttle.md`): after N
failed logins in a window, refuse further tries **before** the bcrypt, with
a cheap 429. Two counters: per address (stops one flooder, and the stall)
and per name (stops many addresses guessing one account, which really means
yours, uid 1). It reuses the game store's per-address table, and the judge
checks it on both hosts.

**The catch:** the per-name counter lets an attacker lock **you** out of
logging in until the window passes, by burning your name's budget. That is a
nuisance, not a breach.

**My recommendation:** CC builds it tonight on a branch, per address **10
failures / 15 minutes** and per name **30 failures / hour**, and you accept
the lockout risk (an hour at worst, during an attack that is unlikely on a
small chat site). The box gates it in the morning on both hosts; it ships
with the cutover only if it is green and you say yes, and otherwise right
after. It changes angry-gopher, so lynrummy.com (Linux) gets it in the same
deploy, which the runbook wants anyway (both hosts on one commit).

**Answer:** ship with the cutover / after the cutover / different numbers.

## 2. Backups: what runs on a schedule

The routine needs the admin password to call `/admin/backup`. **A cron job on
prod would have to store your admin password on prod**, which trades risk 2
(data loss) against risk 1 (passwords). So I would not automate the tar.

**My recommendation:**

- **DigitalOcean volume snapshots, daily and automatic**, plus one by hand
  just before go-live. They need no password stored anywhere, and restore the
  whole volume.
- **The encrypted `/admin/backup` tar by hand**, when you choose (weekly, or
  before anything risky), with a script that asks for your password, checks
  the tar is whole, encrypts it with `age`, keeps 7, and shreds the rest. CC
  writes that script tonight; I check it on the box.
- Later, if you want the tar automatic: a backup-only key that can do nothing
  else, so a stolen key leaks a backup but not your login.

So the worst case is losing up to a day of chat, and only if the whole volume
is lost. Users can always keep their own copy with `d`.

**Answer:** yes / a different interval / automate the tar anyway.
