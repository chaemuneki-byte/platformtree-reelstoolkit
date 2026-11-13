"""Preview .cube LUTs side by side on one frame, blended at a given strength.

Usage:
  python tools/compare_luts.py --video aroll.mp4 --at 9 --luts luts/*.cube --strength 0.65 --out compare.png
The first panel is the untouched frame; the rest follow the order of --luts (printed to the console).
Needs ffmpeg on PATH.
"""
import argparse
import glob
import os
import subprocess
import sys
import tempfile


def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--video", required=True)
    ap.add_argument("--at", type=float, default=1.0, help="frame time in seconds")
    ap.add_argument("--luts", nargs="+", required=True)
    ap.add_argument("--strength", type=float, default=0.65, help="0..1 mix with the original (default 0.65)")
    ap.add_argument("--width", type=int, default=360, help="panel width")
    ap.add_argument("--out", default="lut-compare.png")
    a = ap.parse_args()

    luts = [p for pat in a.luts for p in (glob.glob(pat) or [pat])]
    tmp = tempfile.mkdtemp(prefix="lutcmp-")
    raw = os.path.join(tmp, "raw.png")
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(a.at), "-i", a.video, "-frames:v", "1", raw])
    panels = [raw]
    k = a.strength
    for i, lut in enumerate(luts):
        p = os.path.join(tmp, f"l{i}.png")
        lut_path = os.path.abspath(lut).replace("\\", "/").replace(":", "\\:")
        flt = f"[0]split[a][b];[b]lut3d=file='{lut_path}'[l];[a][l]blend=all_expr='A*(1-{k})+B*{k}'"
        run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-filter_complex", flt, p])
        panels.append(p)
    inputs = []
    for p in panels:
        inputs += ["-i", p]
    scale = "".join(f"[{i}]scale={a.width}:-1[s{i}];" for i in range(len(panels)))
    stack = "".join(f"[s{i}]" for i in range(len(panels))) + f"hstack={len(panels)}"
    run(["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", scale + stack, a.out])
    print("panels:", ["original"] + [os.path.basename(l) for l in luts])
    print(os.path.abspath(a.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
