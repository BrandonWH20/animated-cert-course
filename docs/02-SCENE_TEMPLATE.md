# Scene Template — building one chapter to spec

The reusable recipe. `animations/_template/` is the worked reference — open it alongside this doc.
Follow this and you can build a chapter without re-deriving anything.

## The one rule that matters

The real podcast audio is muxed over the concatenated scenes, so **your scene's total `run_time`
+ `wait` MUST equal `end - start` from `chapters.json` for your chapter.** Drift must be < 0.5s;
aim for < 0.1s. Everything below exists to hit that number exactly while keeping the right visual
on screen while its narration plays.

Look up your chapter's window in `chapters.json`: `start`, `end`, `scene_class`, `slug`,
`key_visuals`. **Your target duration = `end - start`.**

---

## Step 1 — Read your transcript window

Do NOT guess the narration. Pull the exact segments for your window:

```bash
.venv/bin/python -c "
import json
d=json.load(open('courses/<cert>/transcript/transcript.json'))
START, END = 261.16, 471.30          # <-- your chapter's start/end
for s in d['segments']:
    if s['start'] < END and s['end'] > START:
        print(f\"[{s['start']:7.2f}-{s['end']:7.2f}] {s['text'].strip()}\")
"
```

`segments[i]['words']` has word-level timestamps when you need finer placement.

Group the segments into **6–12 beats**, one idea each. A beat's visual must be on screen while
its narration plays. Convert every transcript timestamp to **chapter-relative** by subtracting
your `start`, so beat targets run `0 → end-start`.

## Step 2 — Write `script.md` first

The script drives the animation, not the reverse. Copy `animations/_template/script.md` exactly:

- Header naming the chapter, the audio window, and the sync contract.
- One `## Beat: <Name>  *(~Ns · start–end)*` per beat, each with **On screen:** and
  **Narration:** (the real transcript text for that span).
- **Beat names must be unique** and become the `next_section()` names verbatim.
- The `~Ns` values must sum to your target duration.

## Step 3 — Write `scene.py`

The import block is mandatory and identical across scenes:

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from manim import *
from shared.theme import PALETTE, beat_title

config.background_color = "#0b0b0f"
BLUE=PALETTE["blue"]; TEAL=PALETTE["teal"]; GREEN=PALETTE["green"]
AMBER=PALETTE["amber"]; RED=PALETTE["red"]; PURPLE=PALETTE["purple"]
INK=PALETTE["ink"]; MUTED=PALETTE["muted"]

# Cumulative beat-END targets, chapter-relative. LAST value == end - start.
T = {
    "BeatOne":  18.80,
    "BeatTwo":  52.90,
    "LastBeat": 210.14,      # == chapters.json end - start
}
```

### The timing engine — copy verbatim, do not reinvent

```python
    def P(self, *anims, run_time=1.0, **kw):
        """Play and bank the time."""
        self.play(*anims, run_time=run_time, **kw); self.clock += run_time

    def W(self, dt):
        """Wait and bank the time."""
        if dt > 0: self.wait(dt); self.clock += dt

    def sync_to(self, target):
        """Absorb whatever is left up to an absolute cumulative target."""
        self.W(round(target - self.clock, 3))

    def over(self, dt, *anims, rate_func=linear, **kw):
        """Animate continuously for exactly dt seconds (replaces a dead wait)."""
        dt = round(dt, 3)
        if dt <= 0: return
        self.play(*anims, run_time=dt, rate_func=rate_func, **kw); self.clock += dt

    def sync_over(self, target, *anims, **kw):
        """Fill the gap to `target` with PURPOSEFUL motion instead of waiting."""
        self.over(round(target - self.clock, 3), *anims, **kw)

    def title(self, text, color=INK, rt=0.6):
        t = beat_title(self, text, color=color, run_time=rt); self.clock += rt; return t

    def txt(self, s, size=32, color=INK, weight=NORMAL):
        return Text(s, font="sans-serif", font_size=size, color=color, weight=weight)
```

### Why this always lands

`self.clock` accumulates every `run_time` and every `wait`. Targets are stored as **absolute
cumulative** end times, so `sync_to(target)` waits out `target - clock`. After each beat the
clock equals that beat's target exactly.

This makes the design **self-correcting**: if one beat's animations run a little long, the next
`sync_to` simply waits less. **You never hand-add run times.** The final `sync_to(T["LastBeat"])`
forces the summed timeline to exactly `end - start`.

The only failure mode is a beat whose animations overrun so far that the clock passes a later
target — then `sync_to` waits 0 and the scene ends long. Keep each beat's animated time
comfortably under its budget.

To place a reveal at a specific moment *inside* a beat, `sync_to(<offset>)` before the `P(...)`.

### `construct` shape

```python
    def construct(self):
        self.clock = 0.0
        self.next_section("BeatOne"); self.beat_one()
        self.next_section("BeatTwo"); self.beat_two()
        # one next_section + one method per beat, names EXACTLY matching script.md
        self.W(0.19)   # frame-rounding tail pad — see below
