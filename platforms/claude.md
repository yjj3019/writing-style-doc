# Claude 적용 방법

Claude는 스킬 또는 프로젝트 지침으로 적용할 수 있습니다. 스킬의 description은 관련 글쓰기 요청에서 스킬을 선택하는 기준입니다.

공식 안내 확인일: 2026-10-02. 스킬은 관련 요청에서 자동 선택될 수 있지만, 항상 선택되는 것은 아니므로 적용 여부를 확인합니다.

## 1. Claude 앱 (claude.ai·데스크톱·모바일)

1. `skills/writing-style-doc` 폴더를 zip으로 묶습니다. zip 안에 `writing-style-doc/SKILL.md`가 들어가야 합니다.
2. `Code execution and file creation`을 활성화합니다. 조직 계정은 관리자 설정도 확인합니다.
3. `Customize > Skills`에서 스킬 ZIP을 업로드하고 활성화합니다. 메뉴 위치와 업로드 가능 여부는 계정·앱 버전에 따라 확인합니다.
4. 같은 역할의 다른 문체 스킬이 켜져 있으면 끕니다.

```bash
git clone https://github.com/yjj3019/writing-style-doc.git
cd writing-style-doc
python3 scripts/package_skill.py --output writing-style-doc.zip
```

스킬 대신 프로젝트 지침을 쓰고 싶다면 `STYLE.md` 전체본과 아래 보정 문구를 프로젝트 지침 칸에 넣습니다.

## 2. Claude Code

개인 전역 설치:

아래 명령은 저장소 루트(`writing-style-doc/`)에서 실행합니다. ZIP 생성 명령 다음에도 같은 위치입니다.

```bash
mkdir -p ~/.claude/skills
cp -R skills/writing-style-doc ~/.claude/skills/
```

특정 프로젝트에만 설치하려면 그 프로젝트의 `.claude/skills/` 아래에 복사합니다.

Windows PowerShell에서는 저장소 루트에서 실행합니다.

```powershell
New-Item -ItemType Directory -Force "$HOME/.claude/skills" | Out-Null
Copy-Item -Recurse -Force ./skills/writing-style-doc "$HOME/.claude/skills/"
```

설치 후 Claude Code에서 `/writing-style-doc`를 명시해 글을 다듬어 봅니다. 일반 질문과 코드 작업에는 적용되지 않는지도 확인합니다. 이미 설치했다면 복사한 파일도 새 버전으로 갱신해야 합니다.

## Claude 보정 문구

프로젝트 지침으로 쓸 때 전체본 뒤에 붙입니다. 아래 블록은 동기화 스크립트가 스킬에도 그대로 반영합니다.

```text
## Claude 보정
- 블로그·기고는 문단 중심으로 쓴다. 소제목과 글머리표는 비교·절차에만 쓴다.
- "~일 수 있습니다", "~할 수도 있습니다" 같은 완곡 표현을 연달아 쓰지 않는다.
- 작성 메모 외에 작업 과정이나 판단 이유를 본문 앞뒤에 덧붙이지 않는다.
- 요청한 분량보다 길게 쓰지 않는다. 같은 내용을 다른 말로 반복하지 않는다.
```

공식 출처: [Claude Code 스킬](https://code.claude.com/docs/en/skills), [Claude 앱 스킬](https://support.claude.com/en/articles/12512180-using-skills-in-claude). 조직 정책과 현재 앱 화면에서 업로드·활성화를 확인합니다.
