---
name: icok-report
description: "ICOK 기업분석 리포트(두산에너빌리티 템플릿 기반)를 동일한 양식으로 생성. 어느 기업의 raw data(FnGuide DataGuide6/DART/컨센서스 xlsx)를 넣어도 차트 양식·정렬·캡션·폰트(Pretendard 임베딩)·색상(ICOK블루 #005EB8)이 일관되게 자동 가공됨. PPTX 자료(exhibit) 차트·슬라이드 조립·QA 포함. ICOK 리포트/자료/밸류에이션 슬라이드를 만들 때 사용."
trigger: /icok-report
---

# /icok-report — ICOK 기업분석 리포트 자동 생성

두산에너빌리티 템플릿 기반 ICOK Company Research Report를, **어느 기업의 raw data를 넣어도 동일 양식**으로 생성한다. 차트는 즉흥으로 그리지 말고 **`scripts/icok_style.py` 함수를 호출**하고, 슬라이드는 **`scripts/pptx_build.py`로 템플릿을 복제**해 조립한다. → 즉흥 재작성으로 인한 양식 흔들림 방지.

## 시작 전 반드시 읽기
- **[DESIGN_SPEC.md](DESIGN_SPEC.md)** — 색·폰트·좌표·차트 규칙의 단일 기준(prescriptive). 임의 변경 금지.
- 모든 수치·색·좌표·폰트는 DESIGN_SPEC을 **그대로** 따른다.

## 플랫폼 전제
- Windows + Python(matplotlib·python-pptx·openpyxl·Pillow) + LibreOffice(soffice).
- **모든 Python 실행 시 `PYTHONUTF8=1` 필수** (`set PYTHONUTF8=1`).

## 절대 규칙 (DESIGN_SPEC §0)
1. **템플릿 슬라이드를 복제**해 만든다 — 백지 금지(양식 일관성의 핵심).
2. **Pretendard 임베딩 보존** — de-bold/subset/폰트치환 금지. 저장 후 `.fntdata`로 검증.
3. **모든 수치는 정합표 하나에서** — 차트·표·본문 불일치 금지.
4. **차트는 표시 크기로 그린다** — figsize 작게(~4.0×2.5, 종횡비 1.6) + 폰트 크게. 절반 폭(W3.29")로 축소돼도 읽히게.
5. **자료(exhibit)는 슬라이드 하단**에 캡션 프레임으로 배치.
6. 외부 수치는 **검증 후 사용**. 분기치 ≠ 연간치.

## 워크플로 (DESIGN_SPEC §10)
1. **raw data 수집** — FnGuide DataGuide6(Excel), DART, 컨센서스 xlsx.
   - DataGuide 추출 팁: BandChart 시트 used-range가 비대 → `Ctrl+Shift+End` 금지. Name Box로 정확 범위 지정 후 copy → 클립보드 파싱.
2. **정합표 작성 후 사용자 승인** — 매출·영익·OPM·순익·EBITDA·EPS·BPS·PER·PBR·EV/EBITDA·ROE를 **단일 표**로. 연/분기 구분. 이후 모든 자료는 이 표에서만 인용.
3. **차트 생성** — `scripts/icok_style.py` 사용:
   ```python
   import icok_style as S; S.setup()
   S.band_chart("자료N.png", dates, pbr, lo, hi, median=..., current="현재 8.0x")   # 시계열 밴드
   S.bar_line("자료N.png", cats, eps, pe, target=8.5, target_label="목표 8.5x")     # 이중축 막대+라인
   S.waterfall("자료N.png", labels, start, steps, target, ceiling=...)             # re-rating 워터폴
   S.factor_table("자료N.png", rows, title=..., footnote=...)                       # 정성 분해표
   ```
   - 차트 내 타이틀 금지(제목=캡션 바). 막대 위 라벨은 자동 흰 박스. 색은 모듈 토큰만.
4. **슬라이드 조립** — `scripts/pptx_build.py` 사용:
   ```python
   import pptx_build as B
   s = B.duplicate_slide(prs, EXHIBIT_MASTER)      # 표준 자료 레이아웃 슬라이드 복제
   B.set_caption(frame_table, titles, sources)     # 자료 N. 제목 / 출처
   B.fill_body(text_frame, [(소제목,'h'),(본문,'b')])
   B.place_exhibits(s, ["자료N.png","자료M.png"])   # 하단 2-up
   B.move_slide(prs, -1, 16)                        # 섹션 중간 삽입
   ```
   - 출처: `출처: FnGuide DataGuide6, ICOK` / `출처: DART, ICOK` / 자체산출 `출처: ICOK`. 단일 증권사명 노출 지양.
5. **QA** — `scripts/qa.py`:
   ```
   set PYTHONUTF8=1
   python scripts/qa.py "리포트.pptx" 17    # 렌더 + 17p 자료 하단 크롭 + 폰트검증
   ```
   체크: ①라벨 또렷·겹침無 ②자료 하단 정렬·2-up 폭 일치 ③캡션/출처 형식 ④본문 ICOK블루 소제목 ⑤수치 정합 ⑥폰트 임베딩 ⑦슬라이드 순서·자료번호 연속. 결함 수정 후 재렌더 1회.
6. **백업** — 편집 전 원본을 `_백업_*.pptx`로 복사.

## 입력 계약 (사용자에게 요청할 것)
> *"{기업}({코드}) 리포트. raw=…(DataGuide/DART/xlsx), 베이스 deck 경로, 표준 자료 레이아웃 슬라이드 인덱스, 추가할 섹션/자료 목록."*

Claude는 **정합표를 먼저 제시 → 승인 후** 차트·슬라이드 생성 → QA 결과(크롭) 제시.

## 워크드 예제
`scripts/example_skhynix.py` — SK하이닉스 밸류에이션 자료 2슬라이드(자료 30~33)를 실제로 만드는 **복붙 출발점**. 정합표(DATA)만 교체하고, `build_slide()`의 템플릿 구조 의존 부분(자료 프레임/사이드바 식별 문자열, 삽입 인덱스)을 대상 deck에 맞게 조정하면 다른 기업에 적용된다.

## 베이스 템플릿
`assets/README.md` 참고. 팀원의 **두산에너빌리티 기반 deck**을 `assets/template.pptx`로 두고, `EXHIBIT_MASTER`(표준 자료 레이아웃 슬라이드 인덱스)만 지정하면 된다. 베이스 deck이 곧 양식의 원천이므로 **복제로만** 슬라이드를 만든다.

## 흔한 함정 (팀원 불일치 원인 — DESIGN_SPEC §11)
- 차트를 크게 그려 글씨가 작아짐 → figsize 작게+폰트 크게.
- 막대/밀집 라벨 가려짐 → **흰 박스 bbox** 의무.
- 자료가 중구난방 → 항상 **하단 정렬**(T7.68 / 이미지 T7.99).
- 차트마다 다른 색 → 토큰만(NAVY/RED/ICOK).
- 백지 슬라이드 → **반드시 템플릿 복제**.
- 폰트 깨짐 → de-bold/subset 금지, `PYTHONUTF8=1`, `.fntdata` 검증.
- 분기치를 연간으로 오용 / 외부 수치 미검증.
