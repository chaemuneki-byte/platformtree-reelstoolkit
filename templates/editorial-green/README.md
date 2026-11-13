# editorial-green 템플릿

진녹색 #1f3d2b · 크림 #f1ebdd · 골드 #d9c27a 에디토리얼 매거진 스타일. 1080×1920, 30 fps, 예시 18.6초.

## 레이어 (index.html)
| z | 요소 | 내용 |
|---|---|---|
| 1 | `#cam-a > #aroll` | 촬영본 |
| 2 | `compositions/behind.html` | 녹색 배경판(아래에서 차오름) + **머리 뒤 대형 명조**("조회수 → 구조 → 매출로") |
| 3 | `#cam-b > #person` | 인물 컷아웃 |
| 4 | `hook.html` / `structure.html` / `payoff.html` | 산세리프 헤드라인, 박스 라벨, 손그림 취소선, 3단 구조 패널, 댓글 작성 UI |
| 5 | `captions.html` | 녹색 박스 명조 카라오케 자막 (`build_captions.py --style editorial`) |

## 맞추는 순서
1. 소스: `python tools/prep_footage.py clean.mov <proj>/assets/`
2. 음원: `assets/audio/bgm.mp3`, `hit.wav`(저음 히트), `ping.wav`(전송음). 3개 이하로.
3. 시간: `behind.html`의 `data-start`, `hook.html`·`structure.html`·`payoff.html`의 `T(…)` 안 초 값을 내 단어 시간으로
4. 머리 뒤 글자는 **30~55% 가려질 때** 가장 좋아 보입니다. 머리 윗선 = 576 − 221 × scale + y
5. 자막·폰트·그레이딩
   ```bash
   python tools/build_captions.py --transcript transcript.json --style editorial --out <proj>/compositions/captions.html
   python tools/inject_fonts.py --project <proj> --family noto-serif-kr,noto-sans-kr
   npx hyperframes media-treatment --project <proj> --file index.html --selector '#aroll'  --grading grades/editorial-green.json --apply
   npx hyperframes media-treatment --project <proj> --file index.html --selector '#person' --grading grades/editorial-green.json --apply
   ```

참고: 이 템플릿의 카메라는 짧은 펀치인이 많습니다. 끊겨 보이면 `docs/camera-rules.md` 기준(25% 이상 차이, 문장 경계)으로 줄이세요.
