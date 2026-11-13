"""Embed Korean fonts in a HyperFrames project, shipping only the subset files its text uses.

HyperFrames only bundles Latin fonts; Korean needs @font-face per scene file. This script reads
every compositions/*.html, finds which unicode-range subsets of the chosen families cover the
characters in use, copies those .woff2 files into <project>/assets/fonts/, and writes the
@font-face block at the /*FONTS*/ marker (or replaces a previous /*FONTS:BEGIN*/../*FONTS:END*/ block).

Families (font-family name to use in CSS):
  pretendard     -> "Pretendard"   (npm: pretendard)
  noto-serif-kr  -> "NotoSerifKR"  (npm: @fontsource-variable/noto-serif-kr)
  noto-sans-kr   -> "NotoSansKR"   (npm: @fontsource-variable/noto-sans-kr)

Usage:
  python tools/inject_fonts.py --project video --family pretendard
  python tools/inject_fonts.py --project video --family noto-serif-kr,noto-sans-kr
The npm packages are looked up in node_modules next to the project, its parents, or this toolkit.
"""
import argparse
import glob
import os
import re
import shutil
import sys

FAMILIES = {
    "pretendard": ("Pretendard", "pretendard/dist/web/variable/pretendardvariable-dynamic-subset.css", "45 920"),
    "noto-serif-kr": ("NotoSerifKR", "@fontsource-variable/noto-serif-kr/index.css", "100 900"),
    "noto-sans-kr": ("NotoSansKR", "@fontsource-variable/noto-sans-kr/index.css", "100 900"),
}
BLOCK = re.compile(r"/\*FONTS:BEGIN\*/.*?/\*FONTS:END\*/", re.S)


def find_css(rel, start_dirs):
    for d in start_dirs:
        d = os.path.abspath(d)
        while True:
            p = os.path.join(d, "node_modules", rel)
            if os.path.exists(p):
                return p
            parent = os.path.dirname(d)
            if parent == d:
                break
            d = parent
    return None


def ranges(ur):
    out = []
    for part in ur.split(","):
        part = part.strip().upper().replace("U+", "")
        if "?" in part:
            out.append((int(part.replace("?", "0"), 16), int(part.replace("?", "F"), 16)))
        elif "-" in part:
            x, y = part.split("-"); out.append((int(x, 16), int(y, 16)))
        else:
            out.append((int(part, 16), int(part, 16)))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", required=True)
    ap.add_argument("--family", required=True, help="comma separated: " + ", ".join(FAMILIES))
    a = ap.parse_args()

    scenes = glob.glob(os.path.join(a.project, "compositions", "*.html"))
    if not scenes:
        print("no compositions/*.html in", a.project, file=sys.stderr)
        return 2
    texts = {f: open(f, encoding="utf-8").read() for f in scenes}
    chars = set("".join(BLOCK.sub("", t) for t in texts.values()))
    toolkit = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

    faces = []
    for fam in a.family.split(","):
        fam = fam.strip()
        name, rel, weights = FAMILIES[fam]
        css_path = find_css(rel, [a.project, toolkit])
        if not css_path:
            print(f"npm package for {fam} not found (npm install it next to the project or the toolkit)", file=sys.stderr)
            return 2
        css = open(css_path, encoding="utf-8").read()
        base = os.path.dirname(css_path)
        dest = os.path.join(a.project, "assets", "fonts", fam)
        os.makedirs(dest, exist_ok=True)
        n = 0
        for b in re.findall(r"@font-face\s*\{(.*?)\}", css, re.S):
            src = re.search(r"url\(['\"]?\./([^)'\"]+\.woff2)['\"]?\)", b)
            ur = re.search(r"unicode-range:\s*([^;]+);", b)
            if not src or not ur:
                continue
            rng = ranges(ur.group(1))
            if not any(any(x <= ord(c) <= y for x, y in rng) for c in chars):
                continue
            fname = os.path.basename(src.group(1))
            shutil.copy(os.path.join(base, src.group(1)), os.path.join(dest, fname))
            faces.append(f"@font-face {{ font-family: '{name}'; font-style: normal; font-display: block; "
                         f"font-weight: {weights}; src: url('assets/fonts/{fam}/{fname}') format('woff2-variations'); "
                         f"unicode-range: {ur.group(1).strip()}; }}")
            n += 1
        print(f"{fam}: {n} subset files -> {dest}")

    block = "/*FONTS:BEGIN*/\n    " + "\n    ".join(faces) + "\n    /*FONTS:END*/"
    for f, t in texts.items():
        if BLOCK.search(t):
            t = BLOCK.sub(lambda m: block, t)
        elif "/*FONTS*/" in t:
            t = t.replace("/*FONTS*/", block)
        else:
            continue
        open(f, "w", encoding="utf-8").write(t)
    return 0


if __name__ == "__main__":
    sys.exit(main())
