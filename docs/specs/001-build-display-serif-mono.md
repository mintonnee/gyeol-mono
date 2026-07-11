# 001. Gyeol Mono 빌드

- 상태: Draft
- 작성일: 2026-07-11
- 최종 수정일: 2026-07-11
- 대상 구현: 정적 TTF 및 WOFF2 패밀리

## 1. 개요

이 문서는 IBM Plex Mono의 라틴 글리프, 마루 부리의 한글 글리프와 일본어 후보 글꼴의 가나·한자 글리프를 결합한 `Gyeol Mono`를 만드는 데 필요한 설계와 빌드 규칙을 정의한다.

결과 글꼴은 라틴 문자에 600 units, 한글·가나·한자에 1,200 units의 advance를 사용하는 2폭 구조다. 따라서 엄밀히는 모든 글리프가 동일한 폭을 갖는 monospace가 아니라, 라틴 1셀과 CJK 2셀로 구성된 duospace 글꼴이다. 사용자에게는 일반적인 CJK 코딩 글꼴과 동일하게 모노스페이스 패밀리로 제공한다.

기본 패밀리와 Powerline 글리프를 포함한 터미널용 `PL` 패밀리를 별도로 생성한다. 전체 Nerd Fonts 아이콘 세트는 포함하지 않는다.

## 2. 목표

- IBM Plex Mono의 라틴 디자인, 숫자, 문장부호와 true italic을 보존한다.
- 마루 부리의 한글 조형을 2셀 환경에 맞춰 확대하고 광학적으로 중앙 정렬한다.
- 일본어 가나와 한자에 정돈된 손글씨 또는 친근한 고딕 인상을 제공한다.
- Klee One과 IBM Plex Sans JP를 동일 조건에서 비교해 최종 일본어 원본을 결정한다.
- 본문 크기와 디스플레이 크기에서 모두 읽기 좋은 한영일 혼용 결과를 만든다.
- 편집기와 터미널에서 ASCII 1셀, CJK 2셀 정렬을 보장한다.
- Powerline 및 Powerline Extra 구분자를 라틴 1셀 크기로 제공한다.
- 원본 다운로드부터 산출물 생성까지 재현 가능한 빌드 파이프라인을 제공한다.
- 구조 검사, shaping 검사, 렌더링 검수를 자동화할 수 있는 기반을 마련한다.

## 3. 비목표

초기 버전에서는 다음 항목을 지원하지 않는다.

- 전체 Nerd Fonts 아이콘 세트
- Variable Font
- 한글 및 일본어 글리프의 synthetic italic 또는 oblique
- ExtraLight, Light, Medium, SemiBold, ExtraBold 등 별도 사용자 노출 웨이트
- Klee One과 IBM Plex Sans JP를 한 최종 패밀리 안에서 혼합해 사용하는 구성
- CJK 언어 태그에 따른 JP/KR `locl` 전환
- CFF outline 기반 OTF
- 원본 폰트의 소스 편집 또는 새로운 글리프 디자인

초기 출력 포맷은 TTF와 WOFF2로 제한한다. OTF가 필요하면 별도 스펙에서 CFF 변환 및 힌팅 정책을 정의한다.

## 4. 원본과 버전 고정

빌드는 다음 원본을 사용한다.

| 역할 | 원본 | 형식 |
| --- | --- | --- |
| 라틴 및 기본 OpenType 테이블 | IBM Plex Mono | 정적 TTF |
| 한글 및 한글 전각 문장부호 | 마루 부리 | 정적 TTF |
| 일본어 후보 A | Klee One | 정적 TTF |
| 일본어 후보 B | IBM Plex Sans JP | 정적 TTF |
| Powerline 글리프 | Nerd Fonts Font Patcher에 포함된 Powerline/Powerline Extra | Font Patcher 입력 자산 |

