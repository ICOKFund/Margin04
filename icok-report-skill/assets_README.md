# assets — 베이스 템플릿

ICOK 리포트는 **백지에서 만들지 않고 두산에너빌리티 기반 deck을 복제**해 만든다(양식 일관성의 핵심).

## 사용법
1. 팀원의 **두산에너빌리티 기반 deck**(표준 자료/본문 레이아웃이 들어있는 .pptx)을 이 폴더에 `template.pptx`로 둔다.
   - 또는 `scripts/example_skhynix.py`의 `SRC`처럼 베이스 deck의 절대경로를 직접 지정해도 된다.
2. **표준 자료(exhibit) 레이아웃 슬라이드의 인덱스**를 확인해 `EXHIBIT_MASTER`로 지정한다.
   - 이 슬라이드를 `pptx_build.duplicate_slide(prs, EXHIBIT_MASTER)`로 복제해 새 자료 슬라이드를 만든다.
   - 확인법:
     ```
     set PYTHONUTF8=1
     python -c "from pptx import Presentation; p=Presentation(r'assets/template.pptx'); [print(i, s.shapes.title.text if s.shapes.title else '') for i,s in enumerate(p.slides)]"
     ```

## 왜 deck을 동봉하지 않나
베이스 deck은 각 팀원이 이미 보유한 두산에너빌리티 양식이며, 회사·버전마다 다를 수 있어 **사용자가 직접 지정**하는 편이 안전하다. 스킬은 그 deck 위에 **차트 양식·캡션·정렬·폰트 보존 규칙**을 강제하는 역할을 한다.

## 폰트
deck에 Pretendard가 임베딩(`embedTrueTypeFonts="1"`)돼 있어야 한다. python-pptx 복제는 임베딩을 보존하므로, 베이스 deck이 임베딩돼 있으면 산출물도 유지된다. 저장 후 `pptx_build.verify_fonts()` 또는 `qa.py`로 `.fntdata` 크기를 확인한다.
