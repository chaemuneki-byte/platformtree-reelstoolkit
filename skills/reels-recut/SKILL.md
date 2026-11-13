---
name: reels-recut
description: Re-edit a user's own clean talking-head take in the style of a benchmark reel, keeping the user's picture and voice untouched. Analyses the reference with hypit, cuts out the speaker, grades with a film LUT at 60-70%, builds captions and content-matched motion graphics from a HyperFrames template (editorial-green or warm-creator), plans real-screen B-roll, renders and normalises to -14 LUFS. Use when the user says "/reels-recut", "이 영상 스타일로 내 클린본 편집", "벤치마킹해서 내 영상에 적용", or gives a reference reel plus their own footage.
---

# Reels recut (Platformtree Reels Toolkit)

The toolkit folder is written in `TOOLKIT_PATH` next to this file by `setup/install.*`. Read it first and use
its `tools/`, `templates/`, `grades/` and `docs/`. Speak Korean with the user. Show evidence (frame grids,
LUT comparisons, snapshots) at every step and say what it means.

## Hard rules
- Never generate or alter the user's picture or voice. The reference is evidence only: never use its frames or audio.
- No paid services or API keys. Local WhisperX (CPU), local remove-background, Openverse CC0/CC BY audio.
- Camera: hard cuts only at sentence boundaries and only with >= 25% scale change; otherwise smooth pushes (0.5-0.8 s, power2.inOut). Keep the eye line fixed across graphics sections. A-roll and cutout share one camera wrapper. (`docs/camera-rules.md`)
- LUT strength 0.6-0.7. Apply the same grading JSON to `#aroll` and `#person`.
- SFX: at most 3 (graphic arrivals). BGM ~0.1-0.15 under the voice. Final -14 LUFS, true peak -1 dB.
- Numbers, stats and how-to beats want the user's real screens. Never present invented figures as real; if a graphic visualises the line instead of real data, say so to the user.
- Fix transcript mistakes with the user before captions (show the transcript and ask about doubtful words).

## Steps
1. **Project**: create `<work>/references/<name>/`, `<work>/source/`, copy `templates/<style>` to `<work>/video/`. Make `<work>/package.json` with `"hypit": {"project": true}` and the runtime from `hypit/README.md` if not set up.
2. **Analyse the reference** (`docs/workflow.md` §1): probe, 1 s overview tiles, dense tiles on the hook and on each graphic moment, transcript, audio spectrum. Write ANALYSIS.md: hook, captions, keyword graphics (front/behind head), cut rhythm, colour, sound. Find where the reference's sentence structure matches the user's script and map graphics 1:1.
3. **Pick the style**: editorial-green (moody green magazine) or warm-creator (bright warm talk). Ask only if the reference does not make it obvious.
4. **Prepare footage**: `python tools/prep_footage.py <clean> <work>/video/assets/` → check `matte-check.png`. Transcribe the clean take with hypit; `python tools/silence_check.py <clean>` and cut only if it reports real dead air.
5. **Colour**: `<toolkit>/.venv` python `tools/make_lut.py --preset vision3-2383 --preset portra400 --preset gold200 --out <work>/luts`, then `tools/compare_luts.py ... --strength 0.65`, show the user, register the chosen LUT with `npx hyperframes media-use resolve --type lut --from ...`, set `lut.src` in a copy of `grades/film-lut-65.json`, apply to both videos with `npx hyperframes media-treatment`.
6. **Compose**: retime the template scenes to the user's word times; rewrite copy for their content; keep graphics inside the band above the head (y 168-406 at framing scale 1.15/y 86) or over the chest below the chin. Captions with `tools/build_captions.py` (fixes via `--fix`, emphasis via `--emph`, hide during quote typography via `--hide`). Fonts with `tools/inject_fonts.py`. Search the HyperFrames registry (`npx hyperframes catalog --json`) before hand-building a named effect.
7. **Check**: `npx hyperframes check --json` (fix errors), `npx hyperframes snapshot --at ...` around every cut, push and graphic arrival; look at the frames, fix overlaps (graphics over the face, captions colliding with titles).
8. **B-roll plan**: fill `docs/broll-plan-template.md` with the B-Roll Finder method (`/find-broll` skill if installed). Ask the user for their real screen recordings; do not ship invented stand-ins as if real.
9. **Render**: `npx hyperframes render -q delivery -o renders/out.mp4`, then `python tools/loudnorm.py renders/out.mp4 <final>.mp4`. Extract frames from the final file and check them before handing it over. Tell the user what you could not verify (you cannot listen to audio).
