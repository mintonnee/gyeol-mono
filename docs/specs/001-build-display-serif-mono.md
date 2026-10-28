# 001. Gyeol Mono 빌드

- 상태: Draft
- 작성일: 2026-07-11
- 최종 수정일: 2026-10-28
- 대상 구현: 정적 TTF 및 WOFF2 패밀리

## 1. 개요

이 문서는 IBM Plex Mono의 라틴 글리프, 마루 부리의 한글 글리프와 IBM Plex Sans JP의 가나·한자 글리프를 결합한 `Gyeol Mono`를 만드는 데 필요한 설계와 빌드 규칙을 정의한다.

결과 글꼴은 라틴 문자에 600 units, 한글·가나·한자에 1,200 units의 advance를 사용하는 2폭 구조다. 따라서 엄밀히는 모든 글리프가 동일한 폭을 갖는 monospace가 아니라, 라틴 1셀과 CJK 2셀로 구성된 duospace 글꼴이다. 사용자에게는 일반적인 CJK 코딩 글꼴과 동일하게 모노스페이스 패밀리로 제공한다.

배포 패밀리는 `Gyeol Mono` 하나이며 Powerline 및 Powerline Extra 글리프를 기본으로 포함한다. 별도 `PL` 패밀리는 만들지 않는다(12.10). 전체 Nerd Fonts 아이콘 세트는 포함하지 않는다. 기본 표시가 emoji인 코드포인트는 어느 원본에서 왔든 최종 글꼴에서 제외하고 OS emoji 글꼴 fallback에 맡긴다(6.1).

## 2. 목표

- IBM Plex Mono의 라틴 디자인, 숫자, 문장부호와 true italic을 보존한다.
- 마루 부리의 한글 조형을 2셀 환경에 맞춰 확대하고 광학적으로 중앙 정렬한다.
- 일본어 가나와 한자에 정돈된 손글씨 또는 친근한 고딕 인상을 제공한다.
- Klee One과 IBM Plex Sans JP를 동일 조건에서 비교한 결과에 따라 IBM Plex Sans JP를 최종 일본어 원본으로 사용한다.
- 본문 크기와 디스플레이 크기에서 모두 읽기 좋은 한영일 혼용 결과를 만든다.
- 편집기와 터미널에서 ASCII 1셀, CJK 2셀 정렬을 보장한다.
- 기본 패밀리에서 Powerline 및 Powerline Extra 구분자를 라틴 1셀 크기로 제공한다.
- 컬러 emoji가 OS emoji 글꼴로 fallback되도록 emoji presentation 코드포인트를 글꼴에서 비워 둔다.
- 원본 다운로드부터 산출물 생성까지 재현 가능한 빌드 파이프라인을 제공한다.
- 구조 검사, shaping 검사, 렌더링 검수를 자동화할 수 있는 기반을 마련한다.

## 3. 비목표

초기 버전에서는 다음 항목을 지원하지 않는다.

- 전체 Nerd Fonts 아이콘 세트
- 컬러 또는 흑백 emoji 글리프 및 emoji ZWJ·피부색·국기 시퀀스 shaping
- Variable Font
- 한글 및 일본어 글리프의 synthetic italic 또는 oblique
- ExtraLight, Light, Medium, SemiBold, ExtraBold 등 별도 사용자 노출 웨이트
- CJK 언어 태그에 따른 JP/KR `locl` 전환
- CFF outline 기반 OTF 출력 (CFF 입력은 지원)
- 원본 폰트의 소스 편집 또는 새로운 글리프 디자인

초기 출력 포맷은 TTF와 WOFF2로 제한한다. 한글 원본이 CFF 윤곽이면 0.001 em 허용 근사 오차로 quadratic으로 변환하고 TrueType 방향으로 반전한다. 원본 한글 힌팅은 가져오지 않는다.

## 4. 원본과 버전 고정

빌드는 다음 배포처와 버전을 canonical upstream으로 사용한다. 다운로드 URL과 실제 파일 경로는 저장소 루트의 `sources.toml`을 단일 진실 공급원으로 삼는다.

