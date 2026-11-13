"""Ask auto-editor how much it would cut, without rendering anything.

Usage:
  python tools/silence_check.py source/clean.mov
  python tools/silence_check.py source/clean.mov --thresholds 0.04 0.08 0.12 --margin 0.12
Prints the kept length and cut count per threshold. A tight, hand-edited take usually shows ~0 cuts:
then leave it alone, since cutting breaths makes speech sound robotic.
To actually cut a long raw take:  auto-editor raw.mov --margin 0.15s --export premiere   (or -o out.mp4)
"""
import argparse
import os
import re
import shutil
import subprocess
import sys


def find_auto_editor():
    here = os.path.dirname(os.path.abspath(__file__))
    for cand in (os.path.join(here, "..", ".venv", "Scripts", "auto-editor.exe"),
                 os.path.join(here, "..", ".venv", "bin", "auto-editor")):
        if os.path.exists(cand):
            return os.path.abspath(cand)
    return shutil.which("auto-editor")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("media")
    ap.add_argument("--thresholds", nargs="+", type=float, default=[0.04, 0.08, 0.12])
    ap.add_argument("--margin", type=float, default=0.12)
    a = ap.parse_args()
    exe = find_auto_editor()
    if not exe:
        print("auto-editor not found. Run setup/install.*", file=sys.stderr)
        return 2
    for th in a.thresholds:
        out = subprocess.run([exe, a.media, "--edit", f"audio:threshold={th}", "--margin", f"{a.margin}s", "--preview"],
                             capture_output=True, text=True)
        text = out.stdout + out.stderr
        kept = re.search(r"output:\s+(\S+)\s+\(\d+\)\s+([\d.]+)%", text)
        cuts = re.search(r"cuts:\s*\n\s*- amount:\s+(\d+)", text)
        print(f"threshold {th:<5} kept {kept.group(1) if kept else '?'} ({kept.group(2) if kept else '?'}%)  cuts {cuts.group(1) if cuts else '?'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