다운로더는 원본별 버전, URL 및 SHA-256을 명시적으로 고정해야 한다. `latest` URL을 빌드 입력으로 직접 사용하면 안 된다. 원본 파일과 생성 파일은 Git에서 제외하고, 버전 및 체크섬 manifest만 추적한다.

참고 자료:

- [IBM Plex](https://github.com/IBM/plex)
- [IBM Plex 라이선스](https://github.com/IBM/plex/blob/master/LICENSE.txt)
- [네이버 글꼴 모음 및 마루 부리 사용 안내](https://hangeul.naver.com/font)
- [Klee One 메타데이터](https://github.com/google/fonts/blob/main/ofl/kleeone/METADATA.pb)
- [Klee One 설명](https://github.com/google/fonts/blob/main/ofl/kleeone/DESCRIPTION.en_us.html)
- [IBM Plex Sans JP 메타데이터](https://github.com/google/fonts/blob/main/ofl/ibmplexsansjp/METADATA.pb)
- [Nerd Fonts Font Patcher](https://github.com/ryanoasis/nerd-fonts#font-patcher)
- [Nerd Fonts Glyph Sets and Code Points](https://github.com/ryanoasis/nerd-fonts/wiki/Glyph-Sets-and-Code-Points)

## 5. 패밀리와 스타일

최종 family name은 `Gyeol Mono`로 확정한다. 이름의 `Gyeol`은 글자의 결, 획의 질감과 서로 다른 스크립트가 한 문장 안에서 만드는 흐름을 의미한다. IBM Plex의 Reserved Font Name인 `Plex`를 최종 사용자 노출 이름에 사용하지 않는다.

두 개의 배포 패밀리를 생성한다.

| 패밀리 | 용도 | Powerline 포함 여부 |
| --- | --- | --- |
| `Gyeol Mono` | 일반 디스플레이, 웹, 편집기 | 미포함 |
| `Gyeol Mono PL` | 터미널 및 Powerline 프롬프트 | 포함 |

`PL` 패밀리는 Powerline subset만 포함하므로 이름에 `Nerd Font`를 사용하지 않는다.

### 5.1 OpenType 및 파일 이름

OpenType family name은 플랫폼 호환성을 위해 ASCII `Gyeol Mono`를 사용한다. `결 모노`는 README, 웹사이트와 specimen에서 사용하는 한국어 표시 이름이며 OpenType의 기본 family name으로 사용하지 않는다.

기본 패밀리 이름은 다음과 같다.

| 스타일 | Full name | PostScript name | 파일 이름 |
| --- | --- | --- | --- |
| Regular | `Gyeol Mono Regular` | `GyeolMono-Regular` | `GyeolMono-Regular.ttf` |
| Italic | `Gyeol Mono Italic` | `GyeolMono-Italic` | `GyeolMono-Italic.ttf` |
| Bold | `Gyeol Mono Bold` | `GyeolMono-Bold` | `GyeolMono-Bold.ttf` |
| Bold Italic | `Gyeol Mono Bold Italic` | `GyeolMono-BoldItalic` | `GyeolMono-BoldItalic.ttf` |

Powerline 패밀리 이름은 다음과 같다.

| 스타일 | Full name | PostScript name | 파일 이름 |
| --- | --- | --- | --- |
| Regular | `Gyeol Mono PL Regular` | `GyeolMonoPL-Regular` | `GyeolMonoPL-Regular.ttf` |
| Italic | `Gyeol Mono PL Italic` | `GyeolMonoPL-Italic` | `GyeolMonoPL-Italic.ttf` |
| Bold | `Gyeol Mono PL Bold` | `GyeolMonoPL-Bold` | `GyeolMonoPL-Bold.ttf` |
| Bold Italic | `Gyeol Mono PL Bold Italic` | `GyeolMonoPL-BoldItalic` | `GyeolMonoPL-BoldItalic.ttf` |

`name` ID 1과 16은 각각 `Gyeol Mono` 또는 `Gyeol Mono PL`로 통일한다. ID 2와 17은 `Regular`, `Italic`, `Bold`, `Bold Italic` 중 해당 값을 사용한다. ID 4와 6은 위 표의 Full/PostScript name을 사용한다.

후보 비교 빌드는 동시에 설치해 비교할 수 있도록 사용자 노출 family를 `Gyeol Mono Preview A`와 `Gyeol Mono Preview B`로 분리한다. manifest에서 Preview A를 Klee One, Preview B를 IBM Plex Sans JP에 대응시키며 최종 릴리스에는 Preview 이름을 포함하지 않는다.

### 5.2 웨이트 및 스타일 매트릭스

초기 릴리스는 터미널과 IDE의 RIBBI 선택에 맞춰 다음 네 face를 생성한다.

| 출력 스타일 | 출력 CSS weight | IBM Plex Mono 원본 | 마루 부리 원본 | 일본어 후보 원본 |
| --- | ---: | --- | --- | --- |
| Regular | 400 | Regular | Regular upright | Regular upright |
| Italic | 400 | true Italic | Regular upright | Regular upright |
| Bold | 700 | SemiBold | SemiBold upright | SemiBold upright |
| Bold Italic | 700 | SemiBold Italic | SemiBold upright | SemiBold upright |

두꺼운 face는 세 스크립트의 획 밀도를 일치시키기 위해 모두 SemiBold 600 원본을 사용한다. 다만 최종 사용자 노출 이름과 `OS/2.usWeightClass`는 Bold 700으로 설정한다. 이는 일부 터미널이 `SemiBold` face를 ANSI SGR 1 또는 Bold face로 선택하지 않는 문제를 피하기 위한 의도적인 매핑이다.

후보 비교 단계에서는 Klee One과 IBM Plex Sans JP에 대해 각각 기본 패밀리 4개와 `PL` 패밀리 4개, 총 8개 정적 TTF를 생성한다. 두 후보를 합친 비교 산출물은 총 16개다. 최종 선택 후에는 선택한 일본어 원본의 8개 파일만 배포한다.

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

`₩`, 따옴표, 대시, 화살표, 괄호, 전각 ASCII처럼 둘 이상의 원본에 존재하는 문자는 실제 터미널 셀 동작과 시각적 조화를 확인한 후 allowlist로 관리한다.

마루 부리와 일본어 후보에 포함된 라틴 글리프는 복사하지 않는다. 한자는 임의의 전체 Unicode 범위를 가정하지 않고 선택한 일본어 원본의 `cmap`에 실제로 존재하는 글리프만 복사한다.

초기 버전의 한자 기본 형태는 일본어 원본이 제공하는 JP glyph form이다. 터미널과 IDE가 일반적으로 `ko` 또는 `ja` language tag를 제공하지 않는 점을 고려해 JP/KR `locl` 전환은 구현하지 않는다.

## 7. 메트릭

Regular TTF에서 확인한 주요 입력 메트릭은 다음과 같다.

| 항목 | IBM Plex Mono Regular | 마루 부리 Regular |
| --- | ---: | ---: |
| unitsPerEm | 1,000 | 1,000 |
| 대표 라틴 `A` advance | 600 | 675 |
| 한글 `가` advance | 없음 | 970 |
| hhea ascent | 1,025 | 800 |
| hhea descent | -275 | -200 |
| Typo ascender | 780 | 800 |
| Typo descender | -220 | -200 |

### 7.1 수평 메트릭

- 라틴 셀 폭은 IBM Plex Mono의 600 units를 그대로 유지한다.
- 한글과 일본어 셀 폭은 라틴 셀의 정확히 두 배인 1,200 units로 설정한다.
- CJK outline은 1,200 전체로 늘리지 않고, 셀 안에서 확대 후 광학적으로 중앙 정렬한다.
- CJK 글리프의 좌우 side bearing에는 최소 guard를 둔다.
- 기본 guard 후보는 라틴 셀 폭의 2%, 즉 12 units이며, 렌더링 결과에 따라 조정한다.
- `hhea.advanceWidthMax`는 최종 한글 폭을 반영해 1,200 이상이어야 한다.
- 600/1,200의 규칙적인 2폭 글꼴이므로 `post.isFixedPitch`와 PANOSE proportion은 monospaced로 설정한다.

### 7.2 CJK 확대율

확대율은 아직 최종 결정하지 않았다. 한글과 일본어 원본에 서로 다른 optical scale을 허용한다. Regular에서 다음 후보를 먼저 생성해 비교한다.

```text
1.00
1.05
1.10
1.15
```

확대율은 스크립트와 웨이트별로 다를 수 있다. 한 개의 상수를 모든 CJK 글리프에 강제하지 않는다. 각 글리프는 요청 배율을 적용하되 셀의 수평 guard 또는 최종 수직 셀을 벗어나면 개별적으로 배율을 제한한다.

Klee One과 IBM Plex Sans JP 비교 시에는 원본 자체의 차이만 평가할 수 있도록 동일한 후보 scale과 수직 셀을 먼저 적용한다. 이후 최종 후보가 결정되면 일본어 optical scale을 별도로 미세 조정한다.

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
| 가나, 한자 및 일본어 문장부호 | 동일 웨이트의 upright 일본어 후보 사용 |
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

Nerd Fonts의 다음 Powerline 범위를 포함한다.

| 세트 | 코드포인트 |
| --- | --- |
| Powerline Core | `U+E0A0–U+E0A2`, `U+E0B0–U+E0B3` |
| Powerline Extra | `U+E0A3`, `U+E0B4–U+E0C8`, `U+E0CA`, `U+E0CC–U+E0D7`, `U+2630` |

Powerline 글리프의 advance는 모두 600이다. 배경색 경계에서 가는 틈이 생기지 않도록 Nerd Fonts patcher가 정의하는 좌우 overlap을 보존한다.

### 9.2 패치 순서

Powerline patch는 한글 병합 전에 IBM Plex Mono 정적 TTF에 적용한다.

```text
IBM Plex Mono upright/italic
  -> Powerline subset patch
  -> 마루 부리 한글 병합
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
| `--complete` | 전체 Nerd Fonts 아이콘은 프로젝트 범위 밖임 |
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

NFD 입력을 지원하기 위해 현대 한글 자모 시퀀스를 완성형 한글로 shaping하는 `ccmp` lookup을 제공한다. NFC `한글`과 NFD `한글`은 동일한 2셀 결과를 만들어야 한다.

일본어 원본의 outline과 `cmap`은 복사하지만, monospace advance를 깨뜨릴 수 있는 `palt`, `pkna` 등의 proportional feature는 초기 버전에 포함하지 않는다. 세로쓰기용 `vert`와 `vrt2`, JP/KR glyph form 전환용 `locl`도 초기 범위에서 제외한다.

## 11. 빌드 파이프라인

빌드는 다음 단계를 명시적으로 분리한다.

1. manifest에 고정된 원본 다운로드 및 SHA-256 검증
2. IBM Plex Mono 원본을 기본 패밀리 branch로 유지
3. IBM Plex Mono variant별 Powerline intermediate를 `PL` branch에 생성
4. 두 branch 모두에서 라틴 advance 600 검증
5. 마루 부리와 일본어 후보 글리프 수집 및 outline decomposition
6. 스크립트별 UPM 정규화, 확대, 중앙 정렬 및 클리핑 제한
7. 각 branch에 한글·가나·한자 glyph, cmap 및 hmtx 병합
8. NFD 한글용 `ccmp` 추가
9. style bit, RIBBI 이름, 수직 메트릭 및 Unicode range 갱신
10. Klee One 후보와 IBM Plex Sans JP 후보 TTF 저장
11. 후보별 TTF를 다시 열어 구조 검증
12. WOFF2 변환
13. 동일 specimen과 렌더러로 후보 비교
14. 최종 일본어 원본 선택 후 선택되지 않은 후보를 릴리스 산출물에서 제외
15. 라이선스와 manifest를 포함한 릴리스 패키지 생성

제안하는 저장소 구조는 다음과 같다.

```text
docs/specs/
scripts/download_upstream.py
src/<package>/builder.py
src/<package>/metrics.py
src/<package>/naming.py
src/<package>/japanese.py
src/<package>/powerline.py
src/<package>/cli.py
tests/test_metrics.py
tests/test_merge.py
tests/test_shaping.py
tests/test_japanese.py
tests/test_powerline.py
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
- Powerline 및 Powerline Extra 글리프의 advance가 600이다.
- glyph order와 `glyf` 테이블에 누락 또는 중복이 없다.
- 모든 glyph bounding box가 최종 수직 셀 안에 있다.
- TTF를 fontTools로 저장한 뒤 다시 열 수 있다.
- `ots-sanitize`를 통과한다.
- `fontbakery check-universal`의 치명적 오류가 없다.

### 12.2 스타일 검사

- Upright variant에 italic bit가 설정되지 않는다.
- Italic variant에 italic bit와 올바른 italic angle이 설정된다.
- Regular/Italic은 CSS weight 400, Bold/Bold Italic은 CSS weight 700으로 노출된다.
- Bold outline이 IBM Plex Mono, 마루 부리와 일본어 후보의 SemiBold 600 원본에서 생성됐다는 사실을 manifest에 기록한다.
- family grouping이 macOS, Windows 및 브라우저에서 동일하게 동작한다.
- Italic 라틴 outline이 IBM Plex Mono의 true italic 원본과 일치한다.
- Italic variant의 한글, 일본어와 Powerline은 기울지 않는다.
- 터미널에서 ANSI SGR 1이 Bold face를, italic escape가 Italic face를 선택한다.

### 12.3 Shaping 검사

- NFC와 NFD 한글이 동일한 시각적 음절과 advance를 생성한다.
- 한영일 혼용 문장에서 셀 정렬이 유지된다.
- IBM Plex Mono의 기존 라틴 shaping이 유지된다.
- 일본어 proportional feature가 활성화돼 가나 또는 한자 advance가 달라지지 않는다.
- Powerline PUA 코드포인트가 fallback 없이 현재 폰트에서 선택된다.

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
```

Powerline 검수에서는 연속된 배경색 블록 사이에 1px 틈, 잘림 또는 italic 기울기 흔적이 없어야 한다.

### 12.5 일본어 후보 선택 기준

Klee One을 디자인 후보, IBM Plex Sans JP를 가독성과 웨이트 일관성의 기준 후보로 평가한다. 두 후보를 한 최종 패밀리에 혼합하지 않는다.

평가 우선순위는 다음과 같다.

1. 12–16px 터미널 및 IDE 환경의 가독성
2. IBM Plex Mono 라틴과 마루 부리 한글 사이의 획 밀도 및 조형 조화
3. Regular과 Bold 사이의 시각적 강조 차이
4. IBM Plex Mono true italic과 upright 일본어의 혼용 자연스러움
5. 가나·한자 커버리지와 fallback 발생 여부
6. TTF/WOFF2 파일 크기와 빌드 시간

## 13. 재현성과 배포

- 빌드 도구와 Python 의존성 버전을 lockfile로 고정한다.
- Nerd Fonts patcher와 glyph assets는 동일 tag 또는 commit에서 가져온다.
- 빌드 시각에 따라 `head.modified`가 달라지지 않도록 재현 가능한 timestamp 정책을 사용한다.
- 생성 폰트의 SHA-256을 릴리스 manifest에 기록한다.
- 기본 패밀리는 `GyeolMono`, Powerline 패밀리는 `GyeolMonoPL` 디렉터리 및 별도 archive로 제공한다.
- 웹 배포 시 WOFF2와 명시적인 `@font-face` CSS를 제공한다.

## 14. 라이선스와 저작권 고지

- IBM Plex는 SIL Open Font License 1.1을 사용하며 `Plex`는 Reserved Font Name이다.
- 최종 family name에는 `Plex`를 사용하지 않는다.
- 마루 부리는 수정과 재배포가 허용되지만 네이버와 네이버문화재단의 저작권 안내 및 라이선스 전문을 포함해야 한다.
- Klee One은 SIL Open Font License 1.1이며, 후보 비교 및 Klee 기반 결과물에는 원본 저작권 고지를 포함한다.
- IBM Plex Sans JP는 SIL Open Font License 1.1이며, IBM Plex Mono와 동일하게 최종 family name에서 `Plex`를 사용하지 않는다.
- Powerline 자산을 포함하는 `PL` 패밀리에는 Nerd Fonts 및 해당 glyph source의 라이선스 고지를 추가한다.
- 결과 폰트에 IBM, 네이버 또는 원저작자가 최종 결과물을 보증한다는 표현을 사용하지 않는다.

예상 라이선스 구조:

```text
licenses/
  OFL-1.1.txt
  IBM-PLEX-NOTICE.txt
  NAVER-FONTS-LICENSE.txt
  KLEE-ONE-OFL.txt
  NERD-FONTS-LICENSE.txt
```

후보 비교 archive에는 두 일본어 후보의 고지를 모두 포함한다. 공개 릴리스 archive에는 최종 선택한 일본어 원본의 고지만 포함한다. 공개 릴리스 전에 결합 결과물에 적용되는 라이선스 조합과 고지 문구를 최종 검토한다.

## 15. 미결정 사항

- 최종 일본어 원본: Klee One 또는 IBM Plex Sans JP
- Regular/Bold의 한글 및 일본어 확대율
- 스크립트·웨이트별 수평/수직 optical correction 값
- 전각/반각 및 중복 기호 allowlist
- 기본 패밀리와 `PL` 패밀리를 모두 배포할지 여부
- Klee One 기반 Bold가 터미널 환경에서 충분한 시각적 강조를 제공하는지 여부
- 향후 JP/KR `locl` glyph form 지원 여부
- 향후 synthetic CJK italic 실험 여부

## 16. 결정 요약

- 라틴은 600, 한글·가나·한자는 1,200의 duospace 구조를 사용한다.
- 한글은 마루 부리 upright outline을 확대·중앙 정렬해 사용한다.
- 일본어 원본 후보는 Klee One과 IBM Plex Sans JP로 제한하고 동일 조건의 별도 빌드로 비교한다.
- 두 일본어 후보를 한 최종 패밀리 안에서 혼합하지 않는다.
- 최종 family name은 `Gyeol Mono`, Powerline family name은 `Gyeol Mono PL`을 사용한다.
- 한국어 표시 이름은 `결 모노`를 사용하되 OpenType family name과 PostScript name은 ASCII로 유지한다.
- IBM Plex Mono true italic을 보존한다.
- Italic variant에서도 모든 CJK 글리프와 Powerline은 upright로 유지한다.
- 사용자 노출 웨이트는 Regular와 Bold 두 개로 제한하고 RIBBI 네 face를 제공한다.
- Bold face는 세 스크립트의 SemiBold 600 outline을 사용하되 Bold 700 메타데이터로 노출한다.
- Powerline Core와 Extra만 포함하며 전체 Nerd Fonts 세트는 포함하지 않는다.
- Powerline은 IBM Plex Mono에 먼저 패치한 뒤 한글을 병합한다.
- `--mono` 대신 `--single-width-glyphs`를 사용한다.
- `Gyeol Mono`와 `Gyeol Mono PL` 패밀리를 분리한다.
- 초기 출력은 TTF와 WOFF2로 제한한다.
