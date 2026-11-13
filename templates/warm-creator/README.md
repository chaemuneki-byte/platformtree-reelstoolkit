# warm-creator 템플릿

따뜻한 크리에이터 토크 스타일. 1080×1920, 30 fps, 예시 길이 18.6초(블로그 수익화 예제 대본).

## 레이어 (index.html)
| z | 요소 | 내용 |
|---|---|---|
| 1 | `#cam-a > #aroll` | 촬영본(소리 포함) |
| 2 | `compositions/behind.html` | 상단 제목, 통계 카드, 구조 다이어그램, 댓글 UI — **인물 뒤** |
| 3 | `#cam-b > #person` | 인물 컷아웃(알파). A롤과 같은 카메라 값으로 움직임 |
| 4 | `compositions/front.html` | 명언 타이포("A가 아니라 / B에서") + 손그림 취소선·동그라미 |
| 5 | `compositions/captions.html` | 자막 (`tools/build_captions.py --style warm`으로 생성) |

## 내 영상에 맞추는 순서
1. `assets/aroll.mp4`, `assets/person.webm`을 넣는다 → `python tools/prep_footage.py clean.mov templates/.../assets/`
2. 음원: `assets/audio/bgm.mp3`, `assets/audio/pop.wav` (HyperFrames `media-use`로 CC0 음원). 없으면 index.html의 `<audio>`를 지운다
3. **시간 맞추기**: 각 파일의 숫자(초)는 예제 대본의 단어 시간입니다. 내 받아쓰기에서 같은 역할을 하는 단어의 시간으로 바꿉니다.
   - `index.html` 카메라: `cut(…)`, `push(…)` — 규칙은 `docs/camera-rules.md`
   - `behind.html`: 제목(0–2.1s), 통계 카드(`#graph`), 다이어그램(`#diagram`, 노드별 등장 시간), CTA(`#cta`)
   - `front.html`: 로컬 시간 0 = 호스트 `data-start`(index.html의 `#front`)
4. **문구 바꾸기**: 제목, 카드 라벨, 노드 이름, 댓글 문구는 HTML 텍스트를 직접 수정
5. 자막 생성 → 폰트 주입 → 그레이딩 → 검사
   ```bash
   python tools/build_captions.py --transcript transcript.json --style warm --out <proj>/compositions/captions.html --emph "강조할 문장" --hide 5.4-7.03
   python tools/inject_fonts.py --project <proj> --family pretendard
   npx hyperframes media-treatment --project <proj> --file index.html --selector '#aroll'  --grading grades/film-lut-65.json --apply
   npx hyperframes media-treatment --project <proj> --file index.html --selector '#person' --grading grades/film-lut-65.json --apply
   npx hyperframes check --json && npx hyperframes snapshot --at 0.5,3,7,13
   ```

## 기억할 값
- 상단 그래픽 구간 프레이밍: scale 1.15, y +86 (머리 윗선 ≈ 408px) → 그래픽은 y 168–406 안에
- 강조 타이트: scale 1.45 (상단 그래픽 없이)
- 노란 강조 #ffd23f, 빨간 알약 #c93a26, 다크 카드 rgba(12,11,11,.9)
- 효과음: 카드 등장 팝 3번(0.28 볼륨), 배경음악 0.15
