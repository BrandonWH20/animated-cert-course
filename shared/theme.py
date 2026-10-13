"""Canonical palette + helpers for the explainer series. Import from any scene:
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
    from shared.theme import PALETTE, beat_title
Keeps every animation visually consistent (matches the Study Aids explainers)."""
from manim import Text, FadeIn, FadeOut, UP

# theme-neutral, high-contrast on Manim's dark bg (mirrors the Study Aids palette)
PALETTE = {
    "blue":   "#3987e5",
    "teal":   "#1baf7a",
    "green":  "#22c55e",
    "amber":  "#eda100",
    "red":    "#e34948",
    "purple": "#9085e9",
    "ink":    "#f5f5f7",
    "muted":  "#98989d",
}

def beat_title(scene, text, color="#f5f5f7", run_time=0.5):
    """Standard top-of-frame beat title. Returns the mobject so the caller can fade it out."""
    t = Text(text, font="sans-serif", font_size=34, color=color).to_edge(UP)
    scene.play(FadeIn(t), run_time=run_time)
    return t
