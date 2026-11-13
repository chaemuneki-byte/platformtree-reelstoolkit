# 문제 해결 (실제로 겪은 것들)

## hypit
| 증상 | 원인 / 해결 |
|---|---|
| `uv failed: spawn uv ENOENT` | WhisperX 설치에 uv가 필요. `winget install astral-sh.uv` 후 **새 터미널**, 또는 PATH에 uv 폴더 추가 |
| `Torch not compiled with CUDA enabled` | 배포된 잠금 환경의 torch가 CPU 전용. 프로필에서 `expectedDevice: cpu`, `expectedCompute: int8` (`hypit/runtime.example.json`) |
| Node 버전 오류 | `@hypit/hypit`은 Node 22.15 이상 필요 |
| `Audio Track ... already contains Clip` | 같은 Window를 두 Clip이 공유. 클립마다 별도 `time:Window` 선언 |
| `Temporal Instant falls outside Timeline` | 효과음 Window가 영상 끝을 넘음. 길이를 줄인다 |
| `Text sequence ... selects grapheme N, but only M exist` | 글자 단위 애니메이션의 end-index는 실제 글자 수(공백·마침표 포함)와 같아야 함 |
| `transform origin must remain constant` | Visual Motion 안에서 기준점 변경 불가. 기준점 고정 + y 보정(192 × (scale−1)) |

## HyperFrames
| 증상 | 원인 / 해결 |
|---|---|
| 탐색 시 영상이 멈춤 | 키프레임 간격이 김. `tools/prep_footage.py`가 `-g 30`으로 다시 인코딩 |
| `gsap_animates_clip_element` | `.clip` 요소의 visibility를 건드림. 안쪽 요소만 애니메이션 |
| 한글이 기본 글꼴로 나옴 | 번들 폰트는 라틴만. `tools/inject_fonts.py`로 @font-face 주입 |
| 그레이딩이 인물 컷아웃과 A롤에서 다름 | 두 `<video>`에 같은 grading JSON을 각각 적용 |
| 인물 분리 결과 확인 | ffmpeg 필터 체인에서 ProRes 4444 알파가 사라질 수 있음. 프레임을 `-pix_fmt rgba` PNG로 뽑은 뒤 합성해서 확인 |

## 음량
- 렌더 결과는 보통 -15 LUFS 안팎. `tools/loudnorm.py`로 2-pass 정규화(-14 LUFS, 트루피크 -1 dB).
