#!/usr/bin/env bash
# Concatenate a course's rendered mp4s into one module video + a combined narration script.
# Usage: build/assemble.sh courses/01-networking-fundamentals.yaml
set -euo pipefail
COURSE="${1:?usage: assemble.sh courses/<name>.yaml}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NAME="$(basename "$COURSE" .yaml)"
OUT="$ROOT/build/$NAME"
mkdir -p "$OUT"
# pull animation IDs (lines like "  - 01-slug", skipping commented ones)
IDS=$(grep -E '^\s*-\s' "$ROOT/$COURSE" | grep -v '#' | sed -E 's/^\s*-\s*//')
LIST="$OUT/concat.txt"; : > "$LIST"; SCRIPT="$OUT/combined-script.md"; : > "$SCRIPT"
for id in $IDS; do
  mp4=$(ls "$ROOT/animations/$id/renders/"*.mp4 2>/dev/null | head -1 || true)
  [ -n "$mp4" ] && echo "file '$mp4'" >> "$LIST" || echo "WARN: no render for $id" >&2
  echo -e "\n\n---\n" >> "$SCRIPT"; cat "$ROOT/animations/$id/script.md" >> "$SCRIPT" 2>/dev/null || true
done
ffmpeg -y -f concat -safe 0 -i "$LIST" -c copy "$OUT/$NAME.mp4"
echo "assembled -> $OUT/$NAME.mp4  +  combined-script.md"
