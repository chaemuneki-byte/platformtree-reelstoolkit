"""Two-pass loudness normalisation for a finished reel (video stream copied untouched).

Usage:
  python tools/loudnorm.py render.mp4 final.mp4            # -14 LUFS, true peak -1 dB
  python tools/loudnorm.py render.mp4 final.mp4 --lufs -16
"""
import argparse
import json
import re
import subprocess
import sys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--lufs", type=float, default=-14.0)
    ap.add_argument("--tp", type=float, default=-1.0)
    ap.add_argument("--lra", type=float, default=7.0)
    a = ap.parse_args()

    target = f"I={a.lufs}:TP={a.tp}:LRA={a.lra}"
    p = subprocess.run(["ffmpeg", "-hide_banner", "-i", a.src, "-af", f"loudnorm={target}:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", p.stderr, re.S)
    if not m:
        print(p.stderr[-2000:], file=sys.stderr)
        return 1
    j = json.loads(m.group(0))
    flt = (f"loudnorm={target}:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}"
           f":measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true,aresample=48000")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.src, "-c:v", "copy", "-af", flt, "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", a.dst], check=True)
    print(f"input {j['input_i']} LUFS / {j['input_tp']} dBTP -> {a.dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