| 역할 | 원본 및 버전 | 배포 자산 | SHA-256 |
| --- | --- | --- | --- |
| 라틴 및 기본 OpenType 테이블 | [IBM Plex Mono 2.5.0](https://github.com/IBM/plex/releases/tag/%40ibm%2Fplex-mono%402.5.0) | `ibm-plex-mono.zip` | `6d23f01257663d8cc49a0d64c22ced630b79e0e2a0ac08a0da86e9a38bbc481c` |
| 한글 및 한글 전각 문장부호 | [마루 부리 2022 완성본](https://hangeul.naver.com/font) | `maruburi.zip` | `39e3bb6a00b4543563a745195a6a89282c5a1f0f8b71923ff15c1bc7c135fa0c` |
| 일본어 | [IBM Plex Sans JP 3.0.0](https://github.com/IBM/plex/releases/tag/%40ibm%2Fplex-sans-jp%403.0.0) | `ibm-plex-sans-jp.zip` | `4c14c41552934b0bc92fc216a76b36bdc78f745dfbeed1115f9b8bc405ee314f` |
| Powerline 글리프 | Nerd Fonts Font Patcher에 포함된 Powerline/Powerline Extra | Font Patcher 입력 자산 | Nerd Fonts 버전 결정 후 추가 |
| Emoji presentation 판정 | [Unicode 18.0.0](https://www.unicode.org/versions/Unicode18.0.0/) `emoji-data.txt` | `emoji-data-18.0.0.txt` | `80d00f8e616a0ef27fd6b8de3b758c06383b5d917e2977709578e68baf733bf1` |

IBM Plex Mono에서는 complete TTF의 Regular, Italic, SemiBold, SemiBold Italic을 사용한다. IBM Plex Sans JP에서는 outline 변환 후 무효가 되는 힌팅을 가져오지 않도록 unhinted complete TTF의 Regular와 SemiBold를 사용한다. 마루 부리에서도 Regular와 SemiBold TTF만 추출한다.

마루 부리 ZIP에는 라이선스 파일이 포함되어 있지 않으므로 배포 패키지를 만들 때 [네이버 라이선스 전문](https://help.naver.com/service/30016/contents/18088?osType=PC&lang=ko)을 별도로 포함한다. `emoji-data.txt`처럼 ZIP이 아닌 단일 파일은 `archive_format = "file"`로 선언하고, 공식 URL의 내용이 바뀌면 SHA-256 검증에서 중단한다.

다운로더는 `sources.toml`의 URL 및 SHA-256을 검증하고 선언된 파일만 `upstream/` 아래에 추출한다. `latest` URL을 빌드 입력으로 직접 사용하면 안 된다. 원본 파일과 생성 파일은 Git에서 제외하고 manifest만 추적한다.

참고 자료:

- [IBM Plex](https://github.com/IBM/plex)
- [IBM Plex 라이선스](https://github.com/IBM/plex/blob/master/LICENSE.txt)
- [네이버 글꼴 모음 및 마루 부리 사용 안내](https://hangeul.naver.com/font)
- [IBM Plex Sans JP 메타데이터](https://github.com/google/fonts/blob/main/ofl/ibmplexsansjp/METADATA.pb)
- [Nerd Fonts Font Patcher](https://github.com/ryanoasis/nerd-fonts#font-patcher)
- [Nerd Fonts Glyph Sets and Code Points](https://github.com/ryanoasis/nerd-fonts/wiki/Glyph-Sets-and-Code-Points)
- [Unicode Technical Standard #51: Unicode Emoji](https://www.unicode.org/reports/tr51/)

## 5. 패밀리와 스타일

최종 family name은 `Gyeol Mono`로 확정한다. 이름의 `Gyeol`은 글자의 결, 획의 질감과 서로 다른 스크립트가 한 문장 안에서 만드는 흐름을 의미한다. IBM Plex의 Reserved Font Name인 `Plex`를 최종 사용자 노출 이름에 사용하지 않는다.

배포 패밀리는 하나다.

| 패밀리 | 용도 | Powerline 포함 여부 |
| --- | --- | --- |
| `Gyeol Mono` | 터미널, 편집기, 일반 디스플레이, 웹 | 포함 |

Powerline subset만 포함하므로 이름에 `Nerd Font`, `NF` 또는 `PL` 접미사를 사용하지 않는다. 이전 초안의 `Gyeol Mono PL` 패밀리는 폐지했다(12.10).

### 5.1 OpenType 및 파일 이름

OpenType family name은 플랫폼 호환성을 위해 ASCII `Gyeol Mono`를 사용한다. `결 모노`는 README, 웹사이트와 specimen에서 사용하는 한국어 표시 이름이며 OpenType의 기본 family name으로 사용하지 않는다.

패밀리 이름은 다음과 같다.

| 스타일 | Full name | PostScript name | 파일 이름 |
| --- | --- | --- | --- |
| Regular | `Gyeol Mono Regular` | `GyeolMono-Regular` | `GyeolMono-Regular.ttf` |
| Italic | `Gyeol Mono Italic` | `GyeolMono-Italic` | `GyeolMono-Italic.ttf` |
| Bold | `Gyeol Mono Bold` | `GyeolMono-Bold` | `GyeolMono-Bold.ttf` |
| Bold Italic | `Gyeol Mono Bold Italic` | `GyeolMono-BoldItalic` | `GyeolMono-BoldItalic.ttf` |

`name` ID 1과 16은 `Gyeol Mono`로 통일한다. ID 2와 17은 `Regular`, `Italic`, `Bold`, `Bold Italic` 중 해당 값을 사용한다. ID 4와 6은 위 표의 Full/PostScript name을 사용한다.

후보 비교 빌드는 동시에 설치해 비교할 수 있도록 사용자 노출 family를 `Gyeol Mono Preview A`(Klee One)와 `Gyeol Mono Preview B`(IBM Plex Sans JP)로 분리했다. B안을 확정한 뒤 Klee One은 저장소에서 제거했고(12.11), 현재 preview 빌드는 이미 설치된 시험용 글꼴과 이어지도록 `Gyeol Mono Preview B` 이름을 유지한다. 최종 릴리스에는 Preview 이름을 사용하지 않는다.

### 5.2 웨이트 및 스타일 매트릭스

초기 릴리스는 터미널과 IDE의 RIBBI 선택에 맞춰 다음 네 face를 생성한다.

| 출력 스타일 | 출력 CSS weight | IBM Plex Mono 원본 | 마루 부리 원본 | IBM Plex Sans JP 원본 |
| --- | ---: | --- | --- | --- |
| Regular | 400 | Regular | Regular upright | Regular upright |
| Italic | 400 | true Italic | Regular upright | Regular upright |
| Bold | 700 | SemiBold | SemiBold upright | SemiBold upright |
| Bold Italic | 700 | SemiBold Italic | SemiBold upright | SemiBold upright |

두꺼운 face는 세 스크립트의 획 밀도를 일치시키기 위해 모두 SemiBold 600 원본을 사용한다. Synthetic embolden은 적용하지 않는다. 다만 최종 사용자 노출 이름과 `OS/2.usWeightClass`는 Bold 700으로 설정한다. 이는 일부 터미널이 `SemiBold` face를 ANSI SGR 1 또는 Bold face로 선택하지 않는 문제를 피하기 위한 의도적인 매핑이다.

후보 비교 단계에서는 Klee One과 IBM Plex Sans JP에 대해 각각 RIBBI 4개 정적 TTF를 생성했다. 최종 배포에는 IBM Plex Sans JP를 사용한 `Gyeol Mono` RIBBI 4개만 포함한다.

## 6. 글리프 소유권

중복 코드포인트를 무조건 병합하지 않는다. 다음 표에 따라 어느 원본의 글리프를 유지할지 명시적으로 결정한다.

| 문자 범위 또는 분류 | 소유 원본 | 목표 advance |
| --- | --- | ---: |
| Basic Latin 및 ASCII | IBM Plex Mono | 600 |
| Latin-1 및 Latin Extended | IBM Plex Mono | 600 |
| ASCII 숫자와 일반 문장부호 | IBM Plex Mono | 600 |
| IBM Plex Mono의 OpenType 대체 글리프 | IBM Plex Mono | 원본 유지 |
| 한글 완성형 `U+AC00–U+D7A3` | 마루 부리 | 1,200 |
| 한글 자모 `U+1100–U+11FF` | 마루 부리 | 1,200 |
| 호환용 한글 자모 `U+3130–U+318F` | 마루 부리 | 1,200 |
| 한글 자모 확장-A `U+A960–U+A97F` | 마루 부리 | 1,200 |
| 한글 자모 확장-B `U+D7B0–U+D7FF` | 마루 부리 | 1,200 |
| 히라가나 `U+3040–U+309F` | 선택한 일본어 원본 | 1,200 |
| 가타카나 `U+30A0–U+30FF` | 선택한 일본어 원본 | 1,200 |
| 가타카나 확장 `U+31F0–U+31FF` | 선택한 일본어 원본 | 1,200 |
| 한자 | 선택한 일본어 원본의 실제 `cmap` | 1,200 |
| CJK 기호 및 문장부호 `U+3000–U+303F` | 기본적으로 선택한 일본어 원본 | 1,200 |
| 전각 및 반각 문자 `U+FF00–U+FFEF` | 문자별 allowlist | 600 또는 1,200 |
| Powerline 및 Powerline Extra | Nerd Fonts 자산 | 600 |
| `U+2717` BALLOT X | IBM Plex Mono `U+274C` 윤곽(6.1) | 600 |
| `Emoji_Presentation=Yes` 코드포인트 | 없음(OS emoji 글꼴 fallback) | — |

위 한글 범위는 소유권 규칙이며 실제 원본 `cmap`에 있는 글리프만 복사한다. 마루 부리는 완성형 11,172자와 호환용 자모 51자를 지원하지만 결합 자모 `U+1100–U+11FF`와 자모 확장-A/B는 포함하지 않는다. 현재 빌더는 NFD 조합을 지원하지 않는다.

`₩`, 따옴표, 대시, 화살표, 괄호, 전각 ASCII처럼 둘 이상의 원본에 존재하는 문자는 실제 터미널 셀 동작과 시각적 조화를 확인한 후 allowlist로 관리한다.

마루 부리와 IBM Plex Sans JP에 포함된 라틴 글리프는 복사하지 않는다. 한자는 임의의 전체 Unicode 범위를 가정하지 않고 IBM Plex Sans JP의 `cmap`에 실제로 존재하는 글리프만 복사한다.

초기 버전의 한자 기본 형태는 일본어 원본이 제공하는 JP glyph form이다. 터미널과 IDE가 일반적으로 `ko` 또는 `ja` language tag를 제공하지 않는 점을 고려해 JP/KR `locl` 전환은 구현하지 않는다.

### 6.1 Emoji presentation 코드포인트 제외

터미널과 대부분의 렌더러는 기본 글꼴에 글리프가 있으면 그 글리프를 먼저 사용한다. 기본 표시가 emoji인 문자에 흑백 글리프가 남아 있으면 OS의 컬러 emoji가 가려지므로 다음 규칙을 적용한다.

- 고정한 `emoji-data.txt`에서 `Emoji_Presentation=Yes`인 코드포인트를 최종 `cmap`의 모든 서브테이블에서 제거한다.
- 원본을 가리지 않는다. IBM Plex Mono 베이스, CJK 병합 원본, Nerd Fonts 자산 모두에 적용한다.
- 판정 기준은 `Emoji` 속성이 아니라 `Emoji_Presentation` 속성이다. `#`, `*`, `0–9`, `©`, `®`, `♥`, `★`, `☰`처럼 `Emoji=Yes`이지만 기본 표시가 텍스트인 문자는 유지한다. 터미널 UI에서는 이 기호들이 글꼴의 1셀 흑백 글리프로 표시되는 편이 정렬에 유리하다.
- `U+FE0E`, `U+FE0F` variation selector와 emoji 시퀀스용 `GSUB`는 추가하지 않는다. VS16이 붙은 텍스트 기호의 컬러 전환과 emoji 셀 폭(wcwidth)은 터미널과 OS가 결정한다.
- 매핑을 제거한 뒤 다른 `cmap` 항목, composite glyph, OpenType layout 테이블(`GDEF`, `GPOS`, `GSUB`) 어디에서도 참조하지 않는 글리프는 glyph order에서 제거한다. layout 테이블이 참조하는 글리프는 보수적으로 남긴다.
- 제거는 모든 원본 병합과 패치가 끝난 뒤, 메타데이터와 메트릭을 최종 정규화하기 전에 한 번 수행한다. 따라서 이후 단계가 emoji 코드포인트를 다시 추가하지 않는 한 결과가 원본 구성에 의존하지 않는다.
- 원본이 emoji 코드포인트에 텍스트용 흑백 기호를 디자인해 둔 경우, 제거 직전에 그 글리프를 의미가 같은 text presentation 코드포인트에 추가 매핑해 보존할 수 있다. 대상 코드포인트가 이미 매핑되어 있으면 덮어쓰지 않는다. 현재 alias는 `U+274C` → `U+2717` 하나다.

`Emoji_Presentation=Yes` 문자는 Regional Indicator를 제외하면 모두 East Asian Width가 `W`다. 터미널은 이 문자에 2셀을 배정하므로, 원본의 1셀(600) 흑백 글리프를 남기면 컬러 emoji를 가릴 뿐 아니라 글리프 뒤에 빈 셀이 생긴다.

2026-10-28 preview B Regular 기준 해당 코드포인트는 IBM Plex Mono에서 온 `U+274C`(❌) 하나였다. 이 글리프는 glyph order에서 `uni2713`(✓) 바로 뒤에 있고, ✓와 같은 획 두께의 1셀 X 형태라 PASS/FAIL 같은 텍스트 표기용 ✓/✗ 짝으로 설계된 것으로 보인다. IBM Plex Mono에는 `U+2717`이 없으므로 이 윤곽을 `U+2717`(✗, East Asian Width `N`)에 매핑해 보존하고 `U+274C`는 OS emoji로 넘긴다. JetBrains Mono 2.304도 ✓/✗를 1셀 짝으로 제공한다.

다른 터미널 글꼴도 emoji presentation 코드포인트를 일부 포함한다(2026-10-28 확인). JetBrains Mono 2.304 Regular는 `U+26A1`(⚡), Cascadia Code 2407.24 Regular는 `U+25FD`, `U+25FE`, `U+2B1B`, `U+2B1C`를 1셀 흑백 글리프로 포함하고 Roboto Mono는 포함하지 않는다. Cascadia Code NF는 여기에 Nerd Fonts의 `U+26A1`이 더해진다. IBM Plex Sans JP Regular와 마루 부리 Regular에는 `U+1F000–U+1FAFF` 영역 글리프가 각각 1자, 27자 있지만 6장의 소유권 규칙에 따라 복사되지 않는다. 향후 Nerd Fonts 세트를 추가하면 Octicons의 `U+26A1`(⚡)처럼 PUA 밖 emoji 코드포인트를 쓰는 아이콘이 생기므로 이 규칙이 함께 걸러야 한다.

## 7. 메트릭

Regular TTF에서 확인한 주요 입력 메트릭은 다음과 같다.

| 항목 | IBM Plex Mono Regular | 마루 부리 Regular |
| --- | ---: | ---: |
| unitsPerEm | 1,000 | 1,000 |
| 대표 라틴 `A` advance | 600 | 675 |
| 한글 `가` advance | 없음 | 970 |
| hhea ascent | 1,025 | 965 |
| hhea descent | -275 | -380 |
| Typo ascender | 780 | 965 |
| Typo descender | -220 | -380 |

### 7.1 수평 메트릭

- 라틴 셀 폭은 IBM Plex Mono의 600 units를 그대로 유지한다.
- 한글과 일본어 셀 폭은 라틴 셀의 정확히 두 배인 1,200 units로 설정한다.
- CJK outline은 1,200 전체로 늘리지 않고, 셀 안에서 확대 후 광학적으로 중앙 정렬한다.
- CJK 글리프의 좌우 side bearing에는 최소 guard를 둔다.
- 기본 guard 후보는 라틴 셀 폭의 2%, 즉 12 units이며, 렌더링 결과에 따라 조정한다.
- `hhea.advanceWidthMax`는 최종 한글 폭을 반영해 1,200 이상이어야 한다.
- 600/1,200의 규칙적인 2폭 글꼴이므로 `post.isFixedPitch`와 PANOSE proportion은 monospaced로 설정한다.

### 7.2 CJK 확대율

한글 확대율은 1.10, 수직 anchor y=300, 수직 이동 +30으로 확정했다(12.9). 일본어는 1.00을 유지한다. 한글과 일본어 원본에 서로 다른 optical scale을 허용하며 빌드 CLI는 `--hangul-scale`과 `--japanese-scale`을 분리해 받는다. 비교에 사용한 후보는 다음과 같다.

```text
1.00
1.05
1.10
1.15
```

한글 윤곽은 baseline(y=0)이 아니라 `HANGUL_Y_ANCHOR`(y=300)를 고정점으로 확대한다. 300은 마루 부리 Regular 완성형 음절 bbox 중심의 중앙값이며, baseline 기준 확대는 한글 중심을 위로 밀어 영문과의 상하 정렬을 깨뜨린다(1.15에서 중심 345). 같은 anchor를 SemiBold에도 적용하며 SemiBold 중심 중앙값은 302다. 확대 후 `HANGUL_Y_SHIFT`(+30)만큼 한글을 올려 영문을 상대적으로 내린다. 영문 글리프 자체를 내리지 않는 이유는 박스·블록·Powerline 글리프의 셀 정렬과 IBM Plex Mono descender를 보존하기 위해서다.

확대율은 스크립트와 웨이트별로 다를 수 있다. 한 개의 상수를 모든 CJK 글리프에 강제하지 않는다. 각 글리프는 요청 배율을 적용하되 셀의 수평 guard 또는 최종 수직 셀을 벗어나면 개별적으로 배율을 제한한다.

Klee One과 IBM Plex Sans JP 비교 빌드에는 원본 자체의 차이만 평가할 수 있도록 동일한 1.00 scale과 수직 셀을 적용했다. 최종 B안에서는 한글과 일본어 optical scale을 분리해 미세 조정할 수 있어야 한다.

### 7.3 수직 메트릭

초기 셀 후보는 IBM Plex Mono의 HHEA 영역을 따른다.

```text
xMin = 0
xMax = 600
yMin = -275
yMax = 1025
baseline-to-baseline = 1300
```

Powerline 심볼과 모든 CJK 글리프가 최종 `yMin/yMax` 안에 있어야 한다. `hhea`, `OS/2` Typo metrics 및 Windows metrics가 플랫폼별로 다른 줄 높이를 만들지 않도록 최종 빌드 단계에서 정규화한다.

Nerd Fonts patcher가 중간 파일의 수직 메트릭을 변경할 수 있으므로, 최종 병합 이후 이름과 메트릭을 다시 적용한다.

## 8. Italic 정책

Italic variant는 IBM Plex Mono가 제공하는 true italic TTF를 라틴 베이스로 사용한다. upright 글리프를 기울여서 IBM italic을 흉내 내면 안 된다.

Italic variant의 스크립트별 정책은 다음과 같다.

| 글리프 | 정책 |
| --- | --- |
| 라틴, 숫자, ASCII 문장부호 | IBM Plex Mono true italic 유지 |
| 한글 및 한글 전각 문장부호 | 동일 웨이트의 upright 마루 부리 사용 |
| 가나, 한자 및 일본어 문장부호 | 동일 웨이트의 upright IBM Plex Sans JP 사용 |
| Powerline 및 Powerline Extra | upright 유지 |

Powerline 구분자를 기울이면 셀 경계에 틈이 생기므로 italic variant에서도 기울이지 않는다. 한글과 일본어의 synthetic italic은 초기 버전에서 생성하지 않는다.

Italic variant는 다음 메타데이터를 정확히 설정해야 한다.

- `head.macStyle` italic bit
- `OS/2.fsSelection` italic bit
- `OS/2.usWeightClass`
- `post.italicAngle`: IBM Plex Mono italic 값 보존
- `name` ID 1, 2, 3, 4, 6, 16, 17
- 올바른 RIBBI family grouping

## 9. Powerline 정책

### 9.1 포함 범위

`Gyeol Mono`의 모든 스타일에 Nerd Fonts의 다음 Powerline 범위를 포함한다.

| 세트 | 코드포인트 |
| --- | --- |
| Powerline Core | `U+E0A0–U+E0A2`, `U+E0B0–U+E0B3` |
| Powerline Extra | `U+E0A3`, `U+E0B4–U+E0C8`, `U+E0CA`, `U+E0CC–U+E0D7`, `U+2630` |

Powerline 글리프의 advance는 모두 600이다. 배경색 경계에서 가는 틈이 생기지 않도록 Nerd Fonts patcher가 정의하는 좌우 overlap을 보존한다.

위 범위는 2026-10-28 preview B 빌드의 기존 글리프와 겹치지 않는다. 당시 PUA 글리프는 IBM Plex Mono의 `U+F6D7`, `U+F6D8` 두 개뿐이었고 `U+2630`은 비어 있었다. `U+2630`(☰)은 text presentation 문자이므로 6.1의 emoji 제외 대상이 아니다.

Powerline 글리프는 터미널 셀 높이(`-275:1025`)에 맞춰 그려지므로 CSS `line-height`를 바꾸는 웹·문서 환경에서는 상하 경계가 맞지 않을 수 있다. 이 환경에서는 PUA 문자를 입력할 일이 드물어 기본 포함의 비용으로 수용한다.

### 9.2 패치 순서

Powerline patch는 한글 병합 전에 IBM Plex Mono 정적 TTF에 적용한다.

```text
IBM Plex Mono upright/italic
  -> Powerline subset patch
  -> 마루 부리 한글 및 IBM Plex Sans JP 병합
  -> Emoji_Presentation 코드포인트 제거(6.1)
  -> OpenType 메타데이터 및 메트릭 최종 정규화
  -> 검증 및 패키징
```

이 순서는 Nerd Fonts patcher가 600/1,200의 2폭 글꼴을 단일 폭으로 오인하거나 한글 advance를 변경할 가능성을 제거한다.

### 9.3 Font Patcher 옵션

개념적인 패치 명령은 다음과 같다. 실제 빌드에서는 Nerd Fonts의 tag 또는 commit을 고정하고 절대 경로를 사용한다.

```bash
fontforge -script font-patcher IBMPlexMono-Italic.ttf \
  --powerline \
  --powerlineextra \
  --single-width-glyphs \
  --careful \
  --metrics HHEA \
  --cell '0:600:-275:1025' \
  --makegroups -1 \
  --outputdir build/patched
```

다음 옵션은 사용하지 않는다.

| 옵션 | 사용하지 않는 이유 |
| --- | --- |
| `--mono` | 기존 글리프까지 1셀 폭으로 강제할 수 있어 1,200폭 한글을 손상시킴 |
| `--complete` | 전체 Nerd Fonts 아이콘은 기본 패밀리 범위 밖임(별도 패밀리는 15장 미결정 사항) |
| `--adjust-line-height` | 최종 수직 메트릭은 자체 빌더가 통제함 |
| `--variable-width-glyphs` | Powerline 심볼은 정확히 600폭이어야 함 |

`--single-width-glyphs`는 추가되는 Powerline 글리프를 1셀로 만들기 위해 사용하며, `--mono`의 대체 옵션이 아니다.

## 10. OpenType 처리

IBM Plex Mono를 베이스 폰트로 유지해 기존 `GSUB`, `GPOS` 및 라틴 대체 글리프를 보존한다.

CJK 병합 시 다음 테이블을 갱신해야 한다.

- `cmap`: 한글, 자모, 가나, 한자 및 전각 문자 매핑
- `glyf` 및 `loca`: 변환된 outline과 glyph location
- `hmtx`: 600/1,200 advance와 side bearing
- `hhea`: 최대 advance 및 수직 메트릭
- `head`: 전체 bounding box 및 style bit
- `maxp`: glyph 수와 관련 메타데이터
- `OS/2`: weight, style, Unicode range, code page range, fixed-pitch 관련 정보
- `post`: fixed-pitch 정보와 italic angle
- `name`: 새 family, subfamily, full name, PostScript name

NFD 한글 지원 범위는 실환경 확인 후 결정한다(현재 미구현). 기본 방향은 NFD 자모 클러스터를 OS 글꼴 fallback에 맡기는 것이며, 다음 확인 결과가 fallback으로 충분하지 않을 때만 현대 한글 자모 시퀀스를 완성형으로 shaping하는 `ccmp` lookup을 추가한다.

- NFD는 주로 macOS가 만든 파일 이름에서 유입되며, 한글 입력기로 작성한 문서와 코드는 NFC다.
- 마루 부리에는 결합 자모 글리프가 없어 `ccmp`의 입력 글리프를 먼저 마련해야 한다. 새 자모 디자인은 3장 비목표와 충돌하고, 다른 원본의 자모는 디자인 혼용을 만든다.
- 셀 단위로 렌더링하는 터미널은 `ccmp`를 적용하지 않을 수 있으므로 구현 효과도 환경별로 확인해야 한다.

확인은 NFC/NFD 한글 문자열과 NFD 파일 이름 샘플로 Windows Terminal, IntelliJ, VS Code와 macOS Terminal.app 또는 iTerm2에서 수행한다. 각 환경에서 NFD가 (1) 같은 2셀 음절로 조합되는지, (2) 다른 글꼴로 fallback되는지, (3) 자모가 분리되거나 셀 정렬이 깨지는지 기록한다. (3)이 주요 환경에서 발생할 때만 `ccmp`와 자모 입력 글리프 확보 방식을 v1 범위에서 정한다.

일본어 원본의 outline과 `cmap`은 복사하지만, monospace advance를 깨뜨릴 수 있는 `palt`, `pkna` 등의 proportional feature는 초기 버전에 포함하지 않는다. 세로쓰기용 `vert`와 `vrt2`, JP/KR glyph form 전환용 `locl`도 초기 범위에서 제외한다.

## 11. 빌드 파이프라인

빌드는 다음 단계를 명시적으로 분리한다.

1. manifest에 고정된 원본 다운로드 및 SHA-256 검증
2. IBM Plex Mono variant별 Powerline intermediate 생성
3. intermediate의 라틴 advance 600과 Powerline advance 600 검증
4. 마루 부리와 IBM Plex Sans JP 글리프 수집 및 outline decomposition
5. 스크립트별 UPM 정규화, 확대, 중앙 정렬 및 클리핑 제한
6. 한글·가나·한자 glyph, cmap 및 hmtx 병합
7. NFD 한글용 `ccmp` 추가(10장 확인 결과 필요할 때만)
8. `Emoji_Presentation=Yes` 코드포인트 매핑과 고아 글리프 제거
9. style bit, RIBBI 이름, 수직 메트릭 및 Unicode range 갱신
10. IBM Plex Sans JP 기반 TTF 저장
11. 생성한 TTF를 다시 열어 구조 검증
12. WOFF2 변환
13. 동일 specimen과 렌더러로 H0–H3 한글 optical correction 비교
14. 확정한 correction으로 최종 산출물 재생성
15. 라이선스와 manifest를 포함한 릴리스 패키지 생성

Unicode range(`OS/2.ulUnicodeRange`)는 emoji 제거 이후의 실제 `cmap`으로 계산한다.

제안하는 저장소 구조는 다음과 같다.

```text
docs/specs/
scripts/download_upstream.py
sources.toml
src/<package>/builder.py
src/<package>/metrics.py
src/<package>/naming.py
src/<package>/japanese.py
src/<package>/powerline.py
src/<package>/emoji.py
src/<package>/cli.py
tests/test_metrics.py
tests/test_merge.py
tests/test_shaping.py
tests/test_japanese.py
tests/test_powerline.py
tests/test_emoji.py
specimens/
licenses/
upstream/          # gitignored
build/             # gitignored
fonts/             # gitignored
```

## 12. 검증 기준

### 12.1 구조 검사

- 모든 핵심 ASCII 글리프의 advance가 600이다.
- 한글 완성형 11,172자가 모두 존재하고 advance가 1,200이다.
- 포함된 한글 자모의 advance가 정책과 일치한다.
- 선택한 일본어 원본에서 복사한 가나와 한자의 advance가 1,200이다.
- 일본어 원본의 실제 `cmap`과 결과 글꼴의 대상 일본어 `cmap` 사이에 의도하지 않은 누락이 없다.
- 모든 RIBBI face에 9.1의 Powerline 및 Powerline Extra 코드포인트가 모두 존재하고 advance가 600이다.
- 최종 `cmap`의 모든 서브테이블과 고정한 `emoji-data.txt`의 `Emoji_Presentation=Yes` 집합의 교집합이 비어 있다.
- emoji 제거로 고아가 된 글리프가 남아 있지 않다.
- `U+2717`이 IBM Plex Mono `U+274C` 윤곽을 가리키고 advance가 600이다.
- glyph order와 `glyf` 테이블에 누락 또는 중복이 없다.
- 모든 glyph bounding box가 최종 수직 셀 안에 있다.
- TTF를 fontTools로 저장한 뒤 다시 열 수 있다.
- `ots-sanitize`를 통과한다.
- `fontbakery check-universal`의 치명적 오류가 없다.

### 12.2 스타일 검사

- Upright variant에 italic bit가 설정되지 않는다.
- Italic variant에 italic bit와 올바른 italic angle이 설정된다.
- Regular/Italic은 CSS weight 400, Bold/Bold Italic은 CSS weight 700으로 노출된다.
- Bold outline이 IBM Plex Mono, 마루 부리와 IBM Plex Sans JP의 SemiBold 600 원본에서 생성됐다는 사실을 빌드 계획에 기록한다.
- family grouping이 macOS, Windows 및 브라우저에서 동일하게 동작한다.
- Italic 라틴 outline이 IBM Plex Mono의 true italic 원본과 일치한다.
- Italic variant의 한글, 일본어와 Powerline은 기울지 않는다.
- 터미널에서 ANSI SGR 1이 Bold face를, italic escape가 Italic face를 선택한다.

### 12.3 Shaping 검사

- NFD 한글이 자모 분리나 셀 정렬 깨짐 없이 2셀 음절로 표시된다. 다른 글꼴로의 fallback은 허용한다. `ccmp`를 구현하면 NFC와 NFD가 동일한 시각적 음절과 advance를 생성해야 한다.
- 한영일 혼용 문장에서 셀 정렬이 유지된다.
- IBM Plex Mono의 기존 라틴 shaping이 유지된다.
- 일본어 proportional feature가 활성화돼 가나 또는 한자 advance가 달라지지 않는다.
- Powerline PUA 코드포인트가 fallback 없이 현재 폰트에서 선택된다.
- `❌`, `✅`, `⚡`, `👍` 같은 emoji presentation 문자는 OS emoji 글꼴로 fallback되고, `♥`, `★`, `☰`, `✓`, `✗` 같은 text presentation 기호는 현재 폰트에서 선택된다.

### 12.4 시각 검사

다음 환경에서 upright와 italic을 모두 확인한다.

- macOS CoreText
- Chromium 기반 브라우저
- FreeType/HarfBuzz 기반 렌더러
- Ghostty
- Kitty 또는 WezTerm
- VS Code 또는 Zed

검수 크기는 최소 12, 14, 16, 24, 36, 48, 72px를 포함한다.

권장 specimen:

```text
한글과 English가 섞인 display serif mono
if (상태 === "완료") return "성공";
日本語の可読性を確認する
漢字・ひらがな・カタカナ ABC 0123456789
한글과日本語 그리고 English를 함께 표시한다
if (状態 === "完了") return "성공";
Il1| O0 0123456789 ()[]{} <> != == ->
가각간갇갈감갑값같꿇뷁힣
한글 / 한글
（）［］｛｝，．：；！？
      
     
❌ ✅ ⚡ 👍 | ♥ ★ ☰ ✓ ✗
```

Powerline 검수에서는 연속된 배경색 블록 사이에 1px 틈, 잘림 또는 italic 기울기 흔적이 없어야 한다.

### 12.5 일본어 후보 선택 기준 및 결론

Klee One을 디자인 후보, IBM Plex Sans JP를 가독성과 웨이트 일관성의 기준 후보로 평가했다. 두 후보를 한 최종 패밀리에 혼합하지 않는다.

평가 우선순위는 다음과 같다.

1. 12–16px 터미널 및 IDE 환경의 가독성
2. IBM Plex Mono 라틴과 마루 부리 한글 사이의 획 밀도 및 조형 조화
3. Regular과 Bold 사이의 시각적 강조 차이
4. IBM Plex Mono true italic과 upright 일본어의 혼용 자연스러움
5. 가나·한자 커버리지와 fallback 발생 여부
6. TTF/WOFF2 파일 크기와 빌드 시간

### 12.6 프로토타입 결론과 후속 모멘텀

2026-07-11에 CJK scale 1.00으로 Preview A와 B의 RIBBI 기본 패밀리를 빌드해 동일 specimen으로 비교했다. Klee One 기반 Preview A는 손글씨 성격이 IBM Plex Mono와 마루 부리 사이에서 독립적으로 두드러졌고, 터미널·IDE용 혼용 글꼴로는 조형 연결이 어색했다. IBM Plex Sans JP 기반 Preview B는 Regular/SemiBold의 획 구조가 더 안정적이고 일본어 outline 커버리지도 더 넓어 최종 일본어 원본으로 확정한다.

Preview B에서도 Regular face의 마루 부리가 IBM Plex Mono Regular 및 IBM Plex Sans JP Regular보다 가늘게 보이는 문제가 남았다. 다음 네 한글 조합을 동일한 라틴·일본어 1.00 scale과 specimen에서 비교한다.

| 실험 | 마루 부리 원본 | 한글 scale | 목적 |
| --- | --- | ---: | --- |
| H0 | Regular | 1.00 | 현재 기준선 |
| H1 | Regular | 1.05 | 최소 광학 확대 |
| H2 | Regular | 1.10 | 확대만으로 가능한 보정 상한 확인 |
| H3 | SemiBold | 0.96 | 굵은 outline을 축소해 크기와 획 밀도 동시 조정 |

마루 부리 Regular와 SemiBold의 공통 cmap 12,398자 중 outline topology가 직접 보간 가능한 글리프는 403자, 약 3.25%에 불과했다. 따라서 두 정적 폰트 사이의 일반적인 좌표 보간은 사용하지 않는다. 임의 outline embolden은 부리, counter와 교차 획을 손상시킬 수 있으므로 위 네 실험으로 충분한 결과를 얻지 못했을 때만 별도 스펙으로 검토한다.

후속 조정은 한글 scale과 일본어 scale을 별도 파라미터로 분리하고, 각 후보에 대해 12-unit 수평 guard, `-275:1025` 수직 셀, 600/1,200 advance 및 Regular/Bold 간 대비를 다시 검증해야 한다. 이 항목이 마루 부리 optical correction을 확정하기 위한 다음 작업 단위다.

### 12.7 리디바탕 시안 (2026-09-24, 철회됨)

동일한 라틴·일본어와 scale 1.00에서 마루 부리와 리디바탕을 비교한 뒤 리디바탕을 한글 원본으로 선택해 preview를 빌드했다. 리디바탕은 Regular 한 굵기만 제공하므로 이 시안에서는 RIBBI 전체가 Regular 한글을 사용했고 Bold 한글의 별도 굵기가 없었다. 리디바탕 원본 고정과 비교 시안은 2026-10-28에 저장소에서 제거했다(12.11).

### 12.8 마루 부리 재확정 (2026-10-01)

리디바탕 시안을 실제 폰트로 빌드해 사용해 본 뒤, 사용자가 한글 베이스로 마루 부리가 더 낫다고 판단해 마루 부리를 한글 원본으로 되돌렸다. Regular/Italic은 마루 부리 Regular, Bold/Bold Italic은 마루 부리 SemiBold를 사용하므로 Bold 한글의 강조 차이가 복원된다. 이때 추가한 단일 파일 다운로드와 CFF 입력 변환은 범용 기능으로 유지한다. 12.6의 Regular 굵기 보정(H0–H3)은 다시 미결 과제다. 현재 구현 범위는 non-Powerline preview TTF/WOFF2이며, PL 및 NFD shaping은 기존대로 미구현이다.

### 12.9 한글 배율 확정 (2026-10-05)

`comparisons/hangul/`에서 마루 부리 Regular를 baseline 기준 1.00/1.05/1.10/1.15와 중심(y=300) 기준 1.10/1.15로 같은 라틴·일본어 1.00 조건에서 비교했다. 사용자가 실제 문장으로 확인한 결과 중심 기준 1.10을 채택한다. 이어서 터미널과 IntelliJ(13px, 줄 간격 1.1)에서 사용해 본 뒤 영문이 한글보다 살짝 높아 보인다는 피드백에 따라 한글 +10–50 이동 시안을 비교하고 +30을 채택한다.

| 시안 | 음절 잉크 폭 중앙값 | 음절 간 빈틈 중앙값 | 중심 중앙값 | 셀 초과 | 판단 |
| --- | ---: | ---: | ---: | ---: | --- |
| 1.00 | 848 | 352 | 300 | 0 | 음절 사이가 벌어져 자간이 넓어 보인다 |
| 1.15 baseline | 975 | 225 | 345 | 0 | 꽉 차지만 한글이 영문보다 위로 뜬다 |
| 1.15 중심 | 975 | 225 | ≈300 | 8 | 셀 하단 −275를 넘는 글리프가 있다 |
| **1.10 중심** | 933 | 267 | 300 | 0 | 채택 |

- 1.15는 디지털 화면에서 자간이 빡빡해 인쇄물 같은 인상을 주므로 채택하지 않는다. 1.10 중심은 영문과의 상하 정렬과 음절 간 여백의 균형이 가장 좋다.
- +50은 한글 중심(약 350)이 영문 대문자 높이 중앙(349)까지 올라가 `:` 같은 문장 부호를 한글과 섞어 쓸 때 어색하므로 채택하지 않는다.
- 확정값(1.10, y=300, +30)으로 RIBBI 4종을 빌드했을 때 완성형 음절의 y 범위는 Regular −238–877, SemiBold −235–879, 중심 중앙값은 330/332이고 x 범위는 65–1131이다. 모두 12-unit 수평 guard와 `-275:1025` 수직 셀 안에 있으며 셀 하단 여유는 37 unit이다.
- `validate_built_font`는 모든 한글 글리프가 수평 guard와 수직 셀 안에 있는지 검사한다. 배율, anchor, 이동량을 바꿀 때 이 검사가 첫 방어선이다. 비교 스크립트는 셀 초과를 결과로 기록해야 하므로 `check_hangul_cell=False`로 이 검사만 끈다.
- 확대로 획 폭도 10% 커지지만 Regular 한글의 굵기 인상은 별도로 평가하지 않았다. 12.6의 H3(SemiBold 0.96)은 1.10 빌드를 실제 터미널에서 사용해 본 뒤 진행 여부를 결정한다. Bold는 Regular와 같은 1.10/y=300/+30을 사용한다.

### 12.10 Powerline 기본 포함 및 emoji 제외 (2026-10-28)

`PL` 패밀리를 폐지하고 Powerline Core/Extra를 `Gyeol Mono`에 기본으로 포함한다. 근거는 다음과 같다.

- 추가 글리프가 약 40개로, preview B Regular의 26,076 glyph에 비해 크기 영향이 없다.
- 9.1 범위가 기존 PUA 글리프(`U+F6D7`, `U+F6D8`)와 겹치지 않는다.
- Box Drawing과 Block Elements(`U+2500–U+259F`) 160자를 이미 제공하므로, 셀 경계에 맞닿는 터미널 UI 글리프를 기본 패밀리가 담당하는 편이 일관된다.
- 주 사용처가 터미널과 IDE이며 셀 정렬, 박스 글리프 보존 등 기존 결정도 터미널 기준이다.
- 패밀리가 하나로 줄어 사용자가 PL과 기본 패밀리 중 무엇을 설치할지 고민할 필요가 없고 빌드 행렬과 배포 archive가 절반이 된다.

2026-10-28에 배포 파일을 직접 확인한 결과, JetBrains Mono 2.304 Regular는 기본 패밀리에 Powerline Core 7자를 포함한다. Cascadia Code 2407.24는 기본 패밀리에는 Powerline이 없고 `PL`(38자)과 `NF`(41자) 변형에만 포함하며, Roboto Mono는 포함하지 않는다. Cascadia처럼 `PL` 이름을 분리하는 사례도 있지만, 이 프로젝트에는 기존 PUA 글리프와의 충돌이 없어 분리로 얻는 이점이 작다.

같은 날 6.1의 emoji 제외 정책을 추가했다. 컬러 emoji는 플랫폼마다 포맷(COLR/CPAL, sbix, CBDT)이 다르고, 수록하면 글꼴 크기가 크게 늘어나며, ZWJ 시퀀스 셀 폭은 글꼴이 통제할 수 없어 OS fallback이 낫다고 판단했다. 전체 Nerd Fonts 아이콘은 eza 등에서 필요한 Material Design 세트가 대부분을 차지해 부분 세트의 이점이 작으므로, 넣는다면 별도 패밀리로 전체 세트를 제공하는 방안을 15장에서 결정한다.

### 12.11 비교 원본 제거 (2026-10-28)

일본어 원본(IBM Plex Sans JP)과 한글 원본(마루 부리)이 확정되어 비목표가 된 비교 원본을 저장소에서 제거했다.

- `sources.toml`에서 `klee-one`, `ridi-batang` 항목을 지웠다.
- `JapaneseSource`에는 IBM Plex Sans JP만 남아 preview 빌드 행렬이 4개 target이 된다.
- `scripts/compare_hangul.py`의 리디바탕 참고 시안과 `comparisons/hangul/metrics.json`의 `Ridi100` 기록을 지웠다.
- 12.5–12.8의 비교 결과는 결정 근거로 남긴다. 당시 원본의 버전과 SHA-256은 Git 기록에서 확인할 수 있다.
- 단일 파일 다운로드(`archive_format = "file"`)와 CFF 윤곽 입력 변환은 범용 기능으로 유지한다.

## 13. 재현성과 배포

### 13.1 재현성

- 빌드 도구와 Python 의존성 버전을 lockfile로 고정한다.
- Nerd Fonts patcher와 glyph assets는 동일 tag 또는 commit에서 가져온다. CI에서는 FontForge와 patcher를 digest로 고정한 컨테이너 이미지에서 실행한다.
- `emoji-data.txt`는 Unicode 버전을 명시한 URL과 SHA-256으로 `sources.toml`에 고정한다. Unicode 버전을 올릴 때는 제거 대상 변화를 릴리스 노트에 기록한다.
- 빌드 시각에 따라 `head.modified`가 달라지지 않도록 재현 가능한 timestamp 정책을 사용한다.
- 같은 commit을 두 번 빌드하면 TTF와 WOFF2의 SHA-256이 같아야 한다. CI에서 이를 검사한다.
- 생성 폰트의 SHA-256을 릴리스 manifest(`SHA256SUMS`)에 기록한다.

### 13.2 배포 채널

1차 배포 채널은 GitHub Releases, npm, GitHub Pages 세 가지다.

| 채널 | 대상 | 내용 |
| --- | --- | --- |
| GitHub Releases | 터미널·IDE 사용자 설치 | `GyeolMono-<version>.zip`(RIBBI TTF, `licenses/`, README), `GyeolMono-<version>-web.zip`(npm과 같은 웹폰트), `SHA256SUMS` |
| npm | 웹·문서 사이트 | unicode-range로 분할한 WOFF2, `@font-face` CSS, `OFL.txt`, 네이버 라이선스. TTF는 포함하지 않는다 |
| GitHub Pages | 소개·specimen | 한영일 혼용 문장, 코드, Powerline 프롬프트 specimen, 설치 안내, Releases 다운로드 링크 |

- GitHub Releases가 기준 산출물이다. npm과 Pages의 웹폰트는 같은 태그 빌드에서 만든 파일을 사용한다.
- 스타일당 WOFF2가 약 2.2–2.4MB(2026-10-28 preview B)이므로 웹 배포물은 `fontTools.subset`으로 unicode-range 조각을 만들고, 브라우저가 쓰인 글자의 조각만 받게 한다. 원본 WOFF2 한 파일을 그대로 쓰는 CSS는 제공하지 않는다.
- Pages specimen은 npm 패키지와 같은 CSS와 조각을 로드해 웹 배포물의 실사용 검증을 겸한다.
- npm 패키지 이름에는 Reserved Font Name인 `Plex`를 쓰지 않는다.
- Homebrew tap과 Scoop bucket은 1차 범위에서 제외하고 v1 이후 별도로 검토한다. Homebrew 공식 `homebrew-cask`는 GitHub 인지도 기준(일반 fork 30·watcher 30·star 75 중 하나, 저장소 주인 직접 제출 시 90·90·225 중 하나)이 있으므로 자체 tap부터 시작하는 것이 현실적이다.

### 13.3 릴리스 절차

```text
PR / main push (ci workflow)
  -> fetch(원본 캐시) -> pytest -> RIBBI 빌드 -> 구조 검사(12.1)
  -> specimen PNG 렌더링 -> 폰트와 specimen을 workflow artifact로 업로드
사람이 artifact로 12.4 시각 검사 후 승인
  -> vX.Y.Z 태그 push (release workflow)
  -> 같은 commit 재빌드 및 재현성 검사 -> 웹폰트 분할
  -> GitHub Release 생성 -> npm publish -> Pages 배포
```

- 글리프 형상과 렌더링 판단은 사람이 한다. CI는 결정적으로 판정할 수 있는 구조 검사와 specimen 생성만 담당한다.
- `upstream/archives`는 `sources.toml` 해시를 키로 캐시한다. 외부 배포처가 일시 장애여도 고정 SHA-256 검증은 매번 수행한다.
- npm은 GitHub Actions OIDC trusted publishing으로 provenance와 함께 배포하고 장기 token을 저장소 secret에 두지 않는다.
- Pages는 태그 릴리스에서만 배포해 사이트가 항상 최신 릴리스와 일치하게 한다.
- 태그 버전을 `name` ID 5(`Version x.yyy`)와 `head.fontRevision`에 반영한다. 현재 빌더는 ID 3에 `0.1.0`을 고정하고 ID 5와 `fontRevision`을 IBM Plex Mono 값 그대로 두므로 v1 전에 바꿔야 한다.

### 13.4 v1 선행 작업

1. 이름이 `Gyeol Mono`인 release target 빌드 경로(현재 빌더는 preview target만 허용)
2. 태그 기반 버전 메타데이터
3. 9장 Powerline patch 단계 구현
4. `ots-sanitize`, `fontbakery check-universal` 검사 추가
5. 14장 `licenses/` 구성, archive와 `SHA256SUMS` 생성
6. 웹폰트 unicode-range 분할과 CSS 생성
7. ci, release workflow와 Pages specimen
8. 10장 NFD 한글 실환경 확인과 `ccmp` 필요 여부 결정
9. 12.6 Regular 한글 굵기 보정(H3) 비교와 채택 여부 결정
10. 6장 전각/반각 및 중복 기호 allowlist 확정

v1은 일정보다 완성도를 우선한다. 8–10번도 v1 범위에 포함하며, 글리프 품질 항목(8–10, 3)을 먼저 확정한 뒤 릴리스 인프라(1, 2, 4–7)를 마무리한다.

## 14. 라이선스와 저작권 고지

- IBM Plex는 SIL Open Font License 1.1을 사용하며 `Plex`는 Reserved Font Name이다.
- 최종 family name에는 `Plex`를 사용하지 않는다.
- 마루 부리는 수정과 재배포가 허용되지만 네이버와 네이버문화재단의 저작권 안내 및 라이선스 전문을 포함해야 한다.
- IBM Plex Sans JP는 SIL Open Font License 1.1이며, IBM Plex Mono와 동일하게 최종 family name에서 `Plex`를 사용하지 않는다.
- Powerline 자산을 기본 포함하므로 `Gyeol Mono` 배포물에 Nerd Fonts 및 해당 glyph source의 라이선스 고지를 추가한다.
- `emoji-data.txt`는 빌드 입력으로만 사용하고 글꼴이나 배포물에 포함하지 않는다.
- 결과 폰트에 IBM, 네이버 또는 원저작자가 최종 결과물을 보증한다는 표현을 사용하지 않는다.

예상 라이선스 구조:

```text
licenses/
  OFL-1.1.txt
  IBM-PLEX-NOTICE.txt
  NAVER-FONTS-LICENSE.txt
  NERD-FONTS-LICENSE.txt
```

공개 릴리스 전에 결합 결과물에 적용되는 라이선스 조합과 고지 문구를 최종 검토한다.

## 15. 미결정 사항

- Regular 한글 굵기 보정(H3 SemiBold 축소안) 추가 진행 여부. 배율과 위치는 1.10/y=300/+30으로 확정(12.9)
- Bold의 한글 확대율과 IBM Plex Sans JP의 웨이트별 optical scale
- 스크립트·웨이트별 수평/수직 optical correction 값
- 전각/반각 및 중복 기호 allowlist
- 전체 Nerd Fonts 아이콘을 담은 별도 `Gyeol Mono NF` 패밀리 제공 여부. 제공한다면 IBM Plex Mono에 먼저 패치하는 9.2 순서와 6.1 emoji 제외를 그대로 적용하고, 아이콘 시각 폭 정책과 PUA의 East Asian Width(Ambiguous) 안내를 함께 정한다
- 고정할 Nerd Fonts tag
- NFD 한글 `ccmp` 구현 여부와 자모 입력 글리프 확보 방식(10장 실환경 확인 후 결정)
- npm 패키지 이름(비scope 또는 scope)과 GitHub Pages 주소
- 웹폰트 unicode-range 분할 기준(조각 수, 한글 빈도순 여부)
- SemVer 태그를 `Version x.yyy`와 `head.fontRevision`으로 옮기는 규칙
- 향후 JP/KR `locl` glyph form 지원 여부
- 향후 synthetic CJK italic 실험 여부

## 16. 결정 요약

- 라틴은 600, 한글·가나·한자는 1,200의 duospace 구조를 사용한다.
- 한글은 마루 부리 upright outline을 확대·중앙 정렬해 사용한다.
- 동일 조건의 Preview A/B 비교 결과 최종 일본어 원본은 IBM Plex Sans JP로 확정한다.
- 리디바탕 시안을 철회하고 마루 부리를 한글 원본으로 재확정한다.
- Klee One과 리디바탕은 비교 결과만 기록으로 남기고 원본 고정, 빌드 경로와 비교 시안은 저장소에서 제거한다.
- 마루 부리 Regular의 굵기 보정은 H0–H3 후속 비교로 결정하며 정적 Regular/SemiBold outline의 직접 보간은 사용하지 않는다.
- 한글 기본 배율은 1.10, 수직 anchor는 y=300, 수직 이동은 +30이며 Regular와 Bold에 같이 적용한다. 일본어 배율은 1.00이다.
- 최종 family name은 `Gyeol Mono` 하나이며 `PL` 패밀리는 만들지 않는다.
- 한국어 표시 이름은 `결 모노`를 사용하되 OpenType family name과 PostScript name은 ASCII로 유지한다.
- IBM Plex Mono true italic을 보존한다.
- Italic variant에서도 모든 CJK 글리프와 Powerline은 upright로 유지한다.
- 사용자 노출 웨이트는 Regular와 Bold 두 개로 제한하고 RIBBI 네 face를 제공한다.
- Bold face는 세 스크립트의 SemiBold 600 outline을 사용하되 Bold 700 메타데이터로 노출한다. 한글 synthetic bold는 적용하지 않는다.
- 기본 패밀리에 Powerline Core와 Extra를 포함하며 전체 Nerd Fonts 세트는 포함하지 않는다.
- Powerline은 IBM Plex Mono에 먼저 패치한 뒤 한글을 병합한다.
- `--mono` 대신 `--single-width-glyphs`를 사용한다.
- `Emoji_Presentation=Yes` 코드포인트는 원본과 무관하게 최종 글꼴에서 제외하고 OS emoji 글꼴 fallback에 맡긴다. text presentation 기호는 유지한다.
- IBM Plex Mono의 `U+274C` 흑백 X 윤곽은 `U+2717`(✗)로 옮겨 ✓/✗ 짝을 유지한다.
- 초기 출력은 TTF와 WOFF2로 제한한다.
- NFD 한글은 OS 글꼴 fallback을 기본으로 하고, 실환경에서 자모 분리나 셀 깨짐이 확인될 때만 `ccmp`를 추가한다.
- 1차 배포 채널은 GitHub Releases, npm(분할 WOFF2와 CSS), GitHub Pages이며 태그 workflow 하나에서 함께 배포한다. Homebrew tap과 Scoop bucket은 v1 이후 검토한다.
