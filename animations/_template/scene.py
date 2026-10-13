"""
_template / scene.py
--------------------
The worked reference chapter. COPY THIS FOLDER to start a new chapter.

SYNC CONTRACT (see courses/example-course/chapters.json):
  The real podcast audio (0.0s-60.0s) is muxed over this scene, so the scene's TOTAL
  run_time+wait MUST equal 60.0s. Each beat is wrapped in self.next_section("<Name>")
  matching a "## Beat: <Name>" in script.md exactly.

Demonstrates, in order: the timing engine (P/W/sync_to/over/sync_over), transform-not-swap,
a composed held still, coordinate grounding, a camera push-in that settles, a live computed
number, semantic color identity, and a taxonomy that assembles then reorganizes.

NO LaTeX anywhere (Text/MarkupText only). Palette from shared/theme.py.

Render (draft 720p):  make render ANIM=_template
Check drift:          make check COURSE=courses/example-course/chapters.json
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import numpy as np
from manim import *
from shared.theme import PALETTE, beat_title

config.background_color = "#0b0b0f"

BLUE   = PALETTE["blue"]
TEAL   = PALETTE["teal"]
GREEN  = PALETTE["green"]
AMBER  = PALETTE["amber"]
RED    = PALETTE["red"]
PURPLE = PALETTE["purple"]
INK    = PALETTE["ink"]
MUTED  = PALETTE["muted"]

# Semantic color per quantity — assigned once, reused for the whole chapter (move 6).
IN_COLORS = [BLUE, TEAL, PURPLE]
WEIGHTS   = [0.5, 0.8, 0.4]
INPUTS    = [1.0, 1.5, 0.5]
TOTAL     = sum(w * x for w, x in zip(WEIGHTS, INPUTS))   # 1.70

# Example taxonomy for beat 3 — swap for the real exam domains.
DOMAINS = [
    ("Core concepts",   30, BLUE),
    ("Implementation",  24, TEAL),
    ("Operations",      22, GREEN),
    ("Analysis",        14, AMBER),
    ("Governance",      10, PURPLE),
]

# Cumulative beat-END targets (chapter-relative seconds). LAST value == end - start.
T = {
    "OpeningFrame":  18.0,
    "MechanismDraw": 42.0,
    "WeightedChart": 60.0,
}

TAIL_PAD = 0.0    # frame-rounding compensation — tune from `make check`, nowhere else


class TemplateChapter(MovingCameraScene):
    # ---- timing engine (copy verbatim into every scene) ----
    def P(self, *anims, run_time=1.0, **kw):
        self.play(*anims, run_time=run_time, **kw); self.clock += run_time

    def W(self, dt):
        if dt > 0: self.wait(dt); self.clock += dt

    def sync_to(self, target):
        self.W(round(target - self.clock, 3))

    def over(self, dt, *anims, rate_func=linear, **kw):
        dt = round(dt, 3)
        if dt <= 0: return
        self.play(*anims, run_time=dt, rate_func=rate_func, **kw); self.clock += dt

    def sync_over(self, target, *anims, **kw):
        self.over(round(target - self.clock, 3), *anims, **kw)

    def title(self, text, color=INK, rt=0.6):
        t = beat_title(self, text, color=color, run_time=rt); self.clock += rt; return t

    def txt(self, s, size=32, color=INK, weight=NORMAL):
        return Text(s, font="sans-serif", font_size=size, color=color, weight=weight)

    # ---- one next_section + one method per beat, names EXACTLY matching script.md ----
    def construct(self):
        self.clock = 0.0
        self.next_section("OpeningFrame");  self.opening_frame()
        self.next_section("MechanismDraw"); self.mechanism_draw()
        self.next_section("WeightedChart"); self.weighted_chart()
        self.W(TAIL_PAD)

    # ------------------------------------------------------------------ beat 1
    def opening_frame(self):
        """CONNECTIVE: chips ASSEMBLE one at a time, then the frame is held composed."""
        eyebrow = self.txt("EXAMPLE COURSE  ·  CHAPTER 1", size=20, color=MUTED).to_edge(UP, buff=1.5)
        head    = self.txt("The Template Chapter", size=54, weight=BOLD).next_to(eyebrow, DOWN, buff=0.45)
        self.P(FadeIn(eyebrow, shift=DOWN * 0.2), run_time=0.8)
        self.P(Write(head), run_time=1.6)

        chips = VGroup()
        for label, color in [("sync contract", BLUE), ("one idea per beat", TEAL), ("no LaTeX", PURPLE)]:
            t = self.txt(label, size=26, color=color)
            box = SurroundingRectangle(t, corner_radius=0.18, buff=0.28,
                                       stroke_width=2, color=color)
            chips.add(VGroup(box, t))
        chips.arrange(RIGHT, buff=0.55).next_to(head, DOWN, buff=0.9)

        # LaggedStart staggers the reveal (move 7) — the chips build, they don't pop in as a row.
        self.P(LaggedStart(*[FadeIn(c, shift=UP * 0.25) for c in chips], lag_ratio=0.35),
               run_time=2.0)

        # A composed still, deliberately held. NOT a slideshow — and no decorative pulsing.
        self.sync_to(T["OpeningFrame"] - 0.7)
        self.P(FadeOut(VGroup(eyebrow, head, chips)), run_time=0.7)
        self.sync_to(T["OpeningFrame"])

    # ------------------------------------------------------------------ beat 2
    def mechanism_draw(self):
        """HERO: coordinate grounding + camera push that settles + a live computed number."""
        title = self.title("Inputs, weights, and a sum")

        ax = Axes(x_range=[0, 4, 1], y_range=[0, 3, 1], x_length=6.2, y_length=3.4,
                  axis_config={"include_tip": False, "stroke_color": MUTED,
                               "stroke_width": 2}).shift(DOWN * 0.45 + LEFT * 1.4)
        self.P(Create(ax), run_time=1.2)

        # Three inputs placed in REAL coordinates, each keeping its semantic color.
        dots, labels, edges = VGroup(), VGroup(), VGroup()
        sum_pt = ax.c2p(3.6, 1.5)
        for i, (x, w, c) in enumerate(zip(INPUTS, WEIGHTS, IN_COLORS)):
            pt = ax.c2p(0.5, 2.4 - i * 0.9)
            d = Dot(pt, radius=0.11, color=c)
            # Park labels OUTSIDE the axes and right-align them to a shared edge. Placing them
            # next_to(dot, LEFT) ran them straight through the y-axis — a text-on-figure collision.
            lab = self.txt(f"x{i+1} = {x}   w{i+1} = {w}", size=20, color=c)
            lab.move_to([ax.get_left()[0] - 0.4 - lab.width / 2, pt[1], 0])
            e = Line(pt, sum_pt, stroke_width=2, stroke_opacity=0.45, color=c)
            dots.add(d); labels.add(lab); edges.add(e)

        node = Circle(radius=0.34, color=AMBER, stroke_width=3).move_to(sum_pt)
        node_lab = self.txt("sum", size=18, color=AMBER).next_to(node, DOWN, buff=0.22)

        self.P(LaggedStart(*[FadeIn(d, scale=0.5) for d in dots], lag_ratio=0.2), run_time=1.0)
        self.P(LaggedStart(*[FadeIn(l) for l in labels], lag_ratio=0.2), run_time=1.0)
        self.P(LaggedStart(*[Create(e) for e in edges], lag_ratio=0.2), run_time=1.2)
        self.P(Create(node), FadeIn(node_lab), run_time=0.8)

        # A number that COMPUTES rather than being captioned (move 5).
        total = ValueTracker(0.0)
        # A plain Text readout, NOT DecimalNumber: DecimalNumber defaults to MathTex (needs
        # LaTeX), and mob_class=Text still won't take a `font` kwarg. This closes over `total`
        # and `node` only — never over `self`, which would drag the Scene into a deepcopy.
        readout = always_redraw(lambda: Text(
            f"{total.get_value():.2f}", font="sans-serif", font_size=34,
            color=AMBER).next_to(node, UP, buff=0.3))
        self.add(readout)

        # Each input scales by its weight, then charge flows down the edge into the node.
        self.P(*[d.animate.scale(0.6 + w) for d, w in zip(dots, WEIGHTS)], run_time=0.9)
        # Keep a handle on the flowing dots — MoveAlongPath adds them to the scene, and an
        # untracked mobject will survive into the NEXT chapter's frames. (Real bug, caught in QA.)
        charges = VGroup(*[Dot(radius=0.07, color=c) for c in IN_COLORS])
        flows = [MoveAlongPath(d, e) for d, e in zip(charges, edges)]
        self.P(LaggedStart(*flows, lag_ratio=0.25),
               total.animate.set_value(TOTAL), run_time=2.4, rate_func=linear)

        # One-way camera ease that SETTLES (move 4) — never a repeating loop. Lean in on the
        # whole mechanism, not just the node: a tighter push cropped the inputs out of frame.
        figure = VGroup(ax, dots, labels, edges, node, node_lab)
        self.P(self.camera.frame.animate.scale(0.82).move_to(figure), run_time=1.1)
        self.sync_to(T["MechanismDraw"] - 2.2)

        # Reset the frame before the scene ends so concatenation is seamless.
        self.P(self.camera.frame.animate.scale(1 / 0.82).move_to(ORIGIN), run_time=1.1)
        self.remove(readout)
        self.P(FadeOut(VGroup(title, figure, charges)), run_time=0.7)
        self.sync_to(T["MechanismDraw"])

    # ------------------------------------------------------------------ beat 3
    def weighted_chart(self):
        """CONNECTIVE but never static: the taxonomy ASSEMBLES, then REORGANIZES."""
        title = self.title("Where the weight actually sits")

        # Build the ENTIRE composition up front — including the brace and tally that appear
        # later — then center it as one group. Positioning reveals incrementally is how text
        # ends up running off the frame edge; reserving the space first makes that impossible.
        labels = VGroup(*[self.txt(name, size=22, color=INK) for name, _, _ in DOMAINS])
        labels.arrange(DOWN, buff=0.42, aligned_edge=LEFT)

        bar_x = labels.get_right()[0] + 0.45
        rows, bars = VGroup(), []
        for lab, (name, pct, color) in zip(labels, DOMAINS):
            bar = Rectangle(width=pct * 0.13, height=0.32, color=color,
                            fill_color=color, fill_opacity=0.85, stroke_width=0)
            bar.move_to([bar_x + bar.width / 2, lab.get_center()[1], 0])
            num = self.txt(f"{pct}%", size=22, color=color).next_to(bar, RIGHT, buff=0.28)
            rows.add(VGroup(lab, bar, num)); bars.append((bar, num))

        top3 = VGroup(rows[0], rows[1], rows[2])
        brace = Brace(top3, RIGHT, color=INK)
        pct_total = sum(p for _, p, _ in DOMAINS[:3])
        tally = self.txt(f"{pct_total}% of the exam", size=24, color=INK).next_to(brace, RIGHT, buff=0.3)

        composition = VGroup(rows, brace, tally)
        composition.move_to(ORIGIN).shift(DOWN * 0.35)

        # Reveal: labels, then each bar GROWS to its weight — assembled, never pasted in.
        self.P(LaggedStart(*[FadeIn(l) for l in labels], lag_ratio=0.12), run_time=0.9)
        for bar, num in bars:
            self.P(GrowFromEdge(bar, LEFT), FadeIn(num), run_time=0.5)

        # Then it REORGANIZES: bottom two dim, a brace gathers the top three, total appears.
        self.P(rows[3].animate.set_opacity(0.3), rows[4].animate.set_opacity(0.3), run_time=0.7)
        self.P(GrowFromCenter(brace), FadeIn(tally, shift=LEFT * 0.2), run_time=0.9)

        # Final frame is the full comparison, left up to be studied.
        self.sync_to(T["WeightedChart"] - 0.7)
        self.P(FadeOut(VGroup(title, composition)), run_time=0.7)
        self.sync_to(T["WeightedChart"])
