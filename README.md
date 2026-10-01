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

## 라이선스

- **소스 코드**: 빌드 스크립트·테스트·문서 등 이 저장소의 소스는 [MIT License](LICENSE)입니다.
- **글꼴**: 여기서 생성하는 Gyeol Mono 글꼴 파일은 [SIL Open Font License 1.1](OFL.txt)입니다.
  Gyeol Mono는 아래 OFL 글꼴의 Modified Version이므로 같은 라이선스를 그대로 따르며,
  원본 저작권 고지는 `OFL.txt`에 포함되어 있습니다.

| 원본 | 저작권자 | Reserved Font Name |
| --- | --- | --- |
| [IBM Plex Mono, IBM Plex Sans JP](https://github.com/IBM/plex) | IBM Corp. | `Plex` |
| [마루 부리](https://hangeul.naver.com/font) | NAVER Corporation | `MaruBuri` 외 네이버 글꼴 이름 |

- 글꼴 이름에 Reserved Font Name을 쓰지 않기 위해 패밀리 이름은 `Gyeol Mono`입니다.
  수정해 재배포할 때도 위 이름은 사용할 수 없습니다.
- 글꼴 파일을 재배포할 때는 `OFL.txt`를 함께 포함해야 하며, 글꼴만 단독으로 판매할 수 없습니다.
- IBM, 네이버를 비롯한 원저작자는 이 결과물을 보증하거나 후원하지 않습니다.
- 비교 실험용 Klee One과 리디바탕도 OFL 1.1 글꼴이지만 최종 글꼴에는 포함되지 않습니다.
