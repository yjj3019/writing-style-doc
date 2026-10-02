# 추가 참고 저장소와 반영 범위

확인일: 2026-10-02. 아래 커밋의 파일과 라이선스를 직접 읽었다. 개념을 검토한 뒤 기존 한국어 지침에 맞춰 새 문장과 가상 예시를 작성했다. 원문·코드·규칙 파일의 복사, 문서 번역, 외부 도구 설치는 하지 않았다. 초기 참고 자료의 출처도 아래에 통합했다.

| 저장소·고정 커밋 | 확인 파일 | 라이선스 | 채택한 개념 |
|---|---|---|---|
| [blader/humanizer](https://github.com/blader/humanizer/tree/225a6f39ac85f76ee48dbad772ea4abe4ed6c9d8) | `SKILL.md`, `LICENSE` | MIT | 원문과 수정문의 정보 대조, 코드·링크 보호, 인용·의미 있는 반복의 예외 |
| [evildmp/diataxis-documentation-framework](https://github.com/evildmp/diataxis-documentation-framework/tree/957c09ca40b4a1edc23874f713e01937d50d54d5) | `source/index.rst`, `source/how-to-guides.rst`, `source/reference.rst`, `LICENSE.rst` | CC BY-SA 4.0 | 독자의 학습·작업·조회·이해 목적에 따른 구성 선택 |
| [vale-cli/vale](https://github.com/vale-cli/vale/tree/c74f4da2263d94d49b6aadf4b07a1ccf9df3980b) | `README.md`, `internal/core/markup.go`, `LICENSE` | MIT | 문서 형식을 이해하고 문장과 코드·URL을 구분하는 검사 범위 |
| [btford/write-good](https://github.com/btford/write-good/tree/6940b034c6f5a7e101c01a24d651a778fc3fe435) | `README.md`, `LICENSE` | MIT | 검사 결과를 수정 제안으로 취급하고 문맥에 따라 예외를 인정 |

## 한국어 스킬에서 적용한 방식

- 문장을 짧게 만드는 편집에서도 이름·수치·부정·조건·예외·출처가 빠지지 않는지 원문과 대조한다. 요약에는 핵심 판단을 바꾸는 조건을 남긴다.
- 기술 문서의 목적을 먼저 정한다. 모든 글을 학습·작업·조회·이해 네 절로 재구성하거나 블로그를 기술 참조 문서처럼 바꾸지 않는다.
- 코드·명령 옵션·경로·설정·링크 대상은 문장 교정의 대상에서 제외한다. 명시적인 기술 수정과 익명화는 허용한다.
- 문체 점검에서 발견한 표현은 수정 후보로 취급한다. 인용·고유명사·필요한 불확실성·의미 있는 반복을 일괄 삭제하지 않는다.

## 채택하지 않은 지침

- Humanizer에서 허용하는 반응 추가를 개인 경험·감정 창작으로 확대하지 않는다. 이 스킬은 제공된 의견과 감정만 쓴다.
- Humanizer의 초안·잔여 패턴·최종본 동시 출력 방식을 기본 출력으로 채택하지 않는다. 요청한 완성 본문을 먼저 제공한다.
- 특정 영어 단어, 수동태, 줄표를 AI 작성의 증거로 삼지 않는다. 영어용 금지어·문법 검사와 가독성 점수를 한국어에 그대로 적용하지 않는다.
- 외부 프레임워크의 문장·예시를 번역해 배포하거나 같은 표준을 준수한다고 주장하지 않는다.
- 문체 표지만으로 작성 주체를 판정하거나 AI 탐지 회피 성능을 약속하지 않는다.

향후 원문·코드·상당한 표현을 직접 재사용할 경우 해당 출처의 라이선스에 맞춰 저작권 표시, 허락 고지, 변경 표시와 필요한 배포 조건을 확인한다. 이 문서는 저장소 전체에 새로운 라이선스를 부여하지 않는다.

## 초기 참고 자료

| 자료 | 확인 파일과 Git blob SHA | 반영한 원칙 |
|---|---|---|
| [Google Markdown style guide](https://github.com/google/styleguide/blob/gh-pages/docguide/style.md) | `docguide/style.md`, `50666151ee93587b70929c2f2361e1766e9b4ce1` | 처음 읽는 독자를 위한 배경, 설명적인 링크 이름, 언어를 표시한 코드 블록 |
| [Google Documentation Best Practices](https://github.com/google/styleguide/blob/gh-pages/docguide/best_practices.md) | `docguide/best_practices.md`, `946c2555ec54133728d3f1eba30fe731c7b32017` | 설정 변경과 관련 예시·문서를 함께 갱신, 불필요한 원문 중복 축소 |
| [Developer Style Guide](https://github.com/lornajane/developer-style-guide/blob/main/README.md) | `README.md`, `dbdd3163c5cd174190ad29e4277478fbfd730534` | 독자와 목표를 기준으로 설명 깊이 조절, 예시·그림 설명과 대체 텍스트 |
| [Vale write-good](https://github.com/vale-cli/write-good) | `write-good/Passive.yml`, `f472cb9049f37c0717389de5c4342a1d1b829b2b`; `write-good/Weasel.yml`, `d1d90a7bcc645f625c824a9d87e1c5d361bc84e2` | 모호한 강조·행동 주체를 편집 검토 대상으로 삼음. 자동 삭제나 한국어 문법 판정으로 사용하지 않음 |

blob SHA는 확인한 파일 내용의 식별자이며 커밋 SHA가 아니다. 링크의 브랜치는 이후 변경될 수 있다.


초기 자료는 원칙을 재서술했으며 원문·규칙 파일을 복사하지 않았다. 영어 수동태·대소문자·80자 줄바꿈을 한국어 기준으로 적용하지 않는다.

## 링크 검사 구현 근거

제목 앵커·중복 제목·사용자 지정 앵커 규칙은 [GitHub 공식 Markdown 안내](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#section-links)를 2026-10-02에 확인했습니다. 코드 구현은 별도로 작성했으며 일반 표기 범위만 검사합니다. 전체 Markdown 렌더러를 대체하지 않습니다.
