# Platformtree Reels Toolkit installer (Windows PowerShell 5.1+)
# Usage:  ./setup/install.ps1            (core)
#         ./setup/install.ps1 -WithFunClip
param([switch]$WithFunClip)

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Write-Host "Toolkit: $Root"

function Need($cmd, $hint) {
  if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) { throw "$cmd not found. $hint" }
}
Need node   'Install Node.js 22.15+ (winget install OpenJS.NodeJS.22)'
Need ffmpeg 'Install ffmpeg (winget install Gyan.FFmpeg)'
Need git    'Install git (winget install Git.Git)'
Need python 'Install Python 3.11+'
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
  throw 'uv not found. winget install astral-sh.uv, then open a NEW terminal (hypit WhisperX also needs uv on PATH).'
}

$nodeVer = [version]((node --version).TrimStart('v'))
if ($nodeVer -lt [version]'22.15.0') { throw "Node $nodeVer is too old; hypit needs 22.15+" }

Write-Host '1/5 hypit executable + skill'
npm install --global @hypit/hypit@0.3.2
npx -y skills add hypit-ai/hypit -g -a claude-code -s hypit -y --copy

Write-Host '2/5 HyperFrames CLI (pinned, runs through npx)'
npx -y hyperframes@0.9.40 --version

Write-Host '3/5 Python tools venv: auto-editor + Spectral Film LUT'
Push-Location $Root
uv venv .venv --python python
uv pip install --python .venv/Scripts/python.exe auto-editor spectral-film-lut
Write-Host '   fonts for the templates'
npm install --no-save pretendard@1.3.9 @fontsource-variable/noto-serif-kr@5.3.1 @fontsource-variable/noto-sans-kr@5.3.1
Pop-Location

Write-Host '4/5 Claude skills: reels-recut + B-Roll Finder'
$Skills = Join-Path $HOME '.claude/skills'
New-Item -ItemType Directory -Force $Skills | Out-Null
$Dst = Join-Path $Skills 'reels-recut'
New-Item -ItemType Directory -Force $Dst | Out-Null
Copy-Item (Join-Path $Root 'skills/reels-recut/SKILL.md') $Dst -Force
Set-Content -Path (Join-Path $Dst 'TOOLKIT_PATH') -Value $Root -Encoding utf8
$Broll = Join-Path $Skills 'b-roll-finder'
if (-not (Test-Path $Broll)) { git clone --depth 1 https://github.com/louisedesadeleer/b-roll-finder.git $Broll }

if ($WithFunClip) {
  Write-Host '5/5 FunClip (local ASR only; large model download on first run)'
  $Fc = Join-Path $Root '.funclip'
  if (-not (Test-Path $Fc)) { git clone --depth 1 https://github.com/modelscope/FunClip.git $Fc }
  uv venv (Join-Path $Fc '.venv') --python python
  uv pip install --python (Join-Path $Fc '.venv/Scripts/python.exe') -r (Join-Path $Fc 'requirements.txt')
  Write-Host "   run: $Fc/.venv/Scripts/python.exe $Fc/funclip/launch.py   (do not enter an LLM API key)"
} else {
  Write-Host '5/5 FunClip skipped (use -WithFunClip)'
}

Write-Host 'Done. In Claude Code: /reels-recut'
