# Platformtree Reels Toolkit

벤치마킹하고 싶은 릴스의 **편집 스타일만** 가져와서, 직접 찍은 클린본(토킹헤드)에 입히는 도구 모음입니다.
화면과 목소리는 생성하지 않고 촬영본을 그대로 씁니다. Claude Code에서 쓰도록 만들었습니다.

```
레퍼런스 릴스 ─┐
               ├─ ① 분석 (hypit: 받아쓰기, 프레임 그리드)
내 클린본 ─────┤
               ├─ ② 준비 (인물 분리, 키프레임 정리, 받아쓰기)
               ├─ ③ 색감 (필름 LUT 65% + 그레이딩)
               ├─ ④ 구성 (HyperFrames 템플릿: 자막·모션그래픽·카메라)
               ├─ ⑤ B롤 계획 (B-Roll Finder 방법론)
               └─ ⑥ 렌더 → -14 LUFS 정규화 → 완성본
```

## 무엇이 들어 있나

| 폴더 | 내용 |
|---|---|
| `skills/reels-recut/` | 위 6단계를 순서대로 진행하는 Claude Code 스킬 (`/reels-recut`) |
| `templates/editorial-green/` | 진녹색·크림 에디토리얼 매거진 스타일 HyperFrames 템플릿 |
| `templates/warm-creator/` | 따뜻한 크리에이터 토크 스타일 템플릿 (Pretendard, 다크 UI 카드, 손그림 마크) |
| `tools/` | LUT 생성·비교, 소스 준비, 자막 생성, 폰트 서브셋, 무음 분석, 음량 정규화 스크립트 |
| `grades/` | 검증된 그레이딩 프리셋(JSON) |
| `hypit/` | 로컬 WhisperX(CPU) 런타임 프로필 예시 |
| `docs/` | 작업 흐름, 카메라(줌) 규칙, AI 느낌 줄이기 체크리스트, B롤 계획 양식, 문제 해결 |
| `setup/` | Windows(PowerShell) / macOS·Linux 설치 스크립트 |

## 사용하는 오픈소스 (API 키 필요 없음)

| 도구 | 역할 | 설치 방식 |
|---|---|---|
| [hypit](https://github.com/hypit-ai/hypit) | 레퍼런스 분석, 단어 단위 받아쓰기(로컬 WhisperX), 프레임 그리드 | `npm i -g @hypit/hypit` + 스킬 |
| [HyperFrames](https://hyperframes.heygen.com) | HTML→영상 렌더, 인물 분리(remove-background), 그레이딩, 레지스트리 | `npx hyperframes` (버전 고정) |
| [Spectral Film LUT](https://github.com/JanLohse/spectral_film_lut) | 실제 필름 스톡을 시뮬레이션한 `.cube` LUT 생성 | Python 가상환경 |
| [auto-editor](https://github.com/WyattBlue/auto-editor) | 무음·숨 구간 분석 (긴 촬영본 1차 정리) | Python 가상환경 |
| [FunClip](https://github.com/modelscope/FunClip) | 긴 원본에서 문장 단위로 릴스 구간 추출 (로컬 ASR 모드만 사용) | 선택 설치 |
| [B-Roll Finder](https://github.com/louisedesadeleer/b-roll-finder) | 대본 기반 B롤 계획 방법론 (`/find-broll`) | Claude 스킬로 clone |

LLM API 키가 필요한 기능(FunClip의 LLM 클리핑, 유료 생성 모델)은 쓰지 않습니다.

## 빠른 시작

### 1. 설치

Windows (PowerShell):
```powershell
./setup/install.ps1            # FunClip까지: ./setup/install.ps1 -WithFunClip
```
macOS / Linux:
```bash
bash setup/install.sh          # FunClip까지: bash setup/install.sh --with-funclip
```
필요한 것: Node.js 22.15+, ffmpeg, Python 3.11+, [uv](https://docs.astral.sh/uv/), git.

### 2. Claude Code에서 실행
```
/reels-recut 레퍼런스: C:\영상\ref.mp4  내 클린본: C:\영상\clean.mov  스타일: warm-creator
```
스킬이 단계마다 결과(프레임 그리드, LUT 비교, 스냅샷)를 보여 주며 진행합니다.

### 3. 스크립트만 따로 쓰기
```bash
# 필름 LUT 만들기 (Kodak Vision3 250D → Vision 2383)
.venv/Scripts/python tools/make_lut.py --preset vision3-2383 --out luts/

# LUT 65% 강도로 미리보기 비교
python tools/compare_luts.py --video clean.mp4 --at 9 --luts luts/*.cube --strength 0.65 --out compare.png

# 받아쓰기 → 자막 장면 생성
python tools/build_captions.py --transcript transcript.json --style warm --out compositions/captions.html

# 쓰인 글자만 골라 한글 폰트 서브셋 주입
python tools/inject_fonts.py --project my-reel --family pretendard

# 완성본 음량 -14 LUFS / 피크 -1 dB
python tools/loudnorm.py render.mp4 final.mp4
```

## 스타일 템플릿

| | editorial-green | warm-creator |
|---|---|---|
| 톤 | 진녹색·크림·골드, 무드 있는 필름 | 밝고 따뜻한 거실, 필름 LUT 65% |
| 자막 | 녹색 박스 명조, 카라오케(말한 단어부터 크림) | 박스 없는 흰 Pretendard, 강조 문장만 크게 + 손그림 밑줄 |
| 핵심 그래픽 | 머리 뒤 대형 명조 타이포, 녹색 배경 전환, 구조 패널, 댓글 UI | 빨간 알약 + 제목, 다크 통계 카드, 손그림 취소선·동그라미, 아이콘 흐름도, 댓글 UI |
| 카메라 | 문장 단위 컷 + 짧은 펀치인 | 큰 컷 2개 + 부드러운 푸시 |

각 템플릿의 `README.md`에 바꿔야 할 곳(시간, 문구, 소스 파일)이 정리돼 있습니다.

## 꼭 지킬 것

- **줌은 적게, 크게.** 같은 테이크에서 확대 차이가 25% 미만이면 컷이 아니라 화면이 튄 것처럼 보입니다. → [docs/camera-rules.md](docs/camera-rules.md)
- **LUT는 60~70%.** 100%면 피부톤이 무너집니다.
- **숫자·사용법 장면은 실제 화면으로.** 지어낸 UI는 AI 티의 1순위입니다. → [docs/anti-ai-checklist.md](docs/anti-ai-checklist.md)
- **효과음은 최소로.** 카드 등장 2~3번이면 충분합니다.
- 레퍼런스 영상의 화면·음원은 결과물에 쓰지 않습니다(스타일 분석용).

## 라이선스

이 저장소의 코드와 문서는 MIT 라이선스입니다. 함께 쓰는 도구와 폰트·음원의 라이선스는
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)를 확인하세요.
