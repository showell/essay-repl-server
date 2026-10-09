#!/usr/bin/env python3
"""Our lexicon: the words the box and CC use far more than technical English.

Reads metal-vmm's QUEUE.md, QUEUE-ARCHIVE.md and FEEDBACK.md, and compares
each word's rate there with its rate in the box's man pages (/usr/share/man,
English technical prose, so "file", "error" and "write" cancel out and what is
left is ours). Prints the most over-used words, two-word phrases, and the
code names in backticks.

    python3 tools/lexicon.py [repo dir | file ...]   default ~/showell_repos/metal-vmm

A .zig file contributes its comments as prose, and its function and field
names as code names.

The man-page counts are cached in ~/.cache/lexicon-baseline.json.
"""
import collections
import gzip
import json
import math
import os
import re
import sys

DOCS = ["QUEUE.md", "QUEUE-ARCHIVE.md", "FEEDBACK.md"]
CACHE = os.path.expanduser("~/.cache/lexicon-baseline.json")
WORD = re.compile(r"[a-z]+")
# Names of things, not vocabulary: the repos, the tools, the people.
NAMES = set("""zig gopher metal vmm angry steve sdk chat wce virtio fat elf qemu
kvm linux tcp scsi fsck github antithesis damian codex roc caddy droplet ladder
lynrummy http dhcp msi apic pci rfc spc sbc mib kib gib json jsonl utc""".split())
# Function words, skipped in phrases only (a phrase like "of the" says nothing).
FUNCTION = set("""a an the of to in on at by for from with and or but not no is
are was were be been being it its it's this that these those as if then than so
do does did done has have had can could may might must shall should will would
one two each every all any some what which who whom when where why how there
here i we you he she they them our your his her their me us my up out over into
onto off about after before again also only just more most much many very own
same such too yet both either neither nor""".split())


def lemma(w):
    if len(w) > 4 and w.endswith("ies"):
        return w[:-3] + "y"
    if len(w) > 3 and w.endswith(("ches", "shes", "xes", "sses", "oes")):
        return w[:-2]
    if len(w) > 3 and w.endswith("s") and not w.endswith(("ss", "us", "is")):
        return w[:-1]
    return w


def words(text):
    text = re.sub(r"['\u2019]s\b", "", text.lower())
    return [lemma(w) for w in WORD.findall(text) if len(w) >= 3]


def baseline():
    if os.path.exists(CACHE):
        with open(CACHE) as f:
            return collections.Counter(json.load(f))
    counts = collections.Counter()
    pairs = collections.Counter()
    for root, _, files in os.walk("/usr/share/man"):
        if "/man" not in root or root.count("/") > 4:  # English pages only, not /usr/share/man/de
            continue
        for name in files:
            try:
                with gzip.open(os.path.join(root, name), "rt", errors="ignore") as f:
                    text = f.read()
            except (OSError, EOFError):
                continue
            text = re.sub(r"^\.[A-Za-z]+.*$", " ", text, flags=re.M)  # troff requests
            text = re.sub(r"\\f[BIRP]|\\[-&(e]\S?", " ", text)
            ws = words(text)
            counts.update(ws)
            pairs.update(f"{a} {b}" for a, b in zip(ws, ws[1:]))
    merged = dict(counts)
    merged.update({k: v for k, v in pairs.items() if v >= 3})
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, "w") as f:
        json.dump(merged, f)
    return collections.Counter(merged)


def read_sources(args):
    """Prose from the arguments: a directory means its DOCS; a .zig file
    gives its comments, and its field and function names as code names; any
    other file is read whole."""
    text, code = "", collections.Counter()
    for a in args:
        if os.path.isdir(a):
            for d in DOCS:
                p = os.path.join(a, d)
                if os.path.exists(p):
                    with open(p) as f:
                        text += f.read() + "\n"
        elif a.endswith(".zig"):
            with open(a) as f:
                src = f.read()
            text += "\n".join(m for m in re.findall(r"//[/!]?(.*)", src)) + "\n"
            body = re.sub(r"//.*", "", src)
            code.update(re.findall(r"\bfn\s+([A-Za-z_]\w*)", body))
            code.update(re.findall(r"^\s+([a-z_]\w*)\s*:\s*[^=]", body, flags=re.M))
        else:
            with open(a) as f:
                text += f.read() + "\n"
    return text, code


def main():
    args = sys.argv[1:] or [os.path.expanduser("~/showell_repos/metal-vmm")]
    text, code = read_sources(args)
    DOCS_SAID = ", ".join(os.path.basename(a) for a in args)
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    idents = collections.Counter(m for m in re.findall(r"`([^`\n]{2,40})`", text)) + code
    prose = re.sub(r"`[^`\n]*`", " ", text)
    prose = re.sub(r"\b[0-9a-f]{7,40}\b", " ", prose)

    ws = words(prose)
    ours = collections.Counter(ws)
    ours_pairs = collections.Counter(
        f"{a} {b}" for a, b in zip(ws, ws[1:]) if a not in FUNCTION and b not in FUNCTION and a not in NAMES and b not in NAMES
    )
    base = baseline()
    n_ours = sum(ours.values())
    n_base = sum(v for k, v in base.items() if " " not in k)

    def score(c, b):
        return math.log((c + 1) / n_ours) - math.log((b + 1) / n_base)

    out = [f"{len(ws)} words of prose in {DOCS_SAID}; baseline: {n_base} words of man pages\n"]
    out.append("WORDS, most over-used (count here, count in the man pages)")
    top = sorted((w for w, c in ours.items() if c >= 15 and w not in FUNCTION and w not in NAMES), key=lambda w: -score(ours[w], base[w]))
    for w in top[:70]:
        out.append(f"  {w:<18} {ours[w]:>5}  {base[w]:>7}")
    out.append("\nPHRASES, most over-used")
    topp = sorted((p for p, c in ours_pairs.items() if c >= 8), key=lambda p: -score(ours_pairs[p], base[p]))
    for p in topp[:45]:
        out.append(f"  {p:<30} {ours_pairs[p]:>5}  {base[p]:>7}")
    out.append("\nCODE NAMES in backticks, most used")
    for name, c in idents.most_common(35):
        out.append(f"  {name:<30} {c:>5}")
    print("\n".join(out))


if __name__ == "__main__":
    main()
