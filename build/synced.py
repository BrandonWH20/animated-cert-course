#!/usr/bin/env python3
"""Time-synced companion-video pipeline for a chapters.json course.

Two subcommands:

  check   — for each chapter, compare its RENDERED mp4 duration against the
            target (end-start) from chapters.json and report drift. The sync
            contract is: |rendered - target| must be < TOL seconds per chapter,
            because scenes are concatenated and the original audio is laid over
            the whole timeline. Drift accumulates, so tighten each chapter.

  assemble — concatenate the per-chapter mp4s in order, then mux the ORIGINAL
             podcast audio over the combined video -> one final companion mp4.
             (No TTS: the real recording is the soundtrack.)

Usage:
  python build/synced.py check    courses/<course>/chapters.json
  python build/synced.py assemble courses/<course>/chapters.json [out.mp4]

Renders are expected at animations/<slug>/renders/<SceneClass>.mp4 (Manim's
default output name). Override the render dir per chapter with "render" key.
"""
import json, subprocess, sys, os, pathlib, shutil

TOL = 0.5  # seconds of allowed per-chapter drift
FFMPEG = os.environ.get("FFMPEG") or shutil.which("ffmpeg") or "ffmpeg"
FFPROBE = os.environ.get("FFPROBE") or shutil.which("ffprobe") or "ffprobe"
ROOT = pathlib.Path(__file__).resolve().parents[1]


def probe_duration(path):
    out = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True)
    try:
        return float(out.stdout.strip())
    except ValueError:
        return None


def render_path(ch):
    """Resolve the rendered mp4 for a chapter. Manim writes under
    animations/<slug>/renders/videos/<scene>/<quality>/<SceneClass>.mp4 when
    invoked with --media_dir; some flows also copy a flat <SceneClass>.mp4 to
    the renders root. Prefer the flat copy, else the newest matching mp4."""
    if ch.get("render"):
        return ROOT / ch["render"]
    base = ROOT / "animations" / ch["slug"] / "renders"
    flat = base / f"{ch['scene_class']}.mp4"
    if flat.exists():
        return flat
    matches = sorted(base.rglob(f"{ch['scene_class']}.mp4"),
                     key=lambda p: p.stat().st_mtime, reverse=True)
    return matches[0] if matches else flat


def load(cfg_path):
    cfg = json.loads(pathlib.Path(cfg_path).read_text())
    return cfg


def cmd_check(cfg_path):
    cfg = load(cfg_path)
    print(f"{'CH':>3}  {'slug':32} {'target':>8} {'render':>8} {'drift':>8}  status")
    total_target = total_render = 0.0
    missing = 0
    worst = 0.0
    for ch in cfg["chapters"]:
        target = ch["end"] - ch["start"]
        total_target += target
        rp = render_path(ch)
        if not rp.exists():
            print(f"{ch['id']:>3}  {ch['slug']:32} {target:8.2f} {'--':>8} {'--':>8}  MISSING RENDER")
            missing += 1
            continue
        dur = probe_duration(rp)
        total_render += dur
        drift = dur - target
        worst = max(worst, abs(drift))
        status = "ok" if abs(drift) < TOL else "OUT OF SYNC (tune waits)"
        print(f"{ch['id']:>3}  {ch['slug']:32} {target:8.2f} {dur:8.2f} {drift:+8.2f}  {status}")
    print("-" * 78)
    print(f"     targets sum: {total_target:8.2f}   audio: {cfg['audio_duration_s']:8.2f}   "
          f"rendered sum: {total_render:8.2f}")
    print(f"     worst per-chapter drift: {worst:.2f}s (tolerance {TOL}s); missing renders: {missing}")
    return 1 if (missing or worst >= TOL) else 0


def cmd_assemble(cfg_path, out=None):
    cfg = load(cfg_path)
    course_dir = pathlib.Path(cfg_path).resolve().parent
    build_dir = course_dir / "renders"
    build_dir.mkdir(parents=True, exist_ok=True)
    out = pathlib.Path(out) if out else build_dir / f"{cfg['course']}-companion.mp4"

    # 1. concat list (must be in chapter order)
    missing = [ch["slug"] for ch in cfg["chapters"] if not render_path(ch).exists()]
    if missing:
        print("Cannot assemble — missing renders for:", ", ".join(missing))
        return 1
    listfile = build_dir / "concat.txt"
    listfile.write_text("".join(f"file '{render_path(ch)}'\n" for ch in cfg["chapters"]))

    silent = build_dir / "_combined_silent.mp4"
    print("Concatenating", len(cfg["chapters"]), "chapters ->", silent.name)
    subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(listfile),
                    "-c", "copy", str(silent)], check=True)

    # 2. mux original audio over the combined video
    audio = cfg["source_audio"]
    print("Muxing original audio ->", out.name)
    subprocess.run([FFMPEG, "-y", "-i", str(silent), "-i", audio,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-map", "0:v:0", "-map", "1:a:0", "-shortest", str(out)], check=True)

    vdur = probe_duration(silent)
    print(f"\nDone: {out}")
    print(f"  video timeline: {vdur:.1f}s   audio: {cfg['audio_duration_s']:.1f}s   "
          f"drift: {vdur - cfg['audio_duration_s']:+.1f}s")
    if abs(vdur - cfg["audio_duration_s"]) >= 1.0:
        print("  WARNING: >1s total drift — run 'check' and tune the offending chapters.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    action, cfg = sys.argv[1], sys.argv[2]
    if action == "check":
        sys.exit(cmd_check(cfg))
    elif action == "assemble":
        sys.exit(cmd_assemble(cfg, sys.argv[3] if len(sys.argv) > 3 else None))
    else:
        print("unknown action:", action)
        sys.exit(2)
