# Chat's data on a volume

*2026-10-01, late. gopher-metal `4cdcf5d`.*

## The problem

Every new gopher-metal image replaces the droplet's whole disk, and chat's
files with it. That was fine for testing. It can't stay that way.

## The fix: a second disk that deploys don't touch

DigitalOcean sells **volumes**: separate disks you attach to a droplet. When
the droplet is rebuilt from a new image, its boot disk is replaced and the
volume isn't. A volume is $0.10 per GB per month, can be grown later, and can
be snapshotted for backups.

A volume shows up on a droplet as a **SCSI disk** behind a "virtio-SCSI"
controller, which every droplet has in PCI slot 5 whether or not a volume is
attached. SCSI is an old, simple language for talking to disks. Metal needs
only four of its commands:

- **INQUIRY:** is there a disk at this address?
- **READ CAPACITY:** how big is it?
- **READ** and **WRITE:** a run of 512-byte sectors.

The new driver, `src/scsi.zig`, speaks those four. It answers the same four
questions the old disk driver did ("read a sector", "read many", "write one",
"write many"), so the FAT16 and partition code above it didn't change at all.

When the chat server starts, it looks for a volume. If one is attached, chat's
files come from it. If none is attached, they come from the boot disk, as
they do today. If a volume is attached but broken, the machine stops and says
so, instead of quietly serving an old copy.

## How it was checked

- On the droplet-shaped test machine, a volume placed at three different
  SCSI addresses was found every time. We don't yet know which address
  DigitalOcean uses, so the driver searches.
- The chat judge, which compares every answer and every file with Linux, now
  runs on the droplet-shaped machine with chat's files on a volume. It passes
  in full, uploads included: a picture written through the new driver
  matches Linux byte for byte.
- Everything else still passes too: the old test machine, the boot checks,
  and metal-vmm.

**It hasn't touched a real volume yet.**

## One thing to fix before it goes live

Not everything on today's data disk is data. The home page's text and
pictures (`pages/`, `gallery/`) and metal's own settings belong with the
image, so each deploy updates them. Chat, games and accounts belong on the
volume. So metal will mount **both** disks and send each file to the right
one by its first directory. That's next.

## Room to grow

FAT16 tops out at 2 GB. Prod's data is 215 MB today, nearly all of it chat
and its images. Each user may upload 1 GiB over their lifetime, so two heavy
uploaders could fill a FAT16 volume. FAT32 is the eventual answer, and the
cloud Claude is writing a design note for it.

## Maintenance

Deleting old chats doesn't need metal at all. Turn metal off, boot the
droplet into DigitalOcean's recovery Linux, `mount /dev/sda1`, delete, and
unmount. Linux reads and writes our FAT16; that's been tested in both
directions since September.
