# Prompts — the two sets

A build like this runs on two completely different kinds of prompt, and they fail in different
ways. Knowing which one you're writing saves a lot of wasted audio and a lot of wasted renders.

| | Set 1 — Audio | Set 2 — Code |
|---|---|---|
| **Target** | NotebookLM Audio Overview | A coding agent (Claude Code, Codex, …) |
| **Job** | Teach the module out loud | Draw the mechanism to spec |
| **Form** | One prompt per module, pasted into Customize | Markdown specs checked into this repo |
| **Lives** | `templates/PODCAST-PROMPT.md` → module `Documents/` | `AGENTS.md` + `docs/` |
| **Fails as** | Fluff, preamble, explain-like-I'm-5 | Animated bullet points, overlapping text |
| **Fix** | Rewrite the prompt *and* the source | Write the rule into `03-SCENE_CINEMATIC.md` |

---

## Set 1 — The Audio Overview prompt

One per module. Paste into NotebookLM → Audio Overview → Customize. Three directives do the work.

### 1. No preamble

Without this, every episode burns its first 3–5 minutes re-reciting exam logistics, domain
weights, price, and study strategy. Use close to verbatim:

> **No preamble — start the lesson immediately.** Do not open with exam logistics, domain
> weightings, question counts, price, validity, or study-strategy talk; the course overview
> episode already covered all of that and repeating it wastes minutes. No extended welcome or
> host banter. Within the first thirty seconds, state in one sentence what this module teaches,
> then dive straight into the first concept. If the source chunks open with exam-domain framing,
> skip past it. Exam domains and weights may be mentioned at most once, in passing, mid-episode —
> never as an opening.

**Do not** write "be honest about exam logistics" anywhere in the prompt. That's an invitation to
the recital.

### 2. Practitioner depth, not ELI5

The review note that forced this rule on the original build: *"feels explain-like-I'm-5; 20
minutes in, only a few terms learned."*

> **Practitioner depth, not ELI5.** Assume the listener is a working engineer preparing for a
> professional certification — move fast and go deep. Use precise technical terminology
> throughout; at most ONE brief analogy per concept, then return to the mechanism itself. Speak
> the real numbers, dimensions, and formulas aloud rather than waving at them. Never re-explain a
> term after its first definition, and never pad with reassurance ("don't worry, this sounds
> complicated"). A listener 20 minutes in should have learned a dozen precise concepts, not a few
> terms. Density and pace are the point of a deep dive.

Adjust for a beginner audience if that's genuinely who you're serving — but decide once, up
front. It's hard to change after the knowledge bases are written.

### 3. Walk the chunks in order, and name the traps

The body of the prompt is an ordered agenda plus the specifics. Include:

- **The chunk list, in order**, with the time each deserves — mirroring the KB's `##` sections.
- **Terms to define on first use.** List them explicitly.
- **The exam traps to call out.** Be concrete. From the reference build: *the attention scaling
  divisor is the square root of the key dimension, not sequence length; heads are concatenated,
  not averaged; layer norm, not batch norm; the KV cache stores keys and values, never queries.*
- **What NOT to drift into**, because a later module owns it.
- **Three self-check questions** to close on.
- **Which exam domains this feeds**, mentioned once, for the listener's prioritization.

### The thing that actually gates quality

**The source sets the ceiling, not the prompt.** If your Podcast Source chunks open with "welcome
to module two" and domain-weight framing, you will hear it in the audio no matter what the prompt
says. The original build had to go back and rewrite every source file to this standard before the
audio got good:

- No domain-weight or exam-logistics framing anywhere in the chunks.
- No "welcome to module N" openings.
- No reassurance filler.
- The KB's worked numeric examples written out in spoken prose.

---

## Set 2 — The coding-agent prompts

These are not prompts you type. **They're the markdown in this repo**, which the agent reads
before it writes a scene. Four files, four jobs:

- **`AGENTS.md` / `CLAUDE.md`** — the workflow and the failure modes. Answers *"what am I doing,
  in what order, and what will I get wrong?"*
- **`docs/01-CONVENTIONS.md`** — layout, naming, the three-way sync lock, house style, guardrails.
  Answers *"what does code in this repo look like?"*
- **`docs/02-SCENE_TEMPLATE.md`** — the per-chapter recipe: pull your transcript window, group it
  into beats, copy the timing engine, hit your duration, tune the pad, check drift. Answers *"how
  do I build one unit to spec?"*
- **`docs/03-SCENE_CINEMATIC.md`** — how the screen must behave. Answers *"what does good look
  like?"* This is the one that grows.

### Why written specs beat chat instructions

Three reasons, all of which showed up in the original build:

1. **A rule in a file applies to every future chapter for free.** A rule in a chat message
   applies until the context window turns over.
2. **Parallel agents can't share your chat.** When you fan out to build 12 chapters at once,
   the spec files are the only thing all of them read.
3. **Writing the rule forces you to make it precise.** "Make it more visual" is not actionable;
   "one object persists and morphs instead of fade-out/fade-in" is.

### The spec is supposed to contradict itself over time

In the reference build, `03-SCENE_CINEMATIC.md` explicitly overrides the earlier template's
"holds should dominate" guidance. That's not sloppiness — it's the record of a correction:

1. First the scenes were too busy, so the rule became *holds should dominate.*
2. Then they read as animated bullet points, so the rule became *transform, don't swap.*
3. Then the agent filled every gap with looping scale-pulses to avoid holding still, so the rule
   became *motion must mean something, or hold a composed still.*

Each rejection narrowed the target. **That's the loop to run: reject, write the rule, re-render.**
Don't re-prompt the same correction twice — if you're saying it again, it belongs in a file.
