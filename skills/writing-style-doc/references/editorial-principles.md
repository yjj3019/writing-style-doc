# 외부 지침 반영 기준

공개 Git 저장소를 2026-10-02에 읽고 이번 한국어 지침에 맞게 원칙을 재서술했다. 외부 문장·규칙 파일을 복사하거나 영어 문법 검사를 설치한 자료가 아니다. 개인 문체는 사용자가 제공한 글을 기준으로 판단한다.

## 확인한 자료와 적용 범위

| 자료 | 확인 파일과 Git blob SHA | 반영한 원칙 |
|---|---|---|
| [Google Markdown style guide](https://github.com/google/styleguide/blob/gh-pages/docguide/style.md) | `docguide/style.md`, `50666151ee93587b70929c2f2361e1766e9b4ce1` | 처음 읽는 독자를 위한 배경, 설명적인 링크 이름, 언어를 표시한 코드 블록 |
| [Google Documentation Best Practices](https://github.com/google/styleguide/blob/gh-pages/docguide/best_practices.md) | `docguide/best_practices.md`, `946c2555ec54133728d3f1eba30fe731c7b32017` | 설정 변경과 관련 예시·문서를 함께 갱신, 불필요한 원문 중복 축소 |
| [Developer Style Guide](https://github.com/lornajane/developer-style-guide/blob/main/README.md) | `README.md`, `dbdd3163c5cd174190ad29e4277478fbfd730534` | 독자와 목표를 기준으로 설명 깊이 조절, 예시·그림 설명과 대체 텍스트 |
| [Vale write-good](https://github.com/vale-cli/write-good) | `write-good/Passive.yml`, `f472cb9049f37c0717389de5c4342a1d1b829b2b`; `write-good/Weasel.yml`, `d1d90a7bcc645f625c824a9d87e1c5d361bc84e2` | 모호한 강조·행동 주체를 편집 검토 대상으로 삼음. 자동 삭제나 한국어 문법 판정으로 사용하지 않음 |

blob SHA는 확인한 파일 내용의 식별자이며 커밋 SHA가 아니다. 링크의 브랜치는 이후 변경될 수 있다.

## 상황별 적용

- 초보자 안내: 필요한 배경과 용어를 먼저 설명한다. 이미 아는 내용까지 길게 반복하지 않는다.
- 운영 절차: 선행 조건과 실행 위치를 밝히고 실행·확인 단계를 구분한다. 제공되지 않은 환경이나 실행 결과는 채우지 않는다.
- 장애 보고: 확인된 사건·영향을 먼저 쓴다. 로그에 행위자가 없으면 능동문을 만들기 위해 원인을 지어내지 않는다.
- 개인 블로그: 계기와 실제 경험의 흐름을 유지한다. 기술 문서의 명령형 제목이나 무감정한 어투를 일괄 적용하지 않는다.

## 일괄 적용하지 않은 규칙

- 영어의 수동태·문장 대소문자·80자 줄바꿈 규칙을 한국어 문법이나 분량 기준으로 옮기지 않는다.
- 물음표·감탄사·완곡 표현을 전면 금지하지 않는다. 글의 목적과 근거에 따라 판단한다.
- 원본의 제품명·명령·로그·직접 인용을 문체 검사에 맞춰 바꾸지 않는다. 필요한 익명화만 일관되게 수행한다.
- 외부 문서의 예시를 사용자의 실제 구매·운영 경험으로 바꾸지 않는다.
- 전문용어가 공식 설정 이름이면 표기를 보존하고 설명을 덧붙인다.

표현 점검은 수정 후보를 찾는 보조 절차다. 통과 여부만으로 사실 정확성이나 사용자 문체 재현을 인증하지 않는다.
