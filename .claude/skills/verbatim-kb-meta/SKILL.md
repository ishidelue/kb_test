---
name: verbatim-kb-meta
description: >-
  Index a standalone verbatim/transcript HTML note that has no kb-meta block.
  Trigger when the user points at an existing notes/*.html (typically a 逐字稿 /
  dialogue transcript produced outside the template) and asks to generate its
  kb-meta, index it, or "make it show up in the KB / search". Infers the
  metadata from the file's own content, injects a valid kb-meta block, aligns
  the filename to the id, and rebuilds notes.json via the project venv. Does
  NOT rewrite or restyle the note body.
---

# verbatim-kb-meta

Make an already-written, self-contained HTML note discoverable by the KB. These
notes (usually verbatim transcripts / 逐字稿) come from outside the
`mba-class-note` template — they carry their own inline CSS and MathJax and
render fine on their own, but `build_manifest.py` skips them because they have
**no `<script id="kb-meta">` block**, so they never reach `notes.json`,
`index.html`, or search.

This skill only **adds metadata**; it is not a note generator. Read the repo's
`CLAUDE.md` first — its note contract and invariants govern this skill and
override anything ambiguous here.

## Trigger

The user references an existing file under `notes/` (e.g. "index the
cost-of-capital verbatim", "generate kb-meta for notes/…​.html", "why isn't this
in the KB / search") and wants it indexed. One invocation = one file.

If the file already has a `kb-meta` block, this is the wrong skill — treat it as
an edit (adjust the block, rebuild) and say so; don't add a second block.

## Hard rules

- **Never touch the note's own content.** Do not edit or strip its inline
  `<style>`, MathJax, headings, or body. The only mutation is inserting one
  `kb-meta` block (and renaming the file). The note must still render standalone.
- **Do not fabricate.** Derive every field from what's actually in the file. If a
  value truly can't be inferred (e.g. date), use a provisional value and tell the
  user in chat what to confirm — don't silently guess.
- **Never delete or overwrite the file's substance.** Renaming to `<id>.html` is
  the only file-level change (use `git mv` when the file is tracked, so history
  follows).

## Steps

1. **Read the file** and pull identity signals from its own content:
   - `title` — from `<title>` or the `<h1>` (zh-TW, keep the note's wording).
     **Do not** annotate the title with `（逐字稿）` or similar — that it's a
     transcript is carried by the `tags` (see below) and `type`, not the title.
   - `course` (課程) — look for a "課程 | Course: …" line or equivalent.
   - `date` — from an explicit date in the body, else the filename
     (`YYYY-MM-DD`). If none, use today's date and flag it as provisional in chat.
   - `topic` — a short zh-TW comma list of what the note covers (mirror the note's
     own section headings / key terms; don't invent scope).
   - `tags[]` — **English** framework/concept names for cross-cutting search
     (e.g. `WACC`, `CAPM`, `IRR`, `Beta`, `Tax Shield`). Pull these from the note.
     Also add a **`Verbatim`** tag so the note is discoverable as a transcript —
     this is where "it's a 逐字稿" lives, not in the title.
   - `domains` ⊆ `{ "hospital", "startup" }` — include a domain only if the note
     actually discusses it (醫院/hospital → `hospital`; 新創/Spridea/startup →
     `startup`). Omit domains the note doesn't touch.
   - `prefix` — `PMBA` unless the filename/content clearly indicates another
     family; then use that (uppercase).

2. **Derive identity (deterministic).**
   - `topic-slug` = lowercase, hyphenated, ASCII. For a transcript, end it with
     `-verbatim` so it doesn't collide with a template note on the same topic.
   - `id` = `<prefix-lower>-<YYYY-MM-DD>-<topic-slug>`.
   - **Filename must equal `<id>.html`.** If it differs, plan a `git mv`.

3. **Compose the kb-meta block** (all schema keys, stable + additive):

   ```html
   <script type="application/json" id="kb-meta">
   {
     "id": "<prefix-lower>-<date>-<topic-slug>",
     "prefix": "PMBA",
     "skill": "verbatim-kb-meta",
     "type": "verbatim-transcript",
     "title": "…（zh-TW）",
     "course": "…（zh-TW）",
     "date": "YYYY-MM-DD",
     "topic": "…（zh-TW，逗號分隔）",
     "tags": ["…English…"],
     "domains": ["hospital", "startup"],
     "created": "YYYY-MM-DDThh:mm:ss+08:00",
     "file": "notes/<id>.html"
   }
   </script>
   ```

   - `type` = `verbatim-transcript` for a 逐字稿. Use a different existing type
     only if the note is clearly something else — never reuse `class-note` for a
     transcript.
   - `created` = an ISO-8601 `+08:00` timestamp. If the real capture time is
     unknown, set a reasonable one and tell the user it's a placeholder.
   - `build_manifest.py` rewrites `file` to `notes/<actual filename>` anyway, but
     set it to `notes/<id>.html` to match the rename.

4. **Inject** the block just before `</head>` (or, if the file has no `<head>`,
   just before `</body>`). Insert only — change nothing else.

4b. **Add a "回知識庫" back-to-KB button.** Insert a fixed, self-contained
   anchor just after `<body>` that links to the portal, so the reader can jump
   back to the index from a verbatim page:

   ```html
   <a href="../index.html" aria-label="回知識庫" style="position:fixed;top:16px;left:16px;z-index:1000;display:inline-flex;align-items:center;gap:6px;padding:8px 14px;font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:12px;letter-spacing:.04em;text-decoration:none;color:#16191C;background:rgba(255,255,255,.86);-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px);border:1px solid rgba(22,25,28,.14);border-radius:999px;box-shadow:0 2px 10px rgba(22,25,28,.10);">
     <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>回知識庫</a>
   ```

   - **All styling is inline** so the button needs no external CSS and the note
     still renders standalone (single-file rule). Don't add it to `kb.css`.
   - Link is **`../index.html`** — notes live in `notes/`, the portal at root.
   - Idempotent: if the note already has a `回知識庫` / back-to-KB link, leave it;
     don't add a second one.

5. **Align the filename.** If the current name ≠ `<id>.html`, rename it:

   ```
   git mv notes/<old>.html notes/<id>.html
   ```

   (Plain rename if the file isn't tracked yet.)

6. **Rebuild the manifest via the venv** (stdlib-only, but always use the venv):

   ```
   venv\Scripts\python.exe build_manifest.py
   venv\Scripts\python.exe build_manifest.py --check
   ```

   The rebuild should now include the note (count goes up by one) and `--check`
   must report **0 problems**. If it still reports "no kb-meta block" or "missing
   fields", fix the block and rebuild — don't hand-edit `notes.json`.

7. **Report & optionally commit.** Tell the user the derived `id`, `type`,
   `domains`, and any provisional values (date/created) to confirm. Commit/push
   only if the user asks.

## Checklist before finishing

- [ ] Exactly one `kb-meta` block added; note body/CSS/MathJax untouched.
- [ ] One inline-styled `回知識庫` button added after `<body>`, linking
      `../index.html` (not duplicated if already present).
- [ ] `id` deterministic; filename = `notes/<id>.html`; `kb-meta.file` matches.
- [ ] Required fields present (`id, prefix, skill, type, title, date, file`) and
      `type` = `verbatim-transcript` (not `class-note`).
- [ ] `tags[]` English and include `Verbatim`; `title` NOT annotated with
      （逐字稿）; `title`/`course`/`topic` zh-TW; `domains` ⊆ {hospital, startup}
      and only those the note discusses.
- [ ] Manifest rebuilt via venv; `--check` clean; note count increased by one.
- [ ] Any provisional value (date/created) surfaced to the user for confirmation.
