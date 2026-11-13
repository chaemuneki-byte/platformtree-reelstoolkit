"""Prepare a clean take for the HyperFrames templates.

Writes into <out_dir>:
  aroll.mp4    H.264, 30 fps, keyframe every second (seek-safe), original audio
  person.webm  the speaker cut out with alpha (VP9 yuva420p), same timing
  matte-check.png  four frames of the cutout over a flat colour, to eyeball edges

Usage:
  python tools/prep_footage.py source/clean.mov video/assets/
  python tools/prep_footage.py source/clean.mov video/assets/ --skip-cutout
Needs ffmpeg and Node (for `npx hyperframes remove-background`, which downloads a ~168 MB model once).
"""
import argparse
import os
import shutil
import subprocess
import sys

HF = "hyperframes@0.9.40"


def sh(cmd, **kw):
    print("$", " ".join(cmd))
    subprocess.run(cmd, check=True, **kw)


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True, check=True).stdout.strip()
    return float(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source")
    ap.add_argument("out_dir")
    ap.add_argument("--skip-cutout", action="store_true")
    ap.add_argument("--bg", default="0x1F3D2B", help="matte-check background colour")
    a = ap.parse_args()

    os.makedirs(a.out_dir, exist_ok=True)
    aroll = os.path.join(a.out_dir, "aroll.mp4")
    sh(["ffmpeg", "-v", "error", "-y", "-i", a.source, "-c:v", "libx264", "-crf", "14", "-preset", "slow",
        "-pix_fmt", "yuv420p", "-g", "30", "-keyint_min", "30", "-r", "30",
        "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", aroll])
    if a.skip_cutout:
        return 0

    npx = shutil.which("npx") or shutil.which("npx.cmd")
    if not npx:
        print("npx not found (install Node.js 22.15+)", file=sys.stderr)
        return 2
    tmp_mov = os.path.join(a.out_dir, "_cutout.mov")
    sh([npx, "-y", HF, "remove-background", a.source, "-o", tmp_mov])
    person = os.path.join(a.out_dir, "person.webm")
    sh(["ffmpeg", "-v", "error", "-y", "-i", tmp_mov, "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0",
        "-crf", "22", "-g", "30", "-r", "30", "-row-mt", "1", "-an", person])

    # matte check: decode RGBA frames first (alpha can vanish inside some filter chains), then composite
    d = duration(tmp_mov)
    frames = []
    for i, t in enumerate([d * f for f in (0.1, 0.35, 0.6, 0.9)]):
        fg = os.path.join(a.out_dir, f"_fg{i}.png")
        comp = os.path.join(a.out_dir, f"_c{i}.png")
        sh(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", tmp_mov, "-frames:v", "1", "-pix_fmt", "rgba", fg])
        sh(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c={a.bg}:s=1080x1920", "-i", fg,
            "-filter_complex", "[0][1]overlay=0:0:shortest=1,scale=270:-1", "-frames:v", "1", comp])
        frames += ["-i", comp]
    sh(["ffmpeg", "-v", "error", "-y", *frames, "-filter_complex", "hstack=4", os.path.join(a.out_dir, "matte-check.png")])
    for f in os.listdir(a.out_dir):
        if f.startswith("_"):
            os.remove(os.path.join(a.out_dir, f))
    print("look at", os.path.join(a.out_dir, "matte-check.png"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
