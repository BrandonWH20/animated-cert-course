# example-course

The worked example. **Don't build here — copy the shape.**

`chapters.json` is the contract between "what was said" and "what gets drawn." Its one chapter
points at `animations/_template/`, which renders to exactly 60.0s so you can prove the toolchain
end to end before writing any real content:

```bash
make setup
make render ANIM=_template
make check COURSE=courses/example-course/chapters.json     # expect drift < 0.1s
```

`make assemble` needs `source_audio` to point at a real audio file, so it will fail here by
design — there is no 60-second episode in the repo. That step starts working once you have your
own module audio.

## Starting the real thing

1. `mkdir -p courses/<your-cert>/transcript`
2. Write `courses/<your-cert>/chapters.json` from your transcript — same schema, one entry per
   chapter, exact `start`/`end` from the transcript's topic boundaries.
3. `cp -r animations/_template animations/<your-slug>` per chapter, then rename the class in
   `scene.py` and update `meta.yaml`'s `scene_class` to match.

Full workflow: `AGENTS.md`. Per-chapter recipe: `docs/02-SCENE_TEMPLATE.md`.
