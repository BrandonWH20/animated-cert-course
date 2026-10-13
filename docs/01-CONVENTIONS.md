# Conventions — house rules

*Read before authoring. Consistency here is what makes a set of scenes look like one product
instead of twelve experiments.*

## Directory layout

```
cert-course-template/
  AGENTS.md / CLAUDE.md         # agent entry point — the workflow
  docs/                         # the spec set (runbook, conventions, scene recipe, visual bar, prompts)
  shared/theme.py               # canonical palette + helpers — IMPORT, never redefine
  animations/<slug>/
    scene.py                    # the Manim scene (class name = PascalCase of slug)
    script.md                   # beat-synced narration — the sync contract
    meta.yaml                   # title, duration, domain, publish status
    renders/                    # rendered mp4 (gitignored)
  courses/<cert>/
    chapters.json               # the per-chapter contract (start/end/slug/scene_class)
    transcript/                 # whisper output (gitignored)
    renders/                    # assembled module video (gitignored)
  templates/                    # fill-in templates for KB, podcast source, podcast prompt
  build/                        # drift check + assembly
```

Slugs are kebab-case and prefixed with the chapter number (`m02-05-attention`). The Manim class
is the PascalCase of the slug. `meta.yaml`'s `scene_class` **must** equal the Python class name —
the Makefile resolves the render target from it, and a mismatch renders nothing.

## The sync contract

- Every beat in `scene.py` is wrapped in `self.next_section("BeatName")`.
- `script.md` has one `## Beat: BeatName` per section, **names matching exactly** (case, spacing).
- A scene's total `run_time` + `wait` equals its `end - start` from `chapters.json`.

That three-way lock (chapters.json ⇄ script.md ⇄ scene.py) is what lets you regenerate one
chapter without touching the others.

## Visual house style

- Dark background. High-contrast palette from `shared/theme.py` — blues/teal/green/amber/red.
- **Text, never LaTeX** (`Text`/`MarkupText`). Keeps rendering dependency-free. Unicode math
  (`≈ → · Σ √`) is fine.
- Few elements on screen at once. One idea per beat. Labels fade rather than pile up.
- 16:9. 720p for drafts (`-qm`), 1080p for publish (`-qh`).
- No emojis in any rendered string.

## Text budget (per beat)

One short title plus at most two short caption lines. Numbers and labels *inside* a diagram don't
count. If you're writing a full sentence on screen, redesign the beat as a diagram.

## Guardrails

- **Generic, public content only.** No employer-confidential material, customer names, internal
  figures, or anything under NDA. Certification concepts are public; your company's deal data is not.
- Never commit heavy artifacts: `renders/`, `.venv/`, `media/`, audio files are gitignored.
- Don't edit `build/synced.py` or a `chapters.json` to make a scene fit. Fix the scene.
