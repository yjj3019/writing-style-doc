#!/usr/bin/env python3
"""Generate the self-contained skill from STYLE.md and platform corrections."""
import argparse
import json
from pathlib import Path
import re
import sys


def text_block(path, heading):
    text = path.read_text(encoding="utf-8")
    section = text.split(heading, 1)[1]
    match = re.search(r"```text\n(.*?)\n```", section, re.S)
    if not match:
        raise ValueError(f"Missing text block: {path} / {heading}")
    return match.group(1)


def render(root):
    body = (root / "STYLE.md").read_text(encoding="utf-8").split("\n---\n", 1)[1].strip()
    description = "한국어 블로그·기술 기고·사용기·설정 기록·README·가이드·업무 문서 작성과 편집에 사용한다. 일반 질문·코드·주석·커밋 메시지·PR 설명·작업 완료 보고에는 사용하지 않는다."
    corrections = "\n\n".join(
        text_block(root / f"platforms/{platform}.md", heading)
        for platform, heading in (("claude", "## Claude 보정 문구"), ("codex", "## Codex 보정 문구"))
    )
    return (
        "---\nname: writing-style-doc\ndescription: "
        + json.dumps(description, ensure_ascii=False)
        + "\n---\n\n# writing-style-doc\n\n"
        + "이 파일은 STYLE.md와 플랫폼 보정 문구에서 생성한다. 직접 수정하지 않는다."
        + "\n\n" + body
        + "\n\n## 실행 환경별 보정\n\n해당 환경의 보정만 적용한다.\n\n"
        + corrections
        + "\n\n## 문체 예시\n\n문체가 모호할 때 [익명화한 편집 예시](references/examples.md)를 읽는다. 예시는 가상이며 사용자 경험으로 재사용하지 않는다.\n"
        + "\n## 참고 지침\n\n독자·목적, 링크·예시 설명, 표현 점검의 적용 범위가 필요하면 [외부 지침 반영 기준](references/editorial-principles.md)을 읽는다. 외부 규칙보다 사용자의 요청과 사실 보존을 우선한다.\n"
        + "\n문서 구성이나 표현 수정 여부가 모호하면 [편집 점검 기준](references/editing-checklist.md)을 읽는다. 추가 참고 저장소의 고정 커밋과 채택·제외 이유는 [참고 근거](references/sources.md)에 있다. 기본 작업에는 전체 참고 문서를 반복해서 읽을 필요가 없다.\n"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check without writing")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    expected = render(root)
    target = root / "skills/writing-style-doc/SKILL.md"
    short = text_block(root / "platforms/chatgpt.md", "## 짧은 버전")
    if len(short) > 1500:
        print(f"Short instructions exceed 1500 characters: {len(short)}", file=sys.stderr)
        return 1
    if args.check and (not target.exists() or target.read_text(encoding="utf-8") != expected):
        print("SKILL.md is out of sync. Run python3 scripts/sync_style.py", file=sys.stderr)
        return 1
    if not args.check:
        target.write_text(expected, encoding="utf-8")
    body = (root / "STYLE.md").read_text(encoding="utf-8").split("\n---\n", 1)[1].strip()
    grok = text_block(root / "platforms/grok.md", "## Grok 보정 문구")
    print(f"{'Checked' if args.check else 'Generated'} SKILL.md; full={len(body)}, short={len(short)}, Grok with correction={len(body + chr(10) + grok)} characters")
    print("Short-version semantic consistency and model output quality require manual evaluation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
