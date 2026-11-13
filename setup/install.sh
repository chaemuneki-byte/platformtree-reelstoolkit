#!/usr/bin/env bash
# Platformtree Reels Toolkit installer (macOS / Linux)
# Usage:  bash setup/install.sh [--with-funclip]
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WITH_FUNCLIP=0; [ "${1:-}" = "--with-funclip" ] && WITH_FUNCLIP=1
echo "Toolkit: $ROOT"

need() { command -v "$1" >/dev/null 2>&1 || { echo "$1 not found. $2" >&2; exit 1; }; }
need node   "Install Node.js 22.15+"
need ffmpeg "Install ffmpeg"
need git    "Install git"
need python3 "Install Python 3.11+"
need uv     "Install uv: https://docs.astral.sh/uv/ (hypit WhisperX also needs it on PATH)"
node -e 'const [a,b]=process.versions.node.split(".").map(Number); if(a<22||(a===22&&b<15)){console.error("Node 22.15+ required");process.exit(1)}'

echo "1/5 hypit executable + skill"
npm install --global @hypit/hypit@0.3.2
npx -y skills add hypit-ai/hypit -g -a claude-code -s hypit -y --copy

echo "2/5 HyperFrames CLI (pinned, runs through npx)"
npx -y hyperframes@0.9.40 --version

echo "3/5 Python tools venv: auto-editor + Spectral Film LUT"
cd "$ROOT"
uv venv .venv --python python3
uv pip install --python .venv/bin/python auto-editor spectral-film-lut
echo "   fonts for the templates"
npm install --no-save pretendard@1.3.9 @fontsource-variable/noto-serif-kr@5.3.1 @fontsource-variable/noto-sans-kr@5.3.1

echo "4/5 Claude skills: reels-recut + B-Roll Finder"
SK="$HOME/.claude/skills"; mkdir -p "$SK/reels-recut"
cp "$ROOT/skills/reels-recut/SKILL.md" "$SK/reels-recut/"
printf '%s\n' "$ROOT" > "$SK/reels-recut/TOOLKIT_PATH"
[ -d "$SK/b-roll-finder" ] || git clone --depth 1 https://github.com/louisedesadeleer/b-roll-finder.git "$SK/b-roll-finder"

if [ "$WITH_FUNCLIP" = 1 ]; then
  echo "5/5 FunClip (local ASR only; large model download on first run)"
  FC="$ROOT/.funclip"
  [ -d "$FC" ] || git clone --depth 1 https://github.com/modelscope/FunClip.git "$FC"
  uv venv "$FC/.venv" --python python3
  uv pip install --python "$FC/.venv/bin/python" -r "$FC/requirements.txt"
  echo "   run: $FC/.venv/bin/python $FC/funclip/launch.py   (do not enter an LLM API key)"
else
  echo "5/5 FunClip skipped (use --with-funclip)"
fi
echo "Done. In Claude Code: /reels-recut"
