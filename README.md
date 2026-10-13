# animated-cert-course

**A template for building an animated, narrated video course for any certification exam — with
AI doing the production work and you doing the understanding.**

An AI-generated podcast is the soundtrack. Animation is frame-locked to it, 3Blue1Brown style.
The result is a companion video where every visual lands on the word being spoken.

This repo is the extracted, cert-agnostic version of a build that produced **8.8 hours of
finished courseware — 10 modules, 149 time-synced scenes.** The specs here are the ones that
build survived on, including the rules that only exist because a render got rejected.

---

## The fastest way to use this

Point a coding agent at it and tell it what you're studying:

```
Clone https://github.com/BrandonWH20/animated-cert-course and read AGENTS.md.
Let's build a course for the <YOUR CERT> exam — here's the official exam guide: <link or paste>.
```

`AGENTS.md` is written for the agent, not for you. It contains the workflow, the read order, the
step where it must stop and wait for you, and the six failure modes that cost the original build
the most time. Claude Code reads `CLAUDE.md` (identical); Codex and others read `AGENTS.md`.

## The pipeline

```
exam guide → knowledge base → podcast source + prompt → AI audio (NotebookLM)
   → transcript (word-level) → chapters.json → Manim scenes
   → render → drift check → mux original audio → module video
```

Two rules hold the whole thing together:

1. **The podcast audio is the soundtrack. No TTS, ever.** The real recording is muxed over the
   finished animation untouched.
2. **Therefore every scene's runtime must exactly equal its slice of that audio.** That single
   constraint is what makes "an AI writes the animation" tractable instead of chaos — it gives
   the model a number it either hits or misses.

## Prove the toolchain in two minutes

```bash
make setup                                              # venv + manim
make render ANIM=_template                              # renders the reference chapter
make check COURSE=courses/example-course/chapters.json   # expect drift +0.00
```

`animations/_template/` is a real, working 60-second chapter that lands on its target exactly.
It demonstrates the timing engine, transform-not-swap, a composed still, coordinate grounding, a
camera push that settles, a live computed number, semantic color, and a taxonomy that assembles
then reorganizes. **Copy that folder to start a chapter.**

## What's here

| Path | What it is |
|---|---|
| `AGENTS.md` / `CLAUDE.md` | **Agent entry point** — workflow, read order, failure modes |
| `docs/00-PRODUCTION-RUNBOOK.md` | Environment, per-module build, publishing |
| `docs/01-CONVENTIONS.md` | Layout, naming, the sync lock, house style, guardrails |
| `docs/02-SCENE_TEMPLATE.md` | Per-chapter recipe + **the timing engine** + pitfalls |
| `docs/03-SCENE_CINEMATIC.md` | The quality bar — seven moves, tiering, zero-overlap rule |
| `docs/04-PROMPTS.md` | **Both prompt sets**, with the directives that actually matter |
| `templates/` | Fill-in knowledge base, podcast source, podcast prompt |
| `animations/_template/` | The worked reference chapter (renders to exactly 60.00s) |
| `courses/example-course/` | Annotated `chapters.json` — the contract schema |
| `build/synced.py` | Per-chapter drift check + concat/mux assembly |

## The two kinds of prompt

Most of the leverage is here, and they fail in completely different ways:

- **Audio prompts** (one per module, pasted into NotebookLM) fail as *fluff* — preamble,
  exam-logistics recital, explain-like-I'm-5. Fixed with a no-preamble directive, a
  practitioner-depth directive, and by rewriting the source, which sets the real ceiling.
- **Coding-agent prompts** are the markdown in `docs/` — not chat messages. They fail as
  *animated bullet points* and *overlapping text*. Fixed by writing each rejection into
  `docs/03-SCENE_CINEMATIC.md`, where every future chapter inherits it for free.

Full treatment in `docs/04-PROMPTS.md`.

## Requirements

- Python 3.10+, **Manim Community 0.21** (no LaTeX needed — and none used)
- ffmpeg / ffprobe on PATH
- A transcription engine that emits **word-level** timestamps (`mlx-whisper` on Apple Silicon)
- NotebookLM (or any tool that generates a two-host audio overview from a source document)
- A coding agent — Claude Code, Codex, or similar

## The honest summary

AI removes the production labor, not the understanding. You never type a line of Manim or record
a word, and you still have to understand every mechanism cold — because reviewing a
confidently-wrong animation requires knowing what the right one looks like. **That review loop
is the studying. The course is a side effect.**

## License

MIT — see `LICENSE`.
