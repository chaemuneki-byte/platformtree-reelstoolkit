# Third-party notices

이 저장소는 아래 도구를 **설치해서 사용**합니다. 소스를 포함(vendoring)하지 않으며, 각 도구의 라이선스는 해당 저장소를 따릅니다.
설치 전에 각 저장소의 LICENSE를 직접 확인하세요.

| 도구 | 저장소 | 비고 |
|---|---|---|
| hypit | https://github.com/hypit-ai/hypit | Apache-2.0 with conditions. 저장소 LICENSE 확인 |
| HyperFrames CLI | https://www.npmjs.com/package/hyperframes | HeyGen. 텔레메트리 opt-out 가능 |
| Spectral Film LUT | https://github.com/JanLohse/spectral_film_lut | MIT. PyPI `spectral-film-lut` |
| auto-editor | https://github.com/WyattBlue/auto-editor | 퍼블릭 도메인(Unlicense). 첫 실행 시 공식 릴리스 바이너리를 내려받음 |
| FunClip | https://github.com/modelscope/FunClip | MIT. 로컬 ASR 모드만 사용 |
| B-Roll Finder | https://github.com/louisedesadeleer/b-roll-finder | MIT. Claude 스킬로 clone |

## 폰트

템플릿은 설치된 npm 패키지에서 **쓰인 글자가 든 서브셋 파일만** 복사해 씁니다(`tools/inject_fonts.py`).

| 폰트 | 패키지 | 라이선스 |
|---|---|---|
| Pretendard | `pretendard` | SIL Open Font License 1.1 |
| Noto Serif KR / Noto Sans KR | `@fontsource-variable/noto-serif-kr`, `@fontsource-variable/noto-sans-kr` | SIL Open Font License 1.1 |
| IBM Plex Mono | HyperFrames 번들 | SIL Open Font License 1.1 |

## 음원

저장소에는 음원을 넣지 않습니다. 배경음악과 효과음은 HyperFrames `media-use`로 Openverse(CC0·CC BY)에서 받습니다.
CC BY 음원은 게시할 때 반드시 출처를 표기하세요(`media-use`가 `CREDITS.md`를 만들어 줍니다).
