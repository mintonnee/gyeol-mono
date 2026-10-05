# 한글 배율 비교

`index.html`을 브라우저에서 열면 같은 문장을 마루 부리 한글 배율 1.00/1.05/1.10/1.15로
나란히 비교할 수 있습니다. 상단 체크박스로 표시할 시안을 고릅니다.
크기 12–32px, 행간, 밝은/어두운 배경, 셀 격자와 직접 입력을 지원합니다.
폰트 로드 상태가 **비교 폰트 N개 로드 완료**인지 확인하세요.

## 재생성

저장소 루트에서 실행합니다. 기존 프리뷰나 기본 빌드 설정은 변경하지 않습니다.

```sh
uv run gyeol-mono fetch --source ibm-plex-mono --source maru-buri --source ibm-plex-sans-jp
uv run python scripts/compare_hangul.py
uv run python -m http.server 8765 --bind 127.0.0.1 --directory comparisons/hangul
```

브라우저에서 http://127.0.0.1:8765 를 엽니다. 실행 위치는 저장소 루트여야 합니다.
`--fetch-ridi`를 붙이거나 `upstream/ridi-batang/RIDIBatang.otf`가 있으면 리디바탕 1.00을
참고 시안으로 추가합니다(기본 표시는 꺼짐). 이미 내려받은 리디 파일은 재사용하며,
고정 SHA-256과 다르면 중단합니다.

## 비교 조건과 산출물

- Regular만 비교. 리디 공식 파일에 포함된 스타일은 Regular입니다.
- IBM Plex Mono 2.5.0 영문 + IBM Plex Sans JP 3.0.0 일본어를 공통 사용합니다.
- 마루 부리 한글 윤곽 배율 1.00/1.05/1.10/1.15(`CJK_SCALE_CANDIDATES`), 리디바탕 1.00.
  일본어 배율 1.00, UPM 1000, ASCII 폭 600, 한글 폭 1200.
- 기본 시안은 baseline(y=0) 기준으로 확대합니다. `Maru110C`/`Maru115C`는 마루 부리 1.00의
  음절 bbox 중심 중앙값(y=300)을 고정한 채 확대해 영문과의 상하 위치를 유지합니다.
  `Maru110CU{10,20,30,40,50}`은 `Maru110C`에서 한글만 N unit 올린 시안으로, 영문을 N unit 내린 것과
  상대 위치가 같습니다. 기본 표시는 `Maru110C`, `+30`, `+40`, `+50`입니다.
- 원본 advance를 기준으로 한글 윤곽을 1200-unit 셀 중앙에 배치합니다.
- 리디 CFF 윤곽을 quadratic으로 변환하며 허용 근사 오차는 0.001 em입니다.
- 한글 원본 힌팅과 GSUB/GPOS는 복사하지 않습니다. 커닝·분해형 조합을 포함한
  원본 서체 전체의 렌더링 비교가 아니라 현재 Gyeol Mono 합성 방식의 비교입니다.
- `samples.json`: 수정 가능한 공통 비교 문장.
- `metrics.json`: 시안별 배율·소스 해시·버전·문자 지원 범위·셀 경계 초과 수·12-unit
  수평 guard 위반 수·완성형 음절 잉크 폭 중앙값/최댓값·샘플 누락 문자.
- `glyph-metrics.csv`: 지원 한글 전체의 원본 폭과 출력 폭, 출력 윤곽 bbox.
  원본 폭은 source UPM 단위, bbox는 출력 UPM 1000 단위입니다.
- `GyeolCompare{Maru100,Maru105,Maru110,Maru115,Maru110C,Maru115C,Maru110CU{10–50},Ridi100}-Regular.ttf`, `.woff2`:
  이름을 분리한 비교 폰트.
- `template.html`: 비교 페이지 원본. 스크립트가 문장 데이터를 넣어 `index.html` 생성.

`cell_overflow_count`는 실제 픽셀 잘림 판정이 아니라, 출력 윤곽이
x=0..1200, y=-275..1025를 넘는 글리프 수입니다.
NFD 행은 시스템 폰트로 대체될 수 있으므로 서체 평가 점수에 포함하지 마세요.
14/16/18/20px와 밝은/어두운 배경에서 속공간, 받침 뭉침, 영문과의 크기 조화,
연속 읽기 피로도를 확인하는 용도입니다. Bold/Italic과 실제 터미널 검증은 별도입니다.

## 출처

- 리디바탕: https://ridicorp.com/ridibatang/
- 공식 파일: https://ridicorp.com/wp-content/themes/ridicorp/css/font/RIDIBatang.otf
- 버전: 1.0.1 Build 20191001
- SHA-256: `f13a49c0815d254ac15e392953a0b056613dec08ceb378e54eeed14c4fda9a54`
- 리디바탕 저작권은 리디주식회사에 있으며 공식 페이지는 SIL OFL 1.1을 명시합니다.
- 나머지 폰트의 배포 출처와 해시는 루트 `sources.toml`을 참조하세요.
  IBM 라이선스는 `upstream/ibm-plex-mono/ibm-plex-mono/LICENSE.txt` 및
  `upstream/ibm-plex-sans-jp/ibm-plex-sans-jp/LICENSE.txt`, 마루 부리는
  `sources.toml`의 `license_url`에 있습니다.

현재 산출물은 로컬 비교용입니다. 외부 배포 패키지는 구성하지 않았습니다.
