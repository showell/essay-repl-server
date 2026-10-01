# metal.lynrummy.com

*2026-10-01, evening. gopher-metal `4bc6d27`.*

Gopher Chat on bare metal now has a real address: **https://metal.lynrummy.com**.
You logged in there and chat works.

## How a visit gets there

1. Your browser looks up `metal.lynrummy.com` and gets prod's address, the
   same droplet as lynrummy.com.
2. Prod's Caddy handles the HTTPS part, as it already does for lynrummy.com and
   roc.lynrummy.com. It picked up a certificate for the new name on its own.
3. Caddy passes the request across DigitalOcean's private network to
   `10.100.0.4`, the gopher-metal droplet.
4. gopher-metal answers. It has no Linux and no HTTPS code of its own, and it
   doesn't need either: Caddy is its front door.

The gopher-metal droplet no longer answers on its public address at all. It
listens only on its private card, so scanners can't reach it, and everything
goes through Caddy. That's the same layout as lynrummy.com, except that the
server behind Caddy is on a different machine.

## What changed today to get here

- **The v2 image:** chat's pictures, plus the setting that makes chat listen
  only on the private card.
- **One small Caddy file**, `droplet/metal.lynrummy.com.caddy` in gopher-metal,
  copied into `/etc/caddy/sites/` on prod. It uses the same limits and headers
  as lynrummy.com's. To undo it, delete the file and reload Caddy.

## What it still is: a test site

- **Its data is the chat judge's test site.** The test accounts' password is in
  the public gopher-metal repo, and now the site has a public name. It's fine
  for testing, but it's a reason not to tell anyone about it yet.
- **Rebuilding the droplet replaces its data.** You put that off until there's
  been much more testing.
- **One stall, still unexplained:** a boot here on this box printed its first
  line and then nothing for a minute. It hasn't happened again.

## Natural next steps, whenever you want them

- **Real accounts:** fresh data instead of the judge's test site, so the test
  password stops mattering.
- **Timing against lynrummy.com:** the same pages, fetched from the same place,
  through the same Caddy. That's the "comparable performance" goal, measured
  directly.
- **Data that survives a rebuild:** a separate DigitalOcean volume, or another
  home for chat's files.
