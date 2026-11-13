# hypit 설정 (API 키 없이 로컬로)

hypit은 이 툴킷에서 **분석과 받아쓰기**를 맡습니다. 생성 모델(HypiHub 등 유료)은 쓰지 않습니다.

## 프로젝트에 런타임 연결
```bash
cd my-reel
echo '{"name":"my-reel","private":true,"type":"module","hypit":{"project":true}}' > package.json
hypit runtime init                       # 기본 프로필 생성
cp ../platformtree-reelstoolkit/hypit/runtime.example.json hypit.runtime.json   # 로컬 WhisperX(CPU) 프로필로 교체
hypit programs up --endpoint whisperx.local   # 첫 실행: Python 환경 + large-v3 + ko/en 정렬 모델 다운로드
```
- `uv`가 PATH에 있어야 합니다(없으면 `spawn uv ENOENT`).
- 배포된 환경의 torch는 CPU 전용입니다. `cuda`로 바꾸면 `Torch not compiled with CUDA enabled`로 실패합니다.
  CPU(int8)로도 18초 영상 받아쓰기가 20초 안팎입니다.

## 자주 쓰는 명령
```bash
hypit media probe ref.mp4
hypit media tiles ref.mp4 --start 0 --end 48 --every 1 --columns 6 --rows 3 --cell 300 --to evidence/overview
hypit media tile ref.mp4 --start 0 --end 3.2 --every 0.2 --columns 8 --cell 300 --to evidence/hook.jpg
hypit transcribe ref.mp4 --language ko --to transcript.json
```
받아쓰기 결과는 `passages[].words[]`에 `text`, `start_seconds`, `end_seconds`가 들어 있고,
`tools/build_captions.py`가 그대로 읽습니다.
