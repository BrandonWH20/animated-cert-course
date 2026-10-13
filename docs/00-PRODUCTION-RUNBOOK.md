# Production Runbook — building a module end to end

*Operational detail. `AGENTS.md` is the workflow; this is the environment and the per-module
mechanics.*

## Environment

```bash
make setup          # python3 -m venv .venv && pip install -r requirements.txt
```

- **Manim Community 0.21** — `Text`/`MarkupText` only, no LaTeX install required (and none is
  used; `MathTex` will hard-fail by design).
- **ffmpeg / ffprobe** on PATH. macOS: `brew install ffmpeg cairo pango pkg-config`.
  Debian/Ubuntu: `apt install ffmpeg libcairo2-dev libpango1.0-dev pkg-config`.
  Override discovery with `FFMPEG=` / `FFPROBE=` env vars if needed.
- **Transcription:** `mlx-whisper` is fastest on Apple Silicon. Elsewhere use
  `openai-whisper` or `faster-whisper` — any engine that emits **word-level** timestamps.

Run every command from the repo root.

## Transcription

```bash
.venv/bin/mlx_whisper "<audio>.m4a" \
  --model mlx-community/whisper-large-v3-turbo \
  --output-dir courses/<cert>/transcript --output-format all \
  --language en --word-timestamps True
```

Produces `.json` (segment **and word** timestamps — word timings drive beat placement), `.srt`,
`.txt`. Roughly 55 minutes of audio transcribes in a few minutes on an M-series machine.

## The Documents bucket — three files per module, exactly

1. `<Cert> M<NN> - <Topic> - Knowledge Base.md` — the written courseware. `##` sections define
   the chapter structure.
2. `<Cert> M<NN> - <Topic> - Podcast Source.md` — read-aloud chunks only, one per KB section.
   Upload this file whole as the NotebookLM source.
3. `<Cert> M<NN> - <Topic> - Podcast Prompt.md` — the Audio Overview customization prompt.

**Do not combine source and prompt.** A combined file leaks instructions into the audio.

See `docs/04-PROMPTS.md` for what goes in the prompt — the two directives there are the
difference between usable audio and fifty minutes of nothing.

## Producing a module — two patterns

### Pattern A — synced to podcast (the default; what this template is built for)

Animation is frame-locked to a real recording; the original audio is muxed over it. No TTS.

1. Transcribe the podcast.
2. Segment into topic chapters with exact start/end → `chapters.json`.
3. Author one Manim scene per chapter per `docs/02-SCENE_TEMPLATE.md`. The timing engine makes
   each scene's runtime equal its audio span exactly.
4. Render: `make render ANIM=<slug>` (draft) / `make render-hi ANIM=<slug>` (1080p).
5. Check: `make check COURSE=courses/<cert>/chapters.json` → drift < 0.5s/chapter, aim < 0.1s.
6. Assemble: `make assemble COURSE=courses/<cert>/chapters.json` → concat + mux → one mp4.

> Scaling: prove chapter 1 by hand and write down what you did, *then* fan out. Parallel agents
> cloning a proven template produce a course; parallel agents improvising produce N experiments.

### Pattern B — standalone explainer set

Independent explainers, each its own concept, assembled into a module video. No audio lock;
narration is a script you can voice later (`manim-voiceover` is the upgrade path). Use this when
there's no podcast to sync against.

## Render budget

A 260-second chapter with ~90 animations renders in roughly 20 seconds at 720p on an M-series
laptop. A full 55-minute module is roughly 4–5 minutes of render time. Scales with animation
count and complexity, not just duration. 1080p and 4K cost proportionally more.

## Publishing

- Draft/review cuts → `courses/<cert>/renders/`, then copy where you keep deliverables.
- Name: `YYYY-MM-DD_<module>_<scope>_<quality>.mp4`.
- `meta.yaml` per animation tracks per-platform publish status so nothing gets lost across
  YouTube / course platform / blog.

## Revision loop

Feedback comes by chapter. Scenes are independent: edit that scene, re-render it, re-assemble,
drop a new dated cut. No full rebuild.

**Write every accepted correction into `docs/03-SCENE_CINEMATIC.md`.** That file is the project's
memory; a rule written there applies to every future chapter for free.