```

### Frame-rounding compensation

Manim renders each animation as a whole number of frames at 30fps, so ~N animations lose up to
~N/2 frames total. A 92-animation chapter came in **0.19s short** of the summed clock.

Fix: after the final `sync_to`, add one small pad `self.W(0.19)`. Render, check drift, adjust the
pad by the residual. **This is the ONLY place you tune to kill drift.** Don't chase it per beat.

## Step 4 — `meta.yaml`

Copy the template's. Set `id` / `title` / `series`, `scene_class` to your class name,
`target_duration_s` to `round(end-start)`, `status: draft`. Keep the `publish:` block.

## Step 5 — Render

```bash
make render ANIM=<slug>        # draft 720p
make render-hi ANIM=<slug>     # final 1080p
```

Output lands at `animations/<slug>/renders/videos/scene/720p30/<SceneClass>.mp4`.

## Step 6 — Check drift and tune

```bash
make check COURSE=courses/<cert>/chapters.json
```

Find your chapter's row: `target` vs `render` vs `drift`. Other chapters show `MISSING RENDER` —
ignore them until built. Tune the tail pad and re-render until drift < 0.1s. Large negative drift
means a beat overran — trim run times. Small negative (0.1–0.2s) is frame rounding — bump the pad.

## Step 7 — Frame QA (mandatory before reporting done)

```bash
ffmpeg -ss <t> -i <render> -frames:v 1 /tmp/frame_<t>.png
```

Sample every ~3s across the render, plus every label reveal and camera move. Check each for text
overlapping text, labels crossing the frame edge, elements escaping their boxes. See the
zero-overlap bar in `03-SCENE_CINEMATIC.md`. **A render that completes without error is not a
render that is correct.**

---

## Pitfalls — all of these cost a real re-render

- **NO LaTeX, ever.** `Text`/`MarkupText` only; `MathTex`/`Tex` hard-fail. Unicode `≈ → · Σ √`
  is fine in a `Text` string. Write math as words.
- **`next_section` names must match `script.md` beat names exactly.** That's the contract lock.
- **`scene_class` in `meta.yaml` must equal the Python class name**, or the Makefile renders nothing.
- **Don't call `beat_title()` without banking its time** — it calls `scene.play()` internally and
  is not tracked by `self.clock`. Use the `self.title()` helper.
- **Size text with `font_size=`, not `.scale()`**, for predictable layout.
- **Persist shared mobjects on `self`** if a later beat mutates them.
- **Never pass a bound method (`self._fn`) to `ax.plot(...)`.** `ParametricFunction` stores the
  callable and `Create()` deepcopies it — a bound method drags in the Scene, whose thread lock is
  unpicklable → hard `TypeError: cannot pickle '_thread.lock'`. Define plot functions at module
  level, or use a `lambda` that closes over nothing.
- **`DecimalNumber` pulls in LaTeX.** It defaults to `mob_class=MathTex` and will hard-fail with
  `FileNotFoundError: 'latex'`. `mob_class=Text` fixes that but still won't accept a `font=`
  kwarg (kwargs go to `Mobject`, not the mob class). For a live counter, use
  `always_redraw(lambda: Text(f"{tracker.get_value():.2f}", font="sans-serif", ...))` instead.
  **Close over the tracker and target mobject — never over `self`.**
- **`MoveAlongPath(Dot(...), edge)` adds that dot to the scene and it will survive into later
  beats** — and, because scenes are concatenated, into the *next chapter's* frames. Keep a handle
  on anything you animate into existence and fade it with the rest of the beat's group.
- **`set_width(w, stretch=False)` raises** `TypeError: setter() got an unexpected keyword
  argument 'stretch'` on a `Text`. Size text with `font_size=`; align columns by positioning, not
  by forcing widths.
- **Build a beat's full composition before revealing it.** Position everything — including the
  brace, total, or callout that appears at the end — then center the whole group, then animate
  the reveals. Placing elements incrementally is how labels end up running off the frame edge.
- **`Text` glyph-slice indexing is fragile** (spaces are excluded from glyph submobjects, so
  indices drift). To highlight a phrase, build it as its own `Text` inside a `VGroup().arrange()`
  and box that piece.
- **`np` is not guaranteed by `from manim import *`** — `import numpy as np` explicitly if you
  compute coordinates.
- **`Arrow`:** set `max_tip_length_to_length_ratio` (0.2–0.35) or short arrows get giant tips.
- **Letter/token tiles must not accidentally spell words.** A row reading `L O W E R S T` scans
  as a misspelled "LOWEST". Separate with dots or braces, or group so it can't be parsed as one word.
- **Spell-check every string** before the final render. A typo in a training video destroys its
  credibility instantly.
