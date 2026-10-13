# AGENTS.md — read this first

You are being pointed at this repo because someone wants to **build an animated, narrated video
course for a certification exam**, using the pipeline this repo implements. You will do most of
the work. This file tells you how.

If the user said something like *"copy this repo and let's build a course for the XYZ cert"* —
you are in the right place. Start at **Step 0** below.

---

## What this repo is

A template for producing a **time-synced companion video**: an AI-generated podcast is the
soundtrack, and animation is frame-locked to it. The result feels like a 3Blue1Brown explainer
with a two-host narration track.

The pipeline:

```
exam guide → knowledge base → podcast source + prompt → AI audio (NotebookLM)
   → transcript (word-level) → chapters.json → Manim scenes
   → render → drift check → mux original audio → module video
```

**Two rules the whole design rests on. Do not violate either:**

1. **The podcast audio is the soundtrack. Never generate TTS.** The real recording gets muxed
   over the finished animation untouched.
2. **Therefore every scene's runtime must exactly equal its slice of that audio.** Every chapter
   has a `start` and `end` in `chapters.json`; your scene must land on `end - start` within
   0.1s. This is called the *sync contract* and it is the one hard requirement in this repo.

## Read order (do not skip)

1. **This file** — the workflow.
2. `docs/01-CONVENTIONS.md` — layout, naming, house style, guardrails.
3. `docs/02-SCENE_TEMPLATE.md` — how to build one chapter to spec. **The timing engine lives
   here. Copy it verbatim; do not reinvent it.**
4. `docs/03-SCENE_CINEMATIC.md` — how the screen must *behave*. This is the quality bar, and it
   is where most first attempts fail.
5. `docs/04-PROMPTS.md` — the audio-generation prompts, with fill-in templates.
6. `docs/00-PRODUCTION-RUNBOOK.md` — environment, per-module build, publishing.

`animations/_template/` is a working reference chapter. Open it alongside the docs.

---

## Step 0 — Find out what you're building

Ask the user for these if they haven't said:

- **Which certification?** (exam code and full name)
- **Do they have the official exam guide / syllabus?** Domains and their percentage weights are
  the spec for the whole course. If they don't have it, ask them to paste it or link it. Do not
  invent a syllabus — a course built on a guessed blueprint wastes every later stage.
- **How deep?** One overview module, or an overview plus a deep dive per domain? (The reference
  build was 1 + 9.)
- **Who is the audience?** Working engineers, or beginners? This sets the depth directive in the
  audio prompt and it is hard to change later.

Then rename things: this repo's `courses/example-course/` is a worked example. Create
`courses/<their-cert>/` for the real work.

## Step 1 — Syllabus becomes structure

Turn the exam guide's domains into a module list, weighted by the published percentages. Create
one folder per module with the same four buckets: `Documents/`, `Scripts/`, `Audio/`, `Video/`.

Identical shape per module is what lets you parallelize later. Don't improvise per-module layouts.

## Step 2 — Write the knowledge base (before any audio or animation)

One markdown knowledge base per module, written to real depth: actual numbers, dimensions,
worked examples. Template: `templates/KNOWLEDGE-BASE.md`.

**The structural trick:** its `##` headings *are* the chapter structure. Podcast chunks map 1:1
onto KB sections; video chapters map 1:1 onto podcast chunks. One spine, three artifacts.

## Step 3 — Produce two files per module, never one

- `templates/PODCAST-SOURCE.md` → read-aloud chunks only, one per KB section.
- `templates/PODCAST-PROMPT.md` → the generation directives.

**Never combine them.** Instructions placed inside the source leak into the audio and the hosts
start narrating their own brief. See `docs/04-PROMPTS.md`.

## Step 4 — The user generates the audio (you cannot do this step)

Hand them the two files with these instructions: open a fresh NotebookLM notebook → upload the
Source as the *only* source → Audio Overview → Customize → paste the Prompt → Generate → save
the `.m4a` into that module's `Audio/`.

Then stop and wait. You need the real audio file to continue.

## Step 5 — Transcribe with word-level timestamps

```bash
.venv/bin/mlx_whisper "<module>/Audio/<file>.m4a" \
  --model mlx-community/whisper-large-v3-turbo \
  --output-dir courses/<cert>/transcript --output-format all \
  --language en --word-timestamps True
```

Word timestamps are non-negotiable — they are how a reveal lands on the exact syllable.

## Step 6 — Chapterize

Read the transcript. Cut it at *topic* boundaries (not fixed intervals). Write
`courses/<cert>/chapters.json` — schema and an annotated example in
`courses/example-course/chapters.json`.

Each chapter gets a slug, a scene class name, exact `start`/`end` seconds, a title, and a list of
key visuals. **This file is the contract.** Once written, treat it as fixed; don't quietly adjust
boundaries to make a scene easier.

## Step 7 — Build ONE chapter, by hand, carefully

Do not fan out yet. Pick chapter 1, build it completely, render it, check drift, sample frames,
and show the user. Follow `docs/02-SCENE_TEMPLATE.md` exactly.

**This step is the whole ballgame.** The proven chapter plus the written spec is what makes the
remaining chapters reproducible. Skipping it produces N inconsistent scenes instead of a course.

## Step 8 — Then parallelize

With chapter 1 approved, build the rest against the same template — each chapter is independent
and has an unambiguous success criterion (`end - start`), so they can be built concurrently.

Per chapter: write `script.md` (beats) → write `scene.py` → render → check drift → sample frames.

## Step 9 — Verify and assemble

```bash
make check COURSE=courses/<cert>/chapters.json      # per-chapter drift; must be < 0.5s, aim < 0.1s
make assemble COURSE=courses/<cert>/chapters.json   # concat + mux the original audio
```

## Step 10 — QA before you report done

**You will write code that runs clean and still produces a broken frame.** Rendering without
error is not success. Sample frames across every render and actually look at them:

```bash
ffmpeg -ss <t> -i <render> -frames:v 1 /tmp/frame_<t>.png
```

Check for: text overlapping text, labels off the frame edge, elements escaped from their boxes,
misspelled terms. The zero-overlap bar in `docs/03-SCENE_CINEMATIC.md` is non-negotiable. Fix and
re-render until clean, *then* report.

---

## The failure modes that cost the original build the most time

Read these before writing a scene. Every one of them is a mistake that shipped and had to be redone.

1. **Animated bullet points.** Fading word-cards in and out is a fancy teleprompter. Every
   mechanism must be drawn as a *picture* — motion, transformation, spatial relationships.
2. **Fade-swap instead of transform.** One object should persist and morph into the next idea.
   The eye tracking one evolving thing *is* the explanation.
3. **Decorative motion.** When told to stop holding still, agents fill gaps with looping
   scale-pulses ("breathing") on every shape. That reads as fidget, not film. Motion must carry
   meaning or the frame should be a composed still.
4. **Overlapping text.** The single most common render defect. Position with `.next_to()` /
   `.to_edge()` and explicit `buff`; fade out whatever occupied a spot before putting something
   new there.
5. **Using LaTeX.** `MathTex`/`Tex` hard-fail here by design. `Text`/`MarkupText` only; write
   math as words and Unicode (`≈ → · Σ √`).
6. **Hand-summing run times.** Use the timing engine's cumulative targets. If you find yourself
   adding durations, you've left the pattern.

## When you get feedback

Feedback arrives per chapter. Edit that one scene, re-render that one scene, re-assemble.

**And write the correction into the spec**, not just into this conversation. If the user rejects
something, add the rule to `docs/03-SCENE_CINEMATIC.md` so every future chapter inherits it.
That document should grow over a build. It is the memory of the project.
