# 그레이딩 프리셋

| 파일 | 느낌 | 쓰는 템플릿 |
|---|---|---|
| `editorial-green.json` | 따뜻한 하이라이트 + 녹색·올리브 그림자, 채도 낮춤, 들린 블랙, 비네트 | editorial-green |
| `warm-creator.json` | 밝고 따뜻한 거실 톤, 부드러운 대비 (LUT 없이) | warm-creator |
| `film-lut-65.json` | 따뜻함은 절반, Spectral Film LUT(Vision3 → 2383)를 **65%** | warm-creator (권장) |

`film-lut-65.json`의 `lut.src`는 LUT를 프로젝트에 등록한 경로입니다:
```bash
npx hyperframes media-use resolve --type lut --from luts/vision3-2383.cube --intent "film emulation" --project video
# → .media/luts/lut_001.cube  (번호가 다르면 JSON의 src를 맞춰 주세요)
```
적용은 A롤과 인물 컷아웃 **둘 다** 같은 파일로:
```bash
npx hyperframes media-treatment --project video --file index.html --selector '#aroll'  --grading grades/film-lut-65.json --apply
npx hyperframes media-treatment --project video --file index.html --selector '#person' --grading grades/film-lut-65.json --apply
```
LUT 강도는 0.6~0.7 사이에서 조절하세요. 1.0이면 피부톤이 무너집니다.
