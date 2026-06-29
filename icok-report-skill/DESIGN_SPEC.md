# ICOK 기업분석 리포트 — 양식 & 자동화 스펙 (DESIGN SPEC / SKILL)

> **목적**: 두산에너빌리티 템플릿 기반 ICOK Company Research Report를, **어느 기업의 raw data를 넣어도 동일한 양식**으로 자동 생성하기 위한 단일 기준 문서.
> **사용법(Claude Code)**: 이 파일을 컨텍스트에 넣고 *"이 스펙대로 ○○기업 리포트를 만들어줘. raw data는 …"* 라고 지시. Claude는 아래 **파이프라인 §10**을 순서대로 따른다. 모든 수치·색·좌표·폰트는 본 문서를 **그대로(prescriptive)** 따른다 — 임의 변경 금지.
> **플랫폼**: Windows + PowerShell/Bash. Python(matplotlib·python-pptx·openpyxl·Pillow) + LibreOffice(soffice). **`PYTHONUTF8=1` 필수.**

---

## 0. 절대 규칙 (Non-negotiables)
1. **베이스 템플릿을 복제**해 슬라이드를 만든다. 백지에서 새로 그리지 않는다 → 양식 일관성의 핵심.
2. **임베딩 폰트(Pretendard) 보존**. python-pptx 라운드트립은 보존하지만, de-bold/subset/폰트치환 패스는 **절대 실행 금지**. 저장 후 `*.fntdata` 크기로 검증(§9).
3. **모든 수치는 "정합표(reconciliation table)" 하나에서** 나온다(§10.2). 차트·표·본문이 서로 어긋나면 안 된다.
4. **차트는 표시 크기에 맞춰 그린다**. 슬라이드에서 절반 폭(W3.29")로 축소되므로, figure를 작게(~4.0×2.5") + 폰트를 키워야 글씨가 읽힌다(§4).
5. **자료(exhibit)는 슬라이드 하단**에 캡션 프레임으로 배치(§5–6).
6. 외부 주장 수치는 **검증 후 사용**. 분기치 ≠ 연간치(예: SK하이닉스 DRAM 매출비중 1Q26 78% vs FY26 73.8%).

---

## 1. 캔버스 · 폰트
| 항목 | 값 |
|---|---|
| 슬라이드 크기 | **7.50 × 10.83 in** (세로, 1슬라이드 = 1페이지) |
| 폰트 | **Pretendard** (Bold/Medium/Regular), 파일에 임베딩(`embedTrueTypeFonts="1"`) |
| matplotlib 폰트 | Pretendard 우선, 없으면 Malgun Gothic. `axes.unicode_minus=False` 필수 |
| 인코딩 | 모든 Python 실행 시 `PYTHONUTF8=1` |

```python
# matplotlib 공통 셋업 (모든 차트 스크립트 상단)
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
for c in ["Pretendard","Malgun Gothic"]:
    if c in {f.name for f in fm.fontManager.ttflist}: plt.rcParams["font.family"]=c; break
plt.rcParams["axes.unicode_minus"]=False
```

## 2. 색상 토큰 (HEX, 직접 지정 — 테마 사용 금지)
| 용도 | HEX | 비고 |
|---|---|---|
| **ICOK 블루** | `#005EB8` | 섹션제목·표헤더·자료 캡션바·BUY·사이드바·본문 소제목 |
| **차트 네이비** | `#002A52` | 차트 주색(막대·라인·기준값) |
| **레드** | `#C8101E` | 강조(CAGR·돌파·핵심 콜아웃·해소요인). 대체 `#C00000` |
| 본문 블랙 | `#1A1A1A` | 본문 텍스트 |
| 밴드/음영 | `#CFE0F2` | 차트 밴드·합계행 |
| 서브행 음영 | `#EAF1FA` | 표 교차행 |
| 보더 | `#C2CCD8` / `#BBD0E8` | 표·프레임 |
| 뮤트 그레이 | `#8A97A6` / `#6B7480` | 주석·NM·적자·단위 |

```python
NAVY="#002A52"; RED="#C8101E"; ICOK="#005EB8"; BLACK="#1A1A1A"
BAND="#CFE0F2"; SUB="#EAF1FA"; LINE="#C2CCD8"; GREY="#8A97A6"
```

