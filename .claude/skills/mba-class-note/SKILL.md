---
name: mba-class-note
description: >-
  Turn a PMBA class transcript + in-class shorthand into a structured,
  self-contained HTML knowledge-base note. Trigger when the user's message
  starts with "[PMBA]" (or asks to make/file a PMBA class note). Produces
  notes/<id>.html from assets/note-template.html, content in Traditional
  Chinese (Taiwan), then rebuilds notes.json via the project venv.
---

# mba-class-note

Generate one self-contained class note for the PMBA Knowledge Base. The note is
the **source of truth**; `notes.json` and `index.html` are derived from it.
Read the repo's `CLAUDE.md` first — its note contract and invariants govern this
skill and override anything ambiguous here.

## Trigger

The user opens with `[PMBA] …` (e.g. `[PMBA] 財管 第3堂 現金流量表` followed by a
transcript / photographed whiteboard / shorthand), or explicitly asks to make a
PMBA class note. One invocation = one note = one class.

## Language rule (important)

- **All note body content is Traditional Chinese (Taiwan / zh-TW)** — section
  prose, synthesis, key-term glosses, follow-ups, reference summaries.
- **`tags[]` stay in English** (framework / concept names) for cross-cutting
  search; bilingual term lines (`English 中文 — 定義`) are encouraged in 關鍵詞.
- Talk to the user in **English** in chat; only the saved note is zh-TW.

## Steps

1. **Parse the input.** Pull out: course (課程), class topic, date, the
   frameworks/concepts covered, any case discussed, the teacher's emphasis, and
   the user's own takes. Keep the user's shorthand meaning; don't invent content.

2. **Derive identity (deterministic).**
   - `date` = the class date in `YYYY-MM-DD`. If the user didn't give one, use
     today and add a 待追 line noting the date is provisional.
   - `topic` = a short English topic slug source; `topic-slug` = lowercase,
     hyphenated, ASCII.
   - `id` = `pmba-<YYYY-MM-DD>-<topic-slug>`. **Filename = `<id>.html`.**
   - Re-generating a class reuses the same `id`, so it overwrites by design.

3. **Build the file from the template.** Copy `assets/note-template.html` and
   replace every `{{TOKEN}}` and the whole `kb-meta` block with real values.
   - Fill `kb-meta`: `id, prefix("PMBA"), skill("mba-class-note"),
     type("class-note"), title, course, date, topic, tags[], domains[], created
     (ISO-8601 +08:00), file("notes/<id>.html")`.
   - `domains` ⊆ `{"hospital","startup"}` — keep only those the material maps to,
     and keep the matching `.domain-pill` rows; delete the others.
   - **Single-file rule:** never edit or strip the inline critical-CSS `<style>`
     block, and keep `<link rel="stylesheet" href="../assets/kb.css">` right
     after it. The note must render standalone (e.g. on iPad before filing).
   - Sections are flexible per class. Keep at least **核心概念** and **我的綜整**;
     add **個案 · Case** and **決策與依據 · Decision & Rationale** for case
     classes, **應用 · Application** for tool/analysis classes; drop empty ones.
   - In **我的綜整 (So what)** always write the user's angle for each kept domain
     (醫院 / 新創) — this is the point of the KB.

4. **Corrections — amber, conservative.** Fix only **clear factual / formula /
   arithmetic errors** in the shorthand, inline with
   `<span class="correction" title="原記錄：…">…</span>` (amber, **never red**),
   and add a `已修正` line under **待追** quoting the original and the fix, ending
   with「請確認」. **Never** "correct" the user's judgment, framing, or analogies.

5. **References — 延伸.** Add 1–3 web references (link + one-line zh-TW summary).
   Respect copyright: no long quotes. If you can't verify a source, don't fabricate
   it — add a 待追 line instead.

6. **Save** to `notes/<id>.html`.

7. **Rebuild the manifest via the venv** (stdlib-only, but always use the venv):

   ```
   venv\Scripts\python.exe build_manifest.py
   ```

   Then `venv\Scripts\python.exe build_manifest.py --check` should report 0
   problems. Commit/push if the user wants.

## Retiring / replacing notes (never delete)

- **Never delete a note file.** To retire one, rename it to
  `notes/<id>(not_in_use).html`. `build_manifest.py` skips any `(not_in_use)`
  file, so it leaves the index while staying on disk.
- Editing only body text (no `kb-meta` change) needs no rebuild. Any change to
  `kb-meta` (title/date/tags/domains/id) or adding/retiring a note → rebuild.
- Never hand-edit `notes.json`.

## Checklist before finishing

- [ ] `id` / filename deterministic and matching; `kb-meta.file` = `notes/<id>.html`.
- [ ] Inline critical CSS intact; `kb.css` link present.
- [ ] Body zh-TW; `tags[]` English; `domains` ⊆ {hospital, startup}.
- [ ] Corrections amber + logged under 待追; user's judgment untouched.
- [ ] Manifest rebuilt via venv; `--check` clean.
