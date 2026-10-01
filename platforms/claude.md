# Claude 적용 방법

Claude는 스킬로 쓰는 방법이 가장 편합니다. 글쓰기 요청이 들어오면 스킬 description을 보고 자동으로 불러옵니다.

## 1. Claude 앱 (claude.ai·데스크톱·모바일)

1. `skills/writing-style-doc` 폴더를 zip으로 묶습니다. zip 안에 `writing-style-doc/SKILL.md`가 들어가야 합니다.
2. Claude 설정의 스킬 메뉴에서 업로드합니다. 메뉴 위치는 앱 버전에 따라 다를 수 있습니다.
3. 같은 역할의 다른 문체 스킬이 켜져 있으면 끕니다.

```bash
git clone https://github.com/yjj3019/writing-style-doc.git
cd writing-style-doc/skills
zip -r writing-style-doc.zip writing-style-doc
```

스킬 대신 프로젝트 지침을 쓰고 싶다면 `STYLE.md` 전체본과 아래 보정 문구를 프로젝트 지침 칸에 넣습니다.

## 2. Claude Code

개인 전역 설치:

```bash
mkdir -p ~/.claude/skills
cp -r writing-style-doc/skills/writing-style-doc ~/.claude/skills/
```

특정 프로젝트에만 설치하려면 그 프로젝트의 `.claude/skills/` 아래에 복사합니다.

## Claude 보정 문구

프로젝트 지침으로 쓸 때 전체본 뒤에 붙입니다. 스킬에는 같은 내용이 이미 들어 있습니다.

```text
## Claude 보정
- 블로그·기고는 문단 중심으로 쓴다. 소제목과 글머리표는 비교·절차에만 쓴다.
- "~일 수 있습니다", "~할 수도 있습니다" 같은 완곡 표현을 연달아 쓰지 않는다.
- 작성 메모 외에 작업 과정이나 판단 이유를 본문 앞뒤에 덧붙이지 않는다.
- 요청한 분량보다 길게 쓰지 않는다. 같은 내용을 다른 말로 반복하지 않는다.
```