## 3. 타이포 스케일 (PPTX)
| 요소 | 크기 | 색/굵기 |
|---|---|---|
| 섹션 헤더(예: "4.2 …") | 13 pt | ICOK 블루, Bold |
| 본문 | 10.5 pt | 블랙, Regular, 줄간격 1.22, 단락 후 7pt |
| 자료 캡션 타이틀(네이비 바) | — | 흰색, Bold |
| 출처/단위 | ~8–9 pt | 그레이 |
| 상단 러닝헤더 | — | 좌: 섹션라벨(블루) / 중우: `Company Research Report \| {기업} ({코드})` |

---

## 4. 차트 양식 (matplotlib) — ★팀원이 가장 많이 틀리는 부분
**원칙: "표시 크기로 그리고, 폰트를 키운다."** 자료는 절반 폭 W3.29"로 들어간다. figure가 크면 축소율이 커져 글씨가 안 보인다.

| 규칙 | 값 |
|---|---|
| figsize | **(4.0, 2.5)** 기준, **종횡비 ≈ 1.6 고정** (→ W3.29" 배치 시 H≈2.05" 로 프레임에 맞음) |
| dpi / 저장 | `dpi=200`, `savefig(..., bbox_inches="tight")` |
| **차트 내 타이틀** | **없음** — 제목은 자료 캡션 바가 담당(`set_title` 금지) |
| 폰트 | 축라벨 ~11, 눈금 ~9.5, 주석 ~9.5–10.5, **핵심 콜아웃 ~13(Bold)** |
| 스파인 | top·right 제거. y축만 옅은 그리드(`#E6E9EE`, lw 0.6) |
| 기준선 | 목표/중앙값 = 점선 `ls=(0,(4,3))`, 블루 또는 그레이 |
| **막대 위 라벨/밀집 라벨** | **흰 배경 박스** 필수(저대비 가림 방지): `bbox=dict(boxstyle="round,pad=0.12",fc="white",ec="none",alpha=0.9)` |
| 음수/NM 구간 | 그레이 막대 + "적자 NM" 주석(그레이) |
| 단위 | 한국어(배·만원·조원·%). 라인/막대 색은 §2 토큰만 사용 |

**대표 패턴**
- **시계열 밴드 차트**(PBR/PER 밴드): `axhspan(lo,hi,color=BAND)` + 네이비 라인 + 이탈구간 레드 + 현재값 콜아웃(화살표).
- **이중축 막대+라인**(이익 vs 멀티플): 막대=네이비/그레이(좌축), 라인=레드 마커(우축), 라벨 **흰 박스**, 목표선 점선.
- **워터폴**(re-rating): 시작 네이비 → 증분 레드 → 합계 블루, 점선 커넥터, 천장선 점선.
- **표 이미지**(정성 분해표): `ax.axis("off")` + `Rectangle` 헤더바(네이비) + 교차행 음영 + 우측 태그(잔존=네이비/해소=레드).

```python
# 막대 위에 얹히는 라벨 — 항상 흰 박스로 가독성 확보
WB=dict(boxstyle="round,pad=0.12",fc="white",ec="none",alpha=0.9)
ax.annotate("7.3x",(x,y),textcoords="offset points",xytext=(0,-14),
            ha="center",fontsize=9.5,color=RED,fontweight="bold",bbox=WB,zorder=6)
```

---

## 5. 자료(Exhibit) 캡션 프레임
- 구조 = **3행 표**: ①타이틀바 `자료 N. {제목}`(좌, ICOK블루/네이비 바·흰 Bold) + 단위(우) / ②본문 행(차트·이미지가 위에 올라감) / ③`출처: {원천}, ICOK`(그레이).
- **자료 번호는 문서(슬라이드) 순서대로 연속**. 섹션 중간 삽입 시 이후 번호 재정렬.
- 출처 표기: `출처: FnGuide DataGuide6, ICOK` / `출처: DART, ICOK` / 자체 산출은 `출처: ICOK`.
- 외부 단일 증권사명(예: 특정 리서치) **출처로 노출 지양** — 자체화 시 "ICOK" 또는 일반 표기.

