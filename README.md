# PMBA Knowledge Base

A static, HTML-based personal knowledge base. Each note is a self-contained HTML
file that embeds its own metadata; `notes.json` is a **derived** manifest built
from those notes; `index.html` is a client-side browser (search + filter) over
the manifest. Visual language borrowed from the *Spridea* design system
(zinc grayscale; Fraunces / Inter / IBM Plex Mono).

## Structure
```
kb/
├── index.html          # browser: search + filter by family (prefix) / domain
├── notes.json          # DERIVED manifest — never hand-edit; rebuild instead
├── build_manifest.py   # scans notes/*.html → regenerates notes.json
├── assets/
│   └── kb.css          # single source of truth for the theme
└── notes/
    └── <id>.html       # one note per class; embeds <script id="kb-meta">
```

## The metadata contract (every note, every sibling skill)
Each note embeds:
```html
<script type="application/json" id="kb-meta">
{ "id","prefix","skill","type","title","course","date","topic",
  "tags":[...],"domains":["hospital"|"startup"],"created","file" }
</script>
```
- `prefix` is the **family / namespace** (`PMBA`, future `ER`, `ENG`, …) — lets many
  skills share one KB and lets the index filter by family.
- `domains` drives the domain filter (醫院/急診 vs 資訊新創).
- Keep these keys **stable and additive** — rename one and the index/search breaks.

`id` = `<prefix-lower>-<YYYY-MM-DD>-<topic-slug>` (e.g. `pmba-2026-06-10-competitive-advantage`).
Filename = `<id>.html`.

## Two workflows

### 1) In class (iPad / Claude app)
Generate a single note with the `mba-class-note` skill (`[PMBA] …`). It produces a
self-contained `<id>.html` (inline critical CSS, so it looks right even before it's
filed). Save the file. Back at the office, drop it into `notes/`, then:
```bash
python build_manifest.py     # rebuild notes.json
git add notes/ notes.json && git commit -m "note: <topic>" && git push
```
The note can't update the manifest on iPad — that's fine, the rebuild handles it.

### 2) At the office (Claude Code CLI)
Edit the whole KB directly. After adding/editing/removing notes, run
`python build_manifest.py`, then commit & push. Because the manifest is regenerated
(not merged), notes from both workflows never conflict.

## Viewing
`index.html` fetches `notes.json`, which most browsers **block over `file://`**. Use
a local server or GitHub Pages:
```bash
python -m http.server 8000      # then open http://localhost:8000
```
For anywhere-access (incl. iPad), enable **GitHub Pages** on the repo.

## Theme
The KB uses a single grayscale theme.
Change any token in `assets/kb.css` to restyle the entire KB at once.
