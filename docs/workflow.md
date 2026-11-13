# 작업 흐름

클린본 1개 + 레퍼런스 릴스 1개 → 레퍼런스 스타일로 편집된 완성본. 단계마다 결과를 눈으로 확인하고 넘어갑니다.

## 0. 프로젝트 폴더
```
my-reel/
├── references/<이름>/        # 레퍼런스 원본, 분석 메모, 프레임 그리드 (결과물에는 쓰지 않음)
├── source/                   # 내 클린본, 받아쓰기
└── video/                    # templates/<스타일>을 복사한 HyperFrames 프로젝트
```

## 1. 레퍼런스 분석 (hypit)
```bash
hypit media probe references/ref/source.mp4
hypit media tiles references/ref/source.mp4 --start 0 --end <길이> --every 1 --columns 6 --rows 3 --cell 300 --to references/ref/evidence/overview
hypit transcribe references/ref/source.mp4 --language ko --to references/ref/transcript.json
```
기록할 것 (`references/ref/ANALYSIS.md`):
- 훅(첫 3초)에 무엇이 화면에 있는가
- 자막: 위치, 크기, 박스 여부, 강조 방식, 한 번에 몇 어절
- 키워드 그래픽: 어떤 단어에서, 어떤 형태로(타이포/UI 카드/아이콘), 인물 앞/뒤
- 컷: 몇 초마다, 앵글이 실제로 바뀌는지(카메라 여러 대) 아니면 크롭인지
- 색감: 밝기, 대비, 색온도, 그림자 색
- 소리: 배경음악 유무, 효과음이 몇 번, 어디서 (`ffmpeg ... showspectrumpic`으로 확인)

레퍼런스 대사 구조와 내 대사 구조가 겹치는 지점(예: "A가 아니라 B다")을 찾으면 그래픽을 1:1로 대응시킬 수 있습니다.

## 2. 클린본 준비
```bash
python tools/prep_footage.py source/clean.mov video/assets/      # aroll.mp4(키프레임 1초) + person.webm(알파)
hypit transcribe source/clean.mov --language ko --to source/transcript.json
python tools/silence_check.py source/clean.mov                    # 잘라낼 무음이 있는지만 확인
```
- 받아쓰기는 **반드시 사람이 교정**합니다(예: "전환 노트" → "전환 루트").
- 무음이 거의 없으면 자르지 않습니다. 숨소리를 깎으면 기계처럼 들립니다.

## 3. 색감
```bash
.venv/Scripts/python tools/make_lut.py --preset vision3-2383 --out luts/
python tools/compare_luts.py --video video/assets/aroll.mp4 --at 9 --luts luts/*.cube --strength 0.65 --out luts/compare.png
```
고른 LUT를 `grades/film-lut-65.json`의 `lut.src`로 연결하고 A롤·인물 컷아웃 **두 영상에 같은 값**을 적용합니다.
```bash
npx hyperframes media-use resolve --type lut --from luts/vision3-2383.cube --intent "film emulation" --project video
npx hyperframes media-treatment --project video --file index.html --selector '#aroll'  --grading grades/film-lut-65.json --apply
npx hyperframes media-treatment --project video --file index.html --selector '#person' --grading grades/film-lut-65.json --apply
```

## 4. 구성 (HyperFrames)
- 템플릿을 복사해서 `compositions/*.html`의 시간과 문구를 내 대사 시간(받아쓰기)에 맞춥니다.
- 자막은 생성기로 만듭니다: `python tools/build_captions.py --transcript source/transcript.json --style warm --out video/compositions/captions.html`
- 폰트는 마지막에 주입합니다: `python tools/inject_fonts.py --project video --family pretendard`
- 검사와 스냅샷: `npx hyperframes check --json`, `npx hyperframes snapshot --at 0.5,3,7,13`

## 5. B롤 계획
`docs/broll-plan-template.md`를 채웁니다(B-Roll Finder 방법론). 숫자·사용법 장면은 **본인의 실제 화면**을 받습니다.

## 6. 렌더와 마무리
```bash
npx hyperframes render -q delivery -o renders/out.mp4
python tools/loudnorm.py renders/out.mp4 final.mp4      # -14 LUFS, 피크 -1 dB
```
완성본에서 프레임을 다시 뽑아 확인합니다(그레이딩·인물 정렬·자막 겹침).
