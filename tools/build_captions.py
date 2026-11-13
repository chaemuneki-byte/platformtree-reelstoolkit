"""Build the caption scene (compositions/captions.html) from a word-timed transcript.

Accepts a hypit transcript ({"passages":[{"words":[{"text","start_seconds","end_seconds"}]}]})
or a plain list [{"text","start","end"}] (HyperFrames transcribe).

Styles:
  editorial  green-box serif, karaoke (spoken words turn cream)       -> templates/editorial-green
  warm       plain white Pretendard, emphasised lines larger + hand-drawn underline -> templates/warm-creator

Usage:
  python tools/build_captions.py --transcript transcript.json --style warm --out video/compositions/captions.html \
      --fix 노트=루트 --emph "매출이 안" --emph "바뀝니다" --hide 5.40-7.03
  python tools/build_captions.py --transcript t.json --style editorial --groups groups.json --out ...
groups.json: [[first_word_index, end_word_index_exclusive, emphasised(0|1)], ...]
After writing, run tools/inject_fonts.py for the project so the font faces are embedded.
"""
import argparse
import html
import json
import re
import sys


def load_words(path, fixes):
    d = json.load(open(path, encoding="utf-8"))
    raw = []
    if isinstance(d, dict) and "passages" in d:
        for p in d["passages"]:
            for w in p["words"]:
                raw.append((w["text"], w.get("start_seconds"), w.get("end_seconds")))
    elif isinstance(d, list):
        for w in d:
            raw.append((w["text"], w.get("start"), w.get("end")))
    else:
        raise SystemExit("unknown transcript format")
    words = []
    for i, (t, s, e) in enumerate(raw):
        for old, new in fixes:
            t = t.replace(old, new)
        if s is None:
            s = (words[-1][2] + 0.08) if words else 0.1
        if e is None:
            e = s + 0.45
        words.append((t, float(s), float(e)))
    return words


def auto_groups(words, max_words):
    groups, cur = [], []
    for i, (t, s, e) in enumerate(words):
        if cur and (len(cur) >= max_words or s - words[cur[-1]][2] >= 0.15):
            groups.append(cur); cur = []
        cur.append(i)
        if re.search(r"[.,?!…]$", t):
            groups.append(cur); cur = []
    if cur:
        groups.append(cur)
    return [[g[0], g[-1] + 1, 0] for g in groups]


def in_ranges(t, ranges):
    return any(a <= t < b for a, b in ranges)


STYLE_CSS = {
    "editorial": """
    #root { position: absolute; inset: 0; }
    .cg { position: absolute; left: 0; top: 1232px; width: 1080px; text-align: center; overflow: visible; }
    .cbox {
      display: inline-block; max-width: 900px; background: #1f3d2b; border: 1px solid rgba(241,235,221,.14);
      padding: 9px 20px 12px; border-radius: 3px;
      font: 500 50px/1.25 "NotoSerifKR", serif; letter-spacing: -0.03em; color: #8ea595;
      box-shadow: 0 10px 28px rgba(0,0,0,.25);
    }""",
    "warm": """
    #root { position: absolute; inset: 0; }
    .cap { position: absolute; left: 0; top: 1068px; width: 1080px; text-align: center; overflow: visible; }
    .cap span {
      position: relative; display: inline-block; color: #fff; white-space: nowrap;
      font: 600 58px/1.2 "Pretendard", sans-serif; letter-spacing: -0.04em;
      text-shadow: 0 2px 4px rgba(30, 16, 10, 0.55), 0 4px 18px rgba(30, 16, 10, 0.45);
    }
    .cap.emph { top: 1040px; }
    .cap.emph span { font-weight: 800; font-size: 84px; letter-spacing: -0.05em; }
    .ul { position: absolute; left: -6px; bottom: -14px; width: calc(100% + 12px); height: 24px; overflow: visible; }
    .ul path { fill: none; stroke: #ffd23f; stroke-width: 7; stroke-linecap: round; vector-effect: non-scaling-stroke; }""",
}


