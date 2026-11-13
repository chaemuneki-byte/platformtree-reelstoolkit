"""Generate film-emulation .cube LUTs headlessly with Spectral Film LUT.

Spectral Film LUT (https://github.com/JanLohse/spectral_film_lut, MIT) ships as a GUI app.
This script calls its create_lut() directly with the GUI's defaults, for Rec.709 video.

Usage:
  python tools/make_lut.py --preset vision3-2383 --out luts/
  python tools/make_lut.py --negative "Kodak Portra 400" --print "Kodak Portra Endura Paper" --name my-look --out luts/
  python tools/make_lut.py --list
Run with the toolkit venv (setup/install.*), which has spectral-film-lut installed.
"""
import argparse
import os
import sys

PRESETS = {
    # name: (negative stock, print stock, note)
    "vision3-2383": ("Kodak Vision3 250D 5207", "Kodak Vision 2383", "cinema standard: filmic contrast, natural skin"),
    "portra400": ("Kodak Portra 400", "Kodak Portra Endura Paper", "bright and soft, low contrast"),
    "gold200": ("Kodak Gold 200", "Kodak Portra Endura Paper", "warm, nostalgic, bright"),
    "eterna500": ("Fuji Eterna 500", "Fuji Eterna-CP 3523XD", "muted cinema, cooler shadows"),
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--preset", choices=sorted(PRESETS), action="append", help="preset (repeatable)")
    ap.add_argument("--negative", help="negative stock name (see --list)")
    ap.add_argument("--print", dest="print_stock", help="print stock name (see --list)")
    ap.add_argument("--name", help="output file name without .cube (custom stocks)")
    ap.add_argument("--out", default="luts", help="output folder")
    ap.add_argument("--size", type=int, default=33, help="LUT size (default 33)")
    ap.add_argument("--input", default="ITU-R BT.709", help="input colourspace (colour-science name)")
    ap.add_argument("--list", action="store_true", help="list available film stocks")
    args = ap.parse_args()

    try:
        from spectral_film_lut.film_loader import load_filmstocks
        from spectral_film_lut.utils import create_lut
    except ImportError:
        print("spectral-film-lut is not installed in this Python. Run setup/install.* and use .venv's python.", file=sys.stderr)
        return 2

    stocks = load_filmstocks(lambda *a, **k: None)
    if args.list:
        for n in sorted(stocks):
            print(n)
        return 0

    jobs = []
    for p in args.preset or []:
        neg, prt, _ = PRESETS[p]
        jobs.append((neg, prt, p))
    if args.negative:
        jobs.append((args.negative, args.print_stock, args.name or args.negative.lower().replace(" ", "-")))
    if not jobs:
        ap.error("give --preset or --negative (or --list)")

    os.makedirs(args.out, exist_ok=True)
    out_dir = os.path.abspath(args.out)
    ref = stocks["Kodak Vision3 250D 5207"]
    cwd = os.getcwd()
    os.chdir(out_dir)  # create_lut writes <name>.cube into the working directory
    try:
        for neg, prt, name in jobs:
            for s in (neg, prt):
                if s and s not in stocks:
                    print(f"unknown stock: {s} (see --list)", file=sys.stderr)
                    return 2
            path = create_lut(
                stocks[neg], stocks[prt] if prt else None, name=name, lut_size=args.size, cube=True,
                input_colorspace=args.input, output_gamut="Rec. 709", gamma_func="Gamma 2.4",
                mode="full", white_clip=True, white_balance=1, adx_scaling=4.0,
                apd_intermediate=True, custom_inversion=True, reference_negative=ref,
            )
            print(os.path.join(out_dir, path))
    finally:
        os.chdir(cwd)
    return 0


if __name__ == "__main__":
    sys.exit(main())
