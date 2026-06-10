# CLAUDE.md — PMBA Knowledge Base (operating guide / 交班文件)

A static, HTML-based personal knowledge base. **Each note is a self-contained HTML file and is the source of truth**; everything else is derived or presentational. Read this before editing anything.

---

## Project rules (non-negotiable)

1. **Python runs through the venv.** A `venv/` (Python 3.13) lives in the repo and is the only Python this project uses. Always invoke it explicitly — `venv\Scripts\python.exe build_manifest.py` — never the system `python`. `build_manifest.py` is stdlib-only today; future dependencies go in `requirements.txt` and are installed into the venv. `venv/` is git-ignored.
2. **Note content is Traditional Chinese (Taiwan / zh-TW).** All saved note body text, synthesis, glosses, follow-ups and reference summaries are in zh-TW. `tags[]` stay in English for cross-cutting search. Chat/assistant replies are in English — only the artifacts are zh-TW.
3. **Never delete a note.** To retire one, rename it `notes/<id>(not_in_use).html`. The file stays on disk; `build_manifest.py` skips any `(not_in_use)` file so it drops out of the manifest and index. This overrides any "delete" instruction below.

---

## What lives where

| Path | Role |
|---|---|
| `index.html` | Browser/portal. Client-side: fetches `notes.json`, renders cards, search + filter by **family (prefix)** and **domain**. KB-owned; not generated per note. |
| `notes.json` | **Derived** manifest (array of note metadata). **Never hand-edit.** Rebuild with `build_manifest.py`. |
| `build_manifest.py` | Scans `notes/*.html`, extracts each note's embedded `kb-meta`, regenerates `notes.json`. Flags duplicate ids + missing fields. `--check` validates without writing. |
| `assets/kb.css` | Single source of truth for the theme. Change a token → whole KB restyles (in-repo rendering). |
| `notes/<id>.html` | One note per class. **Source of truth.** Self-contained: inline critical CSS + linked `../assets/kb.css` + embedded `kb-meta`. |
| `.claude/skills/<name>/` | Note-generating skills (e.g. `mba-class-note`). Claude Code auto-loads these. |

---

## The note contract (every note, every skill)

Each note embeds its metadata so the manifest can be rebuilt from the notes themselves:

```html
<script type="application/json" id="kb-meta">{ ...metadata... }</script>
```

Schema — keys are **stable and additive**; never rename or repurpose them or the index breaks:

`id, prefix, skill, type, title, course, date, topic, tags[], domains[], created, file`

- `id` = `<prefix-lower>-<YYYY-MM-DD>-<topic-slug>`, deterministic. Filename = `<id>.html`.
- `prefix` = family / namespace (`PMBA`; future `ER`, `ENG`, …). Lets many skills share one KB; the index filters by it.
- `domains` ⊆ { `hospital`, `startup` }.
- `tags` = framework / concept names (English) for cross-cutting search.

---

## Single-file rule (do not break)

A note must render correctly **on its own** (e.g. on iPad, before it's filed into the repo). Therefore:

1. Keep the inline critical-CSS `<style>` block in `<head>` **verbatim** — never edit or strip it.
2. Keep `<link rel="stylesheet" href="../assets/kb.css">` immediately after it — overrides for full theming once in-repo.

A note missing the inline critical CSS is a bug.

---

## Design tokens (the "Spridea" language)

Zinc grayscale (`--g-0`…`--g-950`, accent `#18181b`). Fonts: **Fraunces** (serif display) / **Inter** (body) / **IBM Plex Mono** (mono + labels). Soft radii + shadows. Domain accents: hospital `#8fa6b0`, startup `#b79a86`. Corrections: amber `#a16207` (**never red**). Theme changes go in `kb.css`; never invent per-note colours.

---

## Editing rules

- Change to `kb-meta` (title / date / tags / domains / id) → **rerun `python build_manifest.py`**.
- Body-text-only change → no rebuild needed; just commit/push.
- **Never** hand-edit `notes.json` — always rebuild.
- **Never delete** a note. Retire it by renaming to `notes/<id>(not_in_use).html` (kept on disk, skipped by the manifest), then rebuild.
- Re-generating a class overwrites by `id` (deterministic) — intended.

---

## Skills

- **`mba-class-note`** — trigger `[PMBA] …`. Turns transcript + in-class shorthand into a structured note, builds `<id>.html` from `assets/note-template.html`, fixes clear errors inline in **amber** (`<span class="correction">`), and adds web references under `延伸`. See its `SKILL.md`.
- Future sibling skills use their own `[PREFIX]` and the **same** note contract + template pattern, so they coexist in one KB.

Install: drop the skill folder in repo `.claude/skills/<name>/` (auto-loaded by Claude Code) or in `~/.claude/skills/` (personal, all projects). The packaged `.skill` also installs in Claude.ai / Claude Desktop.

---

## Workflows

1. **iPad (Claude app), in class:** generate a single `<id>.html` → save → back at office, drop into `notes/` → `python build_manifest.py` → commit / push.
2. **Office (Claude Code):** edit notes / reorganize directly → rebuild → commit / push.

The manifest is **rebuilt, not merged**, so notes coming from both sources never cause a `notes.json` conflict.

---

## Common operations (Claude Code)

Run Python through the venv (PowerShell, repo root):

```powershell
venv\Scripts\python.exe build_manifest.py            # rebuild notes.json from notes/
venv\Scripts\python.exe build_manifest.py --check    # validate only (CI-friendly)
venv\Scripts\python.exe -m http.server 8000          # serve locally (index fetch needs http://, not file://)
```

`build_manifest.py` skips any `notes/*(not_in_use)*.html`, so retired notes stay on disk but leave the index.

Bulk reorg (merge / split / retag / dedupe / add backlinks): edit the note files, then rebuild. Tell Claude Code the intent; it does file ops + rebuild + commit in one pass.

---

## Invariants (don't violate)

- `notes/<id>.html` is the source of truth; `notes.json` is derived.
- Don't edit inline critical CSS in notes; theme via `kb.css`.
- Keep `kb-meta` keys stable; add fields, don't rename.
- Corrections in amber, never red; never "correct" the user's judgment, framing, or analogies — only clear factual/formula/arithmetic errors, and flag them under `待追`.
- References respect copyright: link + one-line summary, no long quotes.

---

## Deploy

Static site → enable **GitHub Pages** for anywhere access (incl. iPad). Commit `notes.json` (always regenerated, never hand-edited).