def build(words, groups, style, hide, end_cap):
    rows, js = [], []
    gi = 0
    for a, b, emph in groups:
        g = words[a:b]
        start = max(0.1, g[0][1] - 0.04)
        if in_ranges(start + 0.05, hide):
            continue
        end = g[-1][2] + (0.12 if style == "editorial" else 0.15)
        later = [x for x in groups if x[0] >= b]
        if later:
            end = min(end, words[later[0][0]][1] - 0.04)
        for ha, hb in hide:
            if start < ha < end:
                end = ha
        end = min(end, end_cap)
        if end - start < 0.12:
            continue
        text_items = [html.escape(t) for t, _, _ in g]
        if style == "editorial":
            spans = " ".join(f'<span class="cw" id="cw{a + k}">{t}</span>' for k, t in enumerate(text_items))
            rows.append(f'    <div id="cg{gi}" class="cg clip" data-start="{start:.3f}" data-duration="{end - start:.3f}" '
                        f'data-track-index="{gi % 2}"><div class="cbox">{spans}</div></div>')
            js.append(f'    grp("#cg{gi}", {start:.3f}, {end:.3f});')
            for k, (_, s, _) in enumerate(g):
                js.append(f'    tl.to("#cw{a + k}", {{ color: "#f1ebdd", duration: 0.08, ease: "none" }}, {s:.3f});')
        else:
            text = " ".join(text_items)
            if emph:
                rows.append(f'    <div id="cp{gi}" class="cap emph clip" data-start="{start:.3f}" data-duration="{end - start:.3f}" '
                            f'data-track-index="{gi % 2}" data-layout-allow-overlap><span>{text}<svg class="ul" '
                            f'preserveAspectRatio="none" viewBox="0 0 400 24"><path id="ul{gi}" d=""/></svg></span></div>')
                js.append(f'    pop("#cp{gi} span", {start:.3f}, 1); line("ul{gi}", {gi}, {start + 0.2:.3f});')
            else:
                rows.append(f'    <div id="cp{gi}" class="cap clip" data-start="{start:.3f}" data-duration="{end - start:.3f}" '
                            f'data-track-index="{gi % 2}"><span>{text}</span></div>')
                js.append(f'    pop("#cp{gi} span", {start:.3f}, 0);')
        gi += 1

    if style == "editorial":
        helpers = """    const grp = (sel, start, end) => {
      const box = `${sel} .cbox`;
      tl.fromTo(box, { opacity: 0 }, { opacity: 1, duration: 0.1, ease: "power2.out" }, start);
      tl.to(box, { opacity: 0, duration: 0.08, ease: "power2.in" }, end - 0.08);
    };"""
    else:
        helpers = """    const hash = (n, seed) => { const x = Math.sin(n * 127.1 + seed * 311.7) * 43758.5453; return (x - Math.floor(x)) * 2 - 1; };
    // plain captions cut in; emphasised lines land with a small settle and a hand-drawn underline
    const pop = (sel, t, emph) => emph
      ? tl.fromTo(sel, { opacity: 0, scale: 0.88 }, { opacity: 1, scale: 1, duration: 0.18, ease: "back.out(1.8)" }, t)
      : tl.fromTo(sel, { opacity: 0 }, { opacity: 1, duration: 0.05, ease: "none" }, t);
    const line = (id, seed, t) => {
      let d = "M 2 " + (12 + hash(0, seed) * 3).toFixed(1);
      for (let i = 1; i <= 5; i++) d += " Q " + (i * 80 - 40 + hash(i, seed) * 10).toFixed(1) + " " + (12 + (i % 2 ? -6 : 6) + hash(i + 9, seed) * 2).toFixed(1) + " " + (i * 80) + " " + (12 + hash(i + 20, seed) * 3).toFixed(1);
      const p = document.getElementById(id); p.setAttribute("d", d);
      tl.fromTo(p, { strokeDasharray: 520, strokeDashoffset: 520 }, { strokeDashoffset: 0, duration: 0.32, ease: "power2.inOut", immediateRender: true }, t);
    };"""

    rows_s = "\n".join(rows)
    js_s = "\n".join(js)
    return f"""<template>
  <style>
    /*FONTS*/{STYLE_CSS[style]}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
{rows_s}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{helpers}
{js_s}
    window.__timelines["captions"] = tl;
  </script>
</template>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--transcript", required=True)
    ap.add_argument("--style", choices=["editorial", "warm"], required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--groups", help="groups.json (explicit grouping); default: automatic")
    ap.add_argument("--max-words", type=int, help="words per group for automatic grouping")
    ap.add_argument("--fix", action="append", default=[], help="correct a mis-heard word: OLD=NEW (repeatable)")
    ap.add_argument("--emph", action="append", default=[], help="emphasise groups containing this text (warm style)")
    ap.add_argument("--hide", action="append", default=[], help="hide captions in START-END seconds (repeatable)")
    ap.add_argument("--end", type=float, default=None, help="clamp the last caption to the video length")
    a = ap.parse_args()

    fixes = [tuple(f.split("=", 1)) for f in a.fix]
    words = load_words(a.transcript, fixes)
    if a.groups:
        groups = json.load(open(a.groups, encoding="utf-8"))
    else:
        groups = auto_groups(words, a.max_words or (4 if a.style == "editorial" else 3))
    for g in groups:
        text = " ".join(t for t, _, _ in words[g[0]:g[1]])
        if any(e in text for e in a.emph):
            g[2] = 1
    hide = [tuple(float(x) for x in h.split("-")) for h in a.hide]
    end_cap = a.end if a.end else words[-1][2] + 0.2
    out = build(words, groups, a.style, hide, end_cap)
    open(a.out, "w", encoding="utf-8").write(out)
    for g in groups:
        print(("* " if g[2] else "  ") + " ".join(t for t, _, _ in words[g[0]:g[1]]))
    print("->", a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
