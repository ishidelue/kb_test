#!/usr/bin/env python3
"""
build_manifest.py — regenerate notes.json from the notes in notes/.

Each note HTML embeds its own metadata in:
    <script type="application/json" id="kb-meta"> { ... } </script>

This script scans notes/*.html, extracts that block from every note, and
writes a fresh notes.json (sorted newest-first). The manifest is therefore a
*derived* artifact — never hand-edited — so:
  - notes generated on iPad (which can't update the manifest) just drop in;
  - two edit sources never cause a notes.json merge conflict (rebuild, don't merge);
  - re-importing the same note overwrites by `id` instead of duplicating.

Usage:
    python build_manifest.py            # build from ./notes -> ./notes.json
    python build_manifest.py --check    # verify only; non-zero exit on problems
"""
import json, re, sys, html
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Windows consoles often default to a legacy codepage (e.g. cp950 on a
# Traditional-Chinese system), which can't encode the ✓ / — status glyphs or
# Chinese note titles. Force UTF-8 so the build never crashes on output.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
NOTES_DIR = ROOT / "notes"
MANIFEST = ROOT / "notes.json"
REQUIRED = ["id", "prefix", "skill", "type", "title", "date", "file"]

META_RE = re.compile(
    r'<script[^>]*id=["\']kb-meta["\'][^>]*>(.*?)</script>', re.S | re.I
)

def extract_meta(path: Path):
    text = path.read_text(encoding="utf-8")
    m = META_RE.search(text)
    if not m:
        return None, f"no kb-meta block in {path.name}"
    raw = html.unescape(m.group(1).strip())
    try:
        meta = json.loads(raw)
    except json.JSONDecodeError as e:
        return None, f"invalid JSON in {path.name}: {e}"
    missing = [k for k in REQUIRED if not meta.get(k)]
    if missing:
        return None, f"{path.name} missing fields: {', '.join(missing)}"
    # normalise file path to be relative to KB root
    meta["file"] = f"notes/{path.name}"
    return meta, None

def main():
    check_only = "--check" in sys.argv
    if not NOTES_DIR.exists():
        print(f"! notes/ not found at {NOTES_DIR}", file=sys.stderr)
        sys.exit(1)

    entries, problems, seen = [], [], {}
    for path in sorted(NOTES_DIR.glob("*.html")):
        # retired notes are kept on disk but renamed with a (not_in_use)
        # postfix; skip them so they drop out of the manifest/index.
        if "(not_in_use)" in path.name:
            continue
        meta, err = extract_meta(path)
        if err:
            problems.append(err); continue
        nid = meta["id"]
        if nid in seen:
            problems.append(f"duplicate id '{nid}' ({path.name} vs {seen[nid]})")
            continue
        seen[nid] = path.name
        entries.append(meta)

    # newest first by date, then created timestamp
    entries.sort(key=lambda e: (e.get("date", ""), e.get("created", "")), reverse=True)

    for p in problems:
        print(f"! {p}", file=sys.stderr)

    if check_only:
        print(f"checked {len(entries)} note(s); {len(problems)} problem(s).")
        sys.exit(1 if problems else 0)

    MANIFEST.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    tz = timezone(timedelta(hours=8))  # Asia/Taipei
    stamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M")
    print(f"✓ wrote {MANIFEST.relative_to(ROOT)} — {len(entries)} note(s) @ {stamp}")
    if problems:
        print(f"  ({len(problems)} skipped — see warnings above)")

if __name__ == "__main__":
    main()
