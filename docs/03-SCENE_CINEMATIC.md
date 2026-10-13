# Scene Cinematic — the quality bar

The sync mechanics in `02-SCENE_TEMPLATE.md` still apply (clock, `sync_to`, drift < 0.1s,
frame-rounding pad, matching beat names, no LaTeX, palette from `shared/theme.py`). What this
document governs is **how the screen behaves between the narrated reveals.**

> **This file is the project's memory.** Every rule below exists because a render was rejected.
> When your user rejects something, add the rule here — then every future chapter inherits it,
> and you stop re-litigating the same note every session.

## The core problem this fixes

The naive way to hit sync is to hold still: `FadeIn` objects → `wait` → `FadeOut` → place the
next set. **That reads as animated bullet points** and it is the single most common failure. The
cure is the seven moves below. The first two are mandatory on every beat.

---

## The seven moves

### 1. Transform, don't swap *(mandatory)*

One object **persists and morphs** into the next idea instead of new-fades-in / old-fades-out.

```python
self.P(ReplacementTransform(sum_node, activation_node), run_time=0.8)   # shape → shape
self.P(TransformMatchingShapes(label_a, label_b), run_time=0.7)         # Text → Text
self.P(Transform(vec, vec.copy().rotate(PI/6)), run_time=0.6)           # in place
```

The eye tracks ONE evolving object, and that continuity *is* the explanation. Only `FadeIn`
something genuinely new. Never fade one thing out just to fade a sibling in.

### 2. Purposeful motion — or a composed still *(mandatory)*

> **Hard rule, learned the hard way:** motion must mean something or be imperceptible. NEVER
> loop a scale-pulse ("breathing") on blocks, circles, or any primitive, and never continuously
> expand/contract shapes to fill time. Constant pulsing reads as distracting fidget, not film.
>
> A short, well-composed **still is NOT a slideshow.** The slideshow was a *frozen, uncomposed
> board.* When you have nothing purposeful to animate, hold a clean frame and let it breathe.
> **Prefer stillness over decorative motion, every time.**

Fill a gap with motion ONLY when the motion carries meaning: an operating point sliding along a
curve, a value ticking via `ValueTracker`, data flowing down an edge, a structure assembling or
reorganizing, a label settling into place, or a **one-way** camera ease that *settles* into a
resting composition (never a repeating in/out loop).

```python
# OLD (slideshow):  self.sync_to(T["Beat"])          # screen frozen on an uncomposed board
# NEW (alive):      self.sync_over(T["Beat"], flow.animate.increment_value(3), rate_func=linear)
# ALSO FINE:        self.sync_to(T["Beat"])          # composed frame, deliberately held
```

If the gap has no meaningful motion, use `sync_to` and hold. A calm 3–6s hold of a good frame is
often better than movement.

### 3. One evolving focus, not a populated board *(hero beats)*

Build a SINGLE central figure and elaborate it — annotations grow off it, it rotates to reveal
structure. Avoid scorecards and column-grids as the primary device; those are the slideshow tell.
If you must list, let the list *assemble out of* the figure, not sit beside it.

### 4. Move the camera *(hero beats)*

Base the scene on `MovingCameraScene`. Push in on the detail under discussion, pull back for context.

```python
class YourScene(MovingCameraScene):                                              # not Scene
    self.P(self.camera.frame.animate.scale(0.5).move_to(node), run_time=1.0)     # push in
    self.P(self.camera.frame.animate.scale(2.0).move_to(ORIGIN), run_time=1.0)   # pull back
```

Reset the frame before the scene ends so concatenation is seamless.

### 5. Ground it in space *(hero beats — the substitute for LaTeX)*

Wherever a concept has a spatial model, draw it in real coordinates:

```python
ax = Axes(x_range=[-4,4,1], y_range=[0,1,0.5], x_length=6, y_length=3)
curve = ax.plot(sigmoid, color=TEAL)                           # module-level fn, not a method
dot = Dot(ax.c2p(x0, sigmoid(x0)), color=AMBER)
vec = Arrow(ax.c2p(0,0), ax.c2p(2,1.5), buff=0, color=BLUE)
```

`Axes`, `NumberPlane`, `Arrow`, `Vector`, `DecimalNumber` + `ValueTracker`, `always_redraw` are
the rigor toolkit. A number that counts via a tracker reads as *computed*, not captioned.