## 6. 슬라이드 레이아웃 / 정렬 (좌표, in)
| 요소 | L | T | W | H |
|---|---|---|---|---|
| 본문 텍스트 박스 | 1.84 | 1.02 | 5.08 | ~4.2 |
| 좌측 사이드바 라벨 | 0.60 | (소제목 높이에 맞춤) | 0.83 | — |
| **자료 프레임(하단)** | 0.42 | **7.68** | 6.70 | 2.74 |
| 자료 이미지 — 좌 | **0.42** | **7.99** | **3.29** | (종횡비) |
| 자료 이미지 — 우 | **3.80** | **7.99** | **3.29** | (종횡비) |

- **자료는 항상 페이지 하단**(다른 자료와 정렬 통일). 2개는 좌·우 2-up.
- 본문 상단 → 자료 하단 구조. 본문이 짧으면 중앙 여백은 정상(다른 슬라이드와 동일 기준).
- 차트 이미지 높이는 종횡비로 자동 계산: `H = W * ih/iw` (W=3.29).

---

## 7. PPTX 조립 (python-pptx)
**핵심: 템플릿 슬라이드를 복제**(폰트는 프레젠테이션 레벨이라 자동 보존). 네이티브 차트는 복제 시 rels 직렬화 오류 → **차트는 건너뛰고 이미지로 대체**.

```python
import copy
from pptx.oxml.ns import qn
REFS=(qn('r:embed'),qn('r:id'),qn('r:link'))
def duplicate_slide(prs, index):
    src=prs.slides[index]; new=prs.slides.add_slide(src.slide_layout)
    for sh in list(new.shapes): sh._element.getparent().remove(sh._element)
    idmap={}
    for rId, rel in src.part.rels.items():                 # 이미지 rel만 재연결
        if rel.is_external or not rel.reltype.endswith("/image"): continue
        idmap[rId]=new.part.relate_to(rel.target_part, rel.reltype)   # 새 rId 발급
    for sh in src.shapes:
        if sh.has_chart: continue                          # 네이티브 차트 skip
        el=copy.deepcopy(sh._element)
        for node in el.iter():                             # XML의 rId remap
            for a in REFS:
                v=node.get(a)
                if v in idmap: node.set(a, idmap[v])
        new.shapes._spTree.append(el)
    return new
# 주의: _Relationships._add_relationship 의 3번째 인자는 is_external 라 rId 직접지정 불가 → relate_to + remap 사용.
```

- **텍스트 교체**: 런(run) 단위로 `.text`만 교체(서식 보존). 단락 재구성 시 폰트=Pretendard, 소제목=ICOK블루 Bold 13pt, 본문=블랙 10.5pt 명시.
- **캡션 셀 채우기 + 이미지 배치**: 프레임 표의 `cell(0,c)`=타이틀, `cell(2,c)`=출처. 이미지는 `add_picture(png, Inches(L), Inches(7.99), width=Inches(3.29), height=Inches(3.29*ih/iw))`.
- **슬라이드 위치 삽입**(섹션 중간): 끝에 추가 후 `prs.slides._sldIdLst` 에서 해당 `sldId`를 원하는 인덱스로 `remove`/`insert`.

---

