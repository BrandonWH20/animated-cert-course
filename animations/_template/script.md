# Narration Script — Template Chapter

*Course: `example-course` · Chapter 1 · Scene: `TemplateChapter`.*
*Window in source audio: **0.0s – 60.0s** (target scene duration **60.0s**).*
*SYNC CONTRACT: the ORIGINAL podcast audio is muxed over the concatenated scenes. Each `## Beat`
below maps 1:1 to a `self.next_section("<name>")` in `scene.py` (names identical). The scene's
total `run_time`+`wait` MUST equal 60.0s so narration stays locked to visuals.*
*Tier: beat 2 is HERO (coordinate grounding, camera push, live computed number); beats 1 and 3
are CONNECTIVE but still assemble and reorganize — never a pre-built board. NO LaTeX.*

---

## Beat: OpeningFrame  *(~18s · 0.0–18.0)*
**On screen:** Composed opener. The chapter title lands, then three condition chips assemble one
at a time beneath it — each in its own semantic color, which it keeps for the rest of the chapter.
The final arrangement is the hero still; it is deliberately held, not pulsed.
**Narration:** "Replace this with the real transcript text for this span. Pull it from the
transcript JSON — do not paraphrase from memory, because the visual has to land on the words that
are actually spoken."

## Beat: MechanismDraw  *(~24s · 18.0–42.0)*
**On screen:** The hero beat. Three colored input dots sit in real axes coordinates; each is
scaled by its weight, then a dot of charge flows down each edge into a summing node while a live
decimal readout counts the running total up to 1.90. The camera pushes in on the node as the
total settles, then pulls back out. One figure, continuously transformed — no fade-swaps.
**Narration:** "The narration for the mechanism goes here. Because this beat explains how
something works rather than naming it, it earns the full treatment: coordinate grounding, a
camera move, and a number that visibly computes rather than being captioned."

## Beat: WeightedChart  *(~18s · 42.0–60.0)*
**On screen:** The five exam domains assemble as labelled bars growing rightward, each percentage
counting up live as its domain is named. Then the chart reorganizes: the bottom two bars dim, a
brace gathers the top three, and a total counts up beside it. The last frame is the full
comparison, left up to be studied.
**Narration:** "The closing narration. Notice that a taxonomy still has to grow and reorganize
rather than appear pre-built — that is the difference between a comparison a learner can study
and a table that was pasted on screen."

### Full read
Replace all three narration blocks above with the real transcript text for the window, then set
the cumulative targets in `scene.py`'s `T` dict to the beat boundaries.