### 6. Color = identity *(mandatory where quantities recur)*

A quantity keeps its color across every transformation, so when a blue vector flows into a new
position it is still "that input." Assign a semantic color per quantity once, then reuse it for
the whole chapter.

### 7. Easing and a per-beat arc *(all beats)*

- `smooth` for reveals, `there_and_back` for a single emphasis pulse, `linear` for ambient flow.
- Stagger grouped reveals: `self.P(LaggedStart(*anims, lag_ratio=0.2), run_time=1.2)`.
- Shape every beat as **setup → transform → settle**: pose the question visually, let the
  transform resolve it, let it breathe. That micro-arc is the "aha."

---

## Tiering — don't full-derive everything

A 55-minute module can't be 13 hero chapters; you'd never finish, and it would exhaust the viewer.

**HERO beats** — the mechanism *is* the lesson. Full treatment: moves 1–7, coordinate space,
camera, continuous transformation. Reserve these for the concepts the exam actually turns on.

**CONNECTIVE beats** — lists, taxonomies, stack diagrams, exam heuristics. Cleaner, BUT never
static: moves 1, 2, 6, 7 still apply. A taxonomy should *grow and reorganize* (items sliding into
groups) rather than appear pre-built. A stack should *assemble layer by layer* with a dot of data
flowing through it, not pop in as a table.

**Rule of thumb:** if the narration explains **how or why something works**, it's hero. If it's
**naming or enumerating**, it's connective.

---

## Worked micro-example — one beat, before and after

Narration (~6s): *"Each input is multiplied by its weight, and the neuron sums them."*

**Before (slideshow):**

```python
eq = self.txt("output = Σ wᵢ·xᵢ", size=40)
self.P(FadeIn(eq)); self.sync_to(T["Beat"]); self.P(FadeOut(eq))
```

**After (cinematic):**

```python
# three input dots already on screen, persistent and color-coded.
total = ValueTracker(0.0)
readout = always_redraw(lambda: DecimalNumber(total.get_value(), num_decimal_places=2,
                                              color=AMBER).next_to(sum_node, UP))
self.add(readout)
flows = [MoveAlongPath(Dot(color=c), edge) for c, edge in zip(IN_COLORS, edges)]
self.P(LaggedStart(*flows, lag_ratio=0.25),
       total.animate.set_value(weighted_sum), run_time=2.2, rate_func=linear)
self.P(self.camera.frame.animate.scale(0.6).move_to(sum_node), run_time=0.8)
self.sync_to(T["Beat"])        # composed hold — the sum sits on screen; no decorative pulsing
```

Same 6 seconds, same sync landing — but one persistent figure computes the sum in front of you,
then rests. The motion *was* the computation, not a fidget added afterward.

---

## Build checklist

- [ ] `script.md` with one `## Beat:` per beat; names == `next_section` names == method names.
- [ ] `scene.py` on `MovingCameraScene` (hero) or `Scene` (connective); timing engine copied in.
- [ ] Gaps with meaningful motion use `sync_over`; otherwise a composed `sync_to` hold. **No
      looping scale-pulse / "breathing" on any shape.**
- [ ] At least one persistent object that transforms across the beat — no fade-swap pairs.
- [ ] Hero beats: coordinate grounding + camera move + a live computed number.
- [ ] Semantic colors consistent across transforms.
- [ ] Every string spell-checked, including transcription-garbled technical terms.
- [ ] **ZERO overlap — non-negotiable.** No two text/label mobjects may share screen space, and
      nothing may collide with the central figure, an axis, or a persistent element.
      Dangerous moments: (a) a new label arriving while an old one is still fading; (b) a camera
      zoom bringing two elements into the same tight frame; (c) a live number or caption landing
      on a curve or node. Defenses: position with `.next_to()` / `.to_edge()` plus explicit
      `buff`; before adding a label, fade out or move whatever occupied that spot; when zoomed,
      verify labels inside the zoom box don't touch. **Verify by sampling frames every ~3s
      across the whole render** — not just a handful of spread-out frames — plus at every label
      reveal and camera-move boundary. An overlap anywhere is a build failure.
- [ ] Drift < 0.1s for the chapter; tail pad tuned.
- [ ] No distracting looping motion anywhere. Composed stills are fine; fidgety pulsing is not.