## 8. 엑셀 산출물(밸류에이션 시트 등) — SWIC 정갈 양식
- openpyxl, **수식 기반**(하드코딩 금지). 헤더 바 + 단위 우측, 서브행 회색 이탤릭 음영, 합계행 틴트, 얇은 보더, 그리드 off, 맑은 고딕.
- 색은 §2 토큰(헤더 ICOK블루 또는 네이비). 입력셀=파랑글씨, 교차참조=녹색.
- **Excel "내용 복구" 경고 회피**: 다중섹션 숫자서식(`;;`·`-`)·빈문자열 셀 금지. 서식 단순화(`#,##0`/`0.0"x"`/`0.0%;(0.0%)`), 빈셀은 value 미설정.
- 백슬래시 `\`는 한글폰트에서 ₩로 보임 → `↓/→` 화살표 사용.
- 재계산/검증: `soffice.exe --headless --convert-to xlsx` 로 변환 후 openpyxl `data_only=True`. (xlsx 스킬 recalc.py 는 Windows AF_UNIX 실패.)

---

## 9. QA 루프 (필수)
```bash
# 1) 렌더
soffice --headless --convert-to pdf --outdir out "리포트.pptx"
pdftoppm -png -r 160 out/리포트.pdf pg
# 2) 자료 가독성 크롭(하단 영역)  — 글씨 작음/겹침 집중 점검
python -c "from PIL import Image; im=Image.open('pg-17.png'); w,h=im.size; im.crop((0,int(h*0.70),w,h)).save('crop.png')"
```
- soffice 는 **`soffice.exe` 직접 호출**(Unix 래퍼 AF_UNIX 실패). 한글 PDF 파일명 깨질 수 있어 `ls -t | head -1` 로 최신본 사용.
- **폰트 임베딩 검증**: `*.fntdata` 개수·최대크기 확인.
```python
import zipfile; z=zipfile.ZipFile("리포트.pptx")
print([z.getinfo(n).file_size for n in z.namelist() if n.endswith(".fntdata")])  # 완전 임베드면 MB 단위 존재
```
- **체크리스트**: ①차트 내 모든 라벨 또렷·겹침無(특히 막대 위 라벨=흰박스) ②자료 하단 정렬·2-up 폭 일치 ③캡션/출처 형식 ④본문 ICOK블루 소제목 ⑤수치 정합(차트=표=본문) ⑥폰트 임베딩 유지 ⑦슬라이드 순서.

---

## 10. 데이터 → 리포트 파이프라인 (Claude 실행 순서)
1. **raw data 수집**: FnGuide DataGuide6(Excel 추출), DART, 컨센서스 xlsx 등. *DataGuide 추출 팁: BandChart 시트의 used-range가 비대 → `Ctrl+Shift+End` 금지, Name Box로 정확 범위 지정 후 copy → 클립보드 파싱.*
2. **정합표 작성**: 매출·영익·OPM·순익·EBITDA·EPS·BPS·PER·PBR·EV/EBITDA·ROE를 **단일 표**로. 연/분기 구분 명확화. 이후 **모든 자료는 이 표에서만** 수치 인용.
3. **차트 생성**(§4): icok_style 규칙대로 PNG. 제목 없이, 종횡비 1.6, 폰트 크게, 막대라벨 흰박스.
4. **슬라이드 조립**(§5–7): 템플릿 복제 → 캡션 프레임 재타이틀 → 이미지 하단 배치 → 섹션 위치 삽입.
5. **QA**(§9): 렌더·크롭·체크리스트·폰트검증. 결함 수정 후 재렌더 1회.
6. **백업**: 편집 전 원본을 `_백업_*.pptx` 로 복사.

### 입력 계약(권장)
- 사용자: *"{기업}({코드}) 리포트. raw=…(DataGuide/DART/xlsx), 목표섹션/자료 목록"* 제공.
- Claude: 정합표 먼저 제시 → 승인 후 차트·슬라이드 생성 → QA 결과(크롭) 제시.

---

## 11. 흔한 함정 (팀원 불일치 원인 Top)
- 차트를 **크게 그려서** 슬라이드에서 글씨가 작아짐 → §4 (figsize 작게+폰트 크게).
- 막대/밀집 영역 라벨이 가려짐 → **흰 박스 bbox** 의무화.
- 자료가 **중구난방 위치** → 항상 **하단 정렬**(T7.68 / 이미지 T7.99).
- 차트마다 **다른 색** → §2 토큰만.
- 백지에서 새 슬라이드 → **반드시 템플릿 복제**(폰트·헤더·여백 일관).
- 폰트 깨짐 → de-bold/subset 금지, UTF8, fntdata 검증.
- 분기치를 연간으로 오용, 외부 수치 미검증 → §0.6.
- 자료 번호 역순/중복 → 문서 순서대로 연속.

---

## 12. 스킬 패키징(권장 최종형)
```
icok-report-skill/
├─ SKILL.md            # "이 스펙(DESIGN_SPEC)대로 {기업} 리포트 생성" 워크플로 = §10
├─ DESIGN_SPEC.md      # 본 문서
├─ scripts/
│   ├─ icok_style.py   # §1·2·4 팔레트·차트 템플릿 함수
│   ├─ pptx_build.py   # §7 duplicate_slide·캡션·임베드·삽입
│   └─ qa.py           # §9 렌더·크롭·폰트검증
└─ assets/template_두산에너빌리티.pptx
```
`.claude/skills/icok-report-skill/` 에 두면, 팀원 Claude Code가 자동 인식 → "○○ 리포트 만들어줘"로 동일 양식 산출. **스크립트를 "실행"하므로 즉흥 재작성으로 인한 양식 흔들림이 없다.**
