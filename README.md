# Gyeol Mono / 결 모노

IBM Plex Mono의 영문, **마루 부리의 한글**, IBM Plex Sans JP의 일본어를 합성하는
600/1200-unit duospace 폰트 빌더입니다.

## 빌드

```sh
uv sync
uv run gyeol-mono fetch --source ibm-plex-mono --source maru-buri --source ibm-plex-sans-jp
uv run gyeol-mono build
```

기본 빌드는 `fonts/preview-b/`에 네 스타일의 TTF/WOFF2를 생성합니다.
원본 URL·버전·SHA-256은 `sources.toml`에서 고정합니다. 한글·일본어 기본 배율은 1.00입니다.

| 출력 | 영문 | 한글 | 일본어 |
| --- | --- | --- | --- |
| Regular | Regular | 마루 부리 Regular | Regular |
| Italic | true Italic | 마루 부리 Regular upright | Regular upright |
| Bold | SemiBold | 마루 부리 SemiBold | SemiBold |
| Bold Italic | SemiBold Italic | 마루 부리 SemiBold upright | SemiBold upright |

Bold는 세 스크립트 모두 SemiBold 원본을 사용합니다.
한글 synthetic bold/italic은 적용하지 않습니다. 현재 구현은 non-Powerline preview
빌드이며 Powerline 패키징과 NFD 한글 shaping은 아직 구현하지 않았습니다.

```sh
uv run gyeol-mono plan --json
uv run pytest
uv run ruff check src tests scripts
```

`plan`은 목표 빌드 행렬을 나타내므로 미구현 PL 단계도 포함합니다.
JSON의 `hangul_source_style`과 `japanese_source_style`로 스크립트별 원본 스타일을
확인할 수 있습니다.

리디바탕은 `sources.toml`에 비교 재현용으로만 남겨 두었습니다. CFF 윤곽 입력은
TTF용 quadratic 윤곽으로 변환해 병합할 수 있습니다.
마루 부리/리디바탕 한글 비교 페이지의 재생성 방법은 `comparisons/hangul/README.md`,
상세 설계와 이전 실험 기록은 `docs/specs/001-build-display-serif-mono.md`를 참조하세요.

마루 부리는 [네이버 글꼴 모음 공식 배포본](https://hangeul.naver.com/font)을 사용합니다.
배포 패키지에는 각 원본의 라이선스와 저작권 고지가 필요합니다.
