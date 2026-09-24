# -*- coding: utf-8 -*-
"""세부섹터 스터디 종합본 템플릿 (A4 가로 7장) 생성.

9/29 세션용. 1장 = 1파트 = 발표 2분. 화면 공유를 전제로 가로 배치한다.
사용: python3 make_sector_study.py [출력경로]
"""
import sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION, WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = sys.argv[1] if len(sys.argv) > 1 else 'ICOK_세부섹터_스터디_템플릿.docx'
F = '맑은 고딕'
NAVY = (0x1F, 0x2A, 0x44); GRAY = (0x5A, 0x5A, 0x5A); RED = (0x9C, 0x00, 0x06)


def style(run, size=10, bold=False, color=None):
    run.font.size = Pt(size); run.font.bold = bold; run.font.name = F
    run._element.rPr.rFonts.set(qn('w:eastAsia'), F)
    if color:
        run.font.color.rgb = RGBColor(*color)


def para(doc, text='', size=10, bold=False, color=None, after=3, align=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(after); p.paragraph_format.space_before = Pt(0)
    if align:
        p.alignment = align
    style(p.add_run(text), size, bold, color)
    return p


def cell(c, text='', size=9, bold=False, color=None, align=None, shade=None):
    c.text = ''
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(0); p.paragraph_format.space_before = Pt(0)
    if align:
        p.alignment = align
    style(p.add_run(text), size, bold, color)
    if shade:
        el = OxmlElement('w:shd'); el.set(qn('w:fill'), shade)
        c._tc.get_or_add_tcPr().append(el)


def table(doc, headers, widths, rows=1, hshade='D6DCE4'):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = 'Table Grid'
    for i, h in enumerate(headers):
        cell(t.rows[0].cells[i], h, 9, True, NAVY,
             WD_ALIGN_PARAGRAPH.CENTER if i else None, hshade)
    for _ in range(rows):
        t.add_row()
    for w, i in zip(widths, range(len(headers))):
        for r in t.rows:
            r.cells[i].width = Cm(w)
    return t


def box(doc, text, h=5.0):
    """그래프·그림을 붙일 빈 영역."""
    t = doc.add_table(rows=1, cols=1); t.style = 'Table Grid'
    c = t.rows[0].cells[0]
    cell(c, text, 9, False, GRAY, WD_ALIGN_PARAGRAPH.CENTER)
    c.width = Cm(27)
    t.rows[0].height = Cm(h)
    return t


def page(doc, first=False):
    if not first:
        doc.add_section(WD_SECTION.NEW_PAGE)
    s = doc.sections[-1]
    s.orientation = WD_ORIENT.LANDSCAPE
    s.page_width, s.page_height = Cm(29.7), Cm(21)
    s.top_margin = s.bottom_margin = Cm(1.2)
    s.left_margin = s.right_margin = Cm(1.5)
    return s


def header(doc, no, title, minutes, why):
    para(doc, f'{no}.  {title}', 16, True, NAVY, after=1)
    para(doc, f'발표 {minutes}  |  담당자 __________  |  {why}', 9, color=GRAY, after=7)


def gap(doc, pt=6):
    doc.add_paragraph().paragraph_format.space_after = Pt(pt)


def main():
    doc = Document()
    page(doc, first=True)

    # ── 표지 겸 진행표 ───────────────────────────────────────────
    para(doc, '세부섹터 스터디 종합본', 20, True, NAVY, after=1)
    para(doc, 'ICOK Fund 26-2  ·  2026년 9월 29일 세션  ·  팀당 발표 12분 + 질의 5분', 10,
         color=GRAY, after=10)

    t = table(doc, ['', '항목', '기재'], [1.2, 6, 19.8], rows=0)
    for k, v in (('팀', ''), ('세부섹터', ''), ('선정 사유', '(팀 미니 IC 의결 · 한 줄)'),
                 ('작성자', ''), ('작성 기준일', '2026-09-__'), ('제출', '9월 28일 자정')):
        r = t.add_row().cells
        cell(r[0], '', 9); cell(r[1], k, 9, True, NAVY, shade='F2F2F2'); cell(r[2], v, 9, color=GRAY)
    for c_, w in ((0, 1.2), (1, 6), (2, 19.8)):
        for r in t.rows:
            r.cells[c_].width = Cm(w)
    gap(doc, 10)

    para(doc, '이 과제가 요구하는 것', 12, True, NAVY, after=3)
    for ln in (
        '이 과제는 산업 전망이 아니라 현황 파악이다. 투자 결론을 쓰지 않는다.',
        '각 파트는 「무엇을 계산하거나 수집해 왔는가」로 평가한다. 서술만 있고 산출이 없으면 미제출로 본다.',
        '1장 = 1파트 = 발표 2분이다. 장을 늘리지 않는다.',
    ):
        para(doc, f'·  {ln}', 10, after=2)
    gap(doc, 8)

    para(doc, '금지 사항', 12, True, RED, after=3)
    for ln in (
        '증권사 리포트를 논지의 근거로 사용하지 않는다. 목표주가를 인용하지 않는다.',
        '검증 불가능한 표현을 쓰지 않는다. 유망하다 · 성장성이 크다 · 저평가되어 있다.',
        '전망 표현을 쓰지 않는다. 전망한다 · 수혜가 예상된다 · 성장이 기대된다.',
        '그래프 3개 이상은 팀이 직접 그린 것이어야 한다. 캡처 이미지는 출처를 달되 3개에 포함하지 않는다.',
        '모든 수치에 출처와 기준일을 기재한다. 1순위 자료는 DART 사업보고서다.',
    ):
        para(doc, f'·  {ln}', 10, after=2)

    # ── 1. 섹터 정의와 밸류체인 ────────────────────────────────
    page(doc)
    header(doc, 1, '섹터 정의와 밸류체인', '2분',
           '산출: 밸류체인 그림 1개 + 담당 종목 배치')
    t = table(doc, ['KRX 300 편입', 'BM 비중', '팀 배정액', '1주 최대 종목', '최저가 종목'],
              [5, 4.5, 6, 6, 5.5], rows=1)
    gap(doc, 5)
    para(doc, '밸류체인  —  전방에서 후방까지 단계를 그리고, 각 단계에 담당 종목을 배치한다', 10, True, after=3)
    box(doc, '밸류체인 그림을 여기에 붙인다', 7.2)
    gap(doc, 5)
    t = table(doc, ['밸류체인 단계', '하는 일', '이 단계의 담당 종목', 'BM 비중 합'],
              [5, 8, 9.5, 4.5], rows=4)

    # ── 2. 돈이 어디서 나오는가 ───────────────────────────────
    page(doc)
    header(doc, 2, '돈이 어디서 나오는가 — 수익 구조', '2분',
           '산출: 대표 3사 사업보고서 매출 구성표를 직접 옮겨 적는다')
    para(doc, '제품별 매출 구성  (최근 사업연도 · 단위 %)', 10, True, after=3)
    t = table(doc, ['기업', '제품 1', '비중', '제품 2', '비중', '제품 3', '비중', '기타', '출처 · 기준일'],
              [3.6, 3.4, 1.8, 3.4, 1.8, 3.4, 1.8, 1.8, 5.6], rows=3)
    gap(doc, 5)
    para(doc, '지역별 매출 구성  (단위 %)', 10, True, after=3)
    t = table(doc, ['기업', '국내', '중국', '미국', '유럽', '기타', '수출 비중', '출처 · 기준일'],
              [3.6, 2.6, 2.6, 2.6, 2.6, 2.6, 3, 7], rows=3)
    gap(doc, 5)
    para(doc, '이 섹터의 매출은 단가와 물량 중 무엇이 움직이는가  —  근거 숫자를 함께 적는다', 10, True, after=3)
    table(doc, ['판정 (단가 / 물량 / 둘 다)', '근거 숫자'], [7, 20], rows=1)

    # ── 3. 사이클 변수 3개 ─────────────────────────────────────
    page(doc)
    header(doc, 3, '사이클을 움직이는 변수 3개', '2분',
           '산출: 5년 시계열 그래프 3개를 직접 작성한다. 이 파트가 이 과제의 중심이다')
    t = table(doc, ['#', '변수', '왜 이 변수인가', '데이터 소스', '기간', '최근값 · 기준일'],
              [1.2, 5, 8, 5.5, 3, 4.3], rows=3)
    gap(doc, 5)
    para(doc, '각 변수의 5년 시계열  —  대표사 영업이익률을 같은 그래프에 겹쳐 그린다', 10, True, after=3)
    t = doc.add_table(rows=1, cols=3); t.style = 'Table Grid'
    for i, lab in enumerate(('변수 1 그래프', '변수 2 그래프', '변수 3 그래프')):
        cell(t.rows[0].cells[i], lab, 9, False, GRAY, WD_ALIGN_PARAGRAPH.CENTER)
        t.rows[0].cells[i].width = Cm(9)
    t.rows[0].height = Cm(7)
    gap(doc, 5)
    para(doc, '세 그래프를 겹쳐 보고 읽은 것을 두 줄로 적는다. 전망이 아니라 관찰을 적는다.',
         10, True, after=3)
    table(doc, ['관찰'], [27], rows=2)

    # ── 4. 경쟁 구도 ──────────────────────────────────────────
    page(doc)
    header(doc, 4, '경쟁 구도', '2분', '산출: 점유율 표 + 진입장벽을 뒷받침하는 숫자 하나')
    para(doc, '점유율  (기준 시장을 먼저 정의한다 — 글로벌인지 국내인지, 금액 기준인지 수량 기준인지)',
         10, True, after=3)
    para(doc, '기준 시장 정의 : ________________________________________________', 9, color=GRAY, after=5)
    t = table(doc, ['순위', '기업', '점유율', '전년 대비', '상장 여부 · 국가', '출처 · 기준일'],
              [1.8, 5.5, 3, 3.5, 5.5, 7.7], rows=5)
    gap(doc, 5)
    para(doc, '진입장벽', 10, True, after=3)
    t = table(doc, ['진입장벽은 무엇인가 (한 문장)', '그것을 뒷받침하는 숫자 하나', '출처'],
              [11, 10, 6], rows=1)
    gap(doc, 4)
    para(doc, '설비 투자액 · 인증 소요기간 · 고객 전환비용 · 특허 건수 중 하나를 고른다. '
              '숫자가 없으면 진입장벽이 있다고 쓰지 않는다.', 9, color=GRAY, after=0)

    # ── 5. 시장이 지금 기대하는 것 ─────────────────────────────
    page(doc)
    header(doc, 5, '시장이 지금 기대하고 있는 것', '2분',
           '산출: 산포도 1개 + 컨센서스 변화율 표. 스크리닝 시트에서 대부분 나온다')
    para(doc, '섹터 전 종목 산포도  —  가로축 12M Fwd PER, 세로축 ROE', 10, True, after=3)
    box(doc, '산포도를 여기에 붙인다 (종목명 라벨 포함)', 7.5)
    gap(doc, 5)
    para(doc, '컨센서스 변화  —  1년 전 대비 2026(E) 영업이익 전망치 변화율 상하위 3종목', 10, True, after=3)
    t = table(doc, ['구분', '종목', '1년 전 전망', '현재 전망', '변화율', '12M Fwd PER', 'PBR', '출처 · 기준일'],
              [3, 4.5, 3.5, 3.5, 3, 3.5, 2.5, 4.5], rows=6)

    # ── 6. 용어집 ─────────────────────────────────────────────
    page(doc)
    header(doc, 6, '용어집 20개', '1분',
           '산출: 섹터 전문용어 20개를 팀이 직접 정의한다. 신입이 읽고 이해할 수 있어야 한다')
    t = doc.add_table(rows=11, cols=6); t.style = 'Table Grid'
    for col in (0, 3):
        cell(t.rows[0].cells[col], '#', 9, True, NAVY, WD_ALIGN_PARAGRAPH.CENTER, 'D6DCE4')
        cell(t.rows[0].cells[col + 1], '용어', 9, True, NAVY, None, 'D6DCE4')
        cell(t.rows[0].cells[col + 2], '정의 (한 줄)', 9, True, NAVY, None, 'D6DCE4')
    for i in range(1, 11):
        cell(t.rows[i].cells[0], str(i), 9, align=WD_ALIGN_PARAGRAPH.CENTER)
        cell(t.rows[i].cells[3], str(i + 10), 9, align=WD_ALIGN_PARAGRAPH.CENTER)
    for c_, w in zip(range(6), (1, 3.5, 9, 1, 3.5, 9)):
        for r in t.rows:
            r.cells[c_].width = Cm(w)

    # ── 7. 우리가 모르는 것 ───────────────────────────────────
    page(doc)
    header(doc, 7, '우리가 모르는 것 5개', '1분',
           '산출: 이번 스터디로 답이 안 나온 질문 5개. 10월 6일 종목 발제의 출발점이 된다')
    t = table(doc, ['#', '모르는 것 (질문 형태로)', '무엇을 보면 답이 나오는가', '확인 담당'],
              [1.2, 11, 11, 3.8], rows=5)
    for i in range(1, 6):
        cell(t.rows[i].cells[0], str(i), 9, align=WD_ALIGN_PARAGRAPH.CENTER)
    gap(doc, 8)
    para(doc, '이 파트를 채우지 못하면 이번 스터디는 실패한 것이다. '
              '5일 공부로 산업을 다 알 수는 없고, 무엇을 모르는지 아는 것이 목표다.',
         10, True, NAVY, after=6)
    para(doc, '「자료가 없어서 모른다」와 「자료는 있는데 아직 안 봤다」를 구분해서 적는다. '
              '앞의 것은 그 섹터의 구조적 한계이고, 뒤의 것은 다음 주 숙제다.', 9, color=GRAY, after=0)

    doc.save(OUT)
    print(f'저장: {OUT}')


if __name__ == '__main__':
    main()
