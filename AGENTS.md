# 저장소 편집 기준

- `STYLE.md`의 구분선 아래가 공통 문체 규칙의 기준이다. `platforms/claude.md`, `platforms/codex.md`의 보정 문구와 함께 `scripts/sync_style.py`가 스킬을 생성한다. 생성된 `SKILL.md`를 직접 수정하지 않는다.
- 의미가 바뀌면 `platforms/chatgpt.md`의 짧은 버전과 예시·평가 사례도 확인한다. 필수·권장·선택 규칙의 강도를 플랫폼마다 바꾸지 않는다.
- `skills/writing-style-doc/references/`에는 필요한 상세 기준만 넣고 스킬에서 직접 링크한다. 외부 자료를 참고하면 출처와 반영 범위를 기록한다. 외부 문장·코드·규칙 파일을 복제할 때는 라이선스를 확인한다.
- 사용자 경험·의견·감정과 비밀값을 만들거나 저장하지 않는다. 가상 예시는 가상이라고 표시한다.
- 변경 후 `python3 scripts/sync_style.py`, `python3 scripts/sync_style.py --check`, `python3 scripts/package_skill.py --output <저장소 밖의 임시 ZIP>`을 실행하고 참조 링크·ZIP 내용을 확인한다.
- 동기화·패키지 검사를 모델 품질 검증이라고 보고하지 않는다. 새 행동 규칙에는 수동 평가 입력을 보완한다.

- 편집 강도는 교정·다듬기·재작성으로 구분하고 범위 미지정은 최소 다듬기로 처리한다. 신규 작성·요약은 해당 요청을 따른다.
- 변경 후 `python3 scripts/validate_repo.py`, `python3 -m unittest discover -s tests`도 실행한다. 버전 변경은 `VERSION`을 수정한 뒤 스킬을 재생성한다.
- 평가 기록에는 정확한 익명화 입력·출력과 지침 커밋, 네 평가 축을 기록한다. 실제 문체 자료가 없으면 개인 문체는 판정 불가다. 미기록 모델·설정을 추정해 채우지 않는다.

- 배포 파일의 로컬 링크가 ZIP 내부에서 해결되는지 확인한다. references 폴더를 포함한 부모 경로의 심볼릭 링크를 허용하지 않는다.
- schema_version 2 평가 기록에는 실제 지침 해시와 개인 문체 자료 식별자를 남긴다. 전체 이력이 있으면 `python3 scripts/validate_repo.py --verify-history`로 당시 커밋·버전을 대조한다.
- CI에서 지정한 Python 버전별 실제 실행 결과와 문법 검사·모델 출력 관찰을 구분한다.
