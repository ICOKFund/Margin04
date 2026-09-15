# -*- coding: utf-8 -*-
"""담당 산업 스크리닝 워크북 생성.

기입 완료 항목(기업명·코드·주가·시총·지수비중·매수판정)은 음영 처리하고,
작성 항목만 흰색으로 남긴다.

사용: python3 make_screening_book.py [CSV] [NAV] [출력경로]
"""
import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter
from sector_map import build, MEGA
from weights import load, BANK

CSV = sys.argv[1] if len(sys.argv) > 1 else 'krx300_constituents_20260915.csv'
NAV = float(sys.argv[2]) if len(sys.argv) > 2 else 28_000_000
OUT = sys.argv[3] if len(sys.argv) > 3 else 'ICOK_담당산업_스크리닝.xlsx'
ASOF = '2026-09-15'
HARD_CAP, BUDGET_CAP = 8.0, 6.0

MANDATE = {
    '자동차·부품': 1, '2차전지·소재': 1, 'IT하드웨어·부품': 1,
    '지주(반도체 프록시)': 1, '반도체·소부장': 1, '소프트웨어·인터넷·게임': 1,
    '전력기기·유틸리티': 2, '조선·기자재': 2, '에너지·상사·운송': 2,
    '기계·건설·로봇': 2, '방산·우주': 2, '소재·화학·철강': 2,
    '금융 — 은행·지주': 3, '헬스케어·바이오': 3, '금융 — 보험·증권': 3,
    '소비재·유통': 3, '통신·미디어·엔터': 3,
}
TEAM = {1: '테크·전동화', 2: '중후장대·인프라', 3: '내수·디펜시브'}
NOTE = {
    '반도체·소부장': '41종목. 전공정(장비·소재) / 후공정(기판·테스트·패키징)으로 분할하여 2인이 분담할 것을 권장한다.',
    '지주(반도체 프록시)': 'SK스퀘어 1종목. SK하이닉스 지분 룩스루 배수 1.8배. 팀장이 관리한다.',
    '헬스케어·바이오': '44종목 중 다수가 매출 미발생 임상 단계 기업이다. 매출·영업이익률·PER 산출이 불가능한 기업은 하위 테마에 「파이프라인」으로 표기한다.',
    '금융 — 은행·지주': '매출·영업이익률 대신 NIM·대손비용률·CET1·주주환원율을 사용한다. 밸류에이션은 PBR-ROE 기준.',
    '금융 — 보험·증권': '보험은 IFRS17 기준 CSM을 확인한다.',
}

F = '맑은 고딕'
TITLE   = Font(name=F, size=15, bold=True, color='1F2A44')
SUB     = Font(name=F, size=9,  color='5A5A5A')
HEAD    = Font(name=F, size=9,  bold=True, color='FFFFFF')
LABEL   = Font(name=F, size=9,  bold=True, color='1F2A44')
BODY    = Font(name=F, size=9)
BOLD    = Font(name=F, size=9,  bold=True)
BAD     = Font(name=F, size=9,  bold=True, color='9C0006')

C_HEAD  = PatternFill('solid', fgColor='44546A')
C_LABEL = PatternFill('solid', fgColor='D6DCE4')
C_GIVEN = PatternFill('solid', fgColor='F2F2F2')
C_BAND  = PatternFill('solid', fgColor='FAFAFA')
C_BAD   = PatternFill('solid', fgColor='FFC7CE')
C_RULE  = PatternFill('solid', fgColor='1F2A44')

_t = Side(style='thin', color='BFBFBF')
_m = Side(style='medium', color='44546A')
BOX  = Border(left=_t, right=_t, top=_t, bottom=_t)
TOPB = Border(left=_t, right=_t, top=_m, bottom=_t)
BOTB = Border(left=_t, right=_t, top=_t, bottom=_m)
CEN  = Alignment(horizontal='center', vertical='center')
RGT  = Alignment(horizontal='right',  vertical='center')
WRAP = Alignment(vertical='top', wrap_text=True)

# (헤더, 폭, 기입완료여부, 정렬)
COLS = [
    ('하위 테마', 12, False, None), ('기업명', 16, True, None), ('코드', 8, True, CEN),
    ('주가', 10, True, RGT), ('시가총액(조)', 11, True, RGT),
    ('지수 비중', 10, True, RGT), ('1주 / 팀예산', 11, True, RGT),
    ('매수 판정', 10, True, CEN),
    ('매출 CAGR(3Y)', 12, False, CEN), ('영업이익률', 10, False, CEN), ('ROE', 9, False, CEN),
    ('PER / PBR', 11, False, CEN), ('주요 제품', 22, False, None),
    ('시장 포지셔닝', 26, False, None), ('투자포인트 / 탈락 사유', 34, False, None),
    ('출처 · 기준일', 18, False, None), ('판정', 9, False, CEN),
]
N = len(COLS)


def put(ws, r, c, v=None, font=BODY, fill=None, align=None, border=BOX, fmt=None):
    cell = ws.cell(row=r, column=c, value=v)
    cell.font = font
    if fill: cell.fill = fill
    if align: cell.alignment = align
    if border: cell.border = border
    if fmt: cell.number_format = fmt
    return cell


def field(ws, r, c, label, value, lw=1, vw=2):
    """라벨 / 값 한 쌍."""
    put(ws, r, c, label, LABEL, C_LABEL, CEN)
    put(ws, r, c + lw, value, BODY, None, CEN)
    if vw > 1:
        ws.merge_cells(start_row=r, start_column=c + lw, end_row=r, end_column=c + lw + vw - 1)
        for k in range(1, vw):
            ws.cell(row=r, column=c + lw + k).border = BOX
    return c + lw + vw


def rule(ws, r):
    for i in range(1, N + 1):
        put(ws, r, i, None, BODY, C_RULE, border=None)
    ws.row_dimensions[r].height = 3


def build_sheet(wb, sec, team, stocks, budget):
    ws = wb.create_sheet(f'{team}_{sec}'[:31].replace('/', '·'))
    ws.sheet_view.showGridLines = False
    for i, (_, wdt, _, _) in enumerate(COLS, 1):
        ws.column_dimensions[get_column_letter(i)].width = wdt

    w = sum(s['w'] for s in stocks)
    ws.cell(row=1, column=1, value=sec).font = TITLE
    ws.row_dimensions[1].height = 22
    c = ws.cell(row=2, column=1, value=f'ICOK Fund 26-2  ·  담당 산업 스크리닝')
    c.font = SUB
    rule(ws, 3)

    nx = field(ws, 4, 1, '팀', f'팀 {team} · {TEAM[team]}', 1, 2)
    nx = field(ws, 4, nx, '담당자', None, 1, 2)
    field(ws, 4, nx, '제출일', None, 1, 2)
    nx = field(ws, 5, 1, '지수 비중', f'{w:.2f}%', 1, 2)
    nx = field(ws, 5, nx, '배정액', f'{w/100*NAV:,.0f}원', 1, 2)
    nx = field(ws, 5, nx, '종목 수', f'{len(stocks)}', 1, 2)
    field(ws, 5, nx, '기준일', ASOF, 1, 2)
    for r in (4, 5):
        ws.row_dimensions[r].height = 17

    r = 7
    if sec in NOTE:
        put(ws, r, 1, NOTE[sec], SUB, None, WRAP, border=None)
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=N)
        ws.row_dimensions[r].height = 15
        r += 1
    put(ws, r, 1, '음영 셀은 기입 완료. 흰색 셀만 작성한다.', SUB, None, None, border=None)
    hr = r + 2

    for i, (h, _, _, _) in enumerate(COLS, 1):
        put(ws, hr, i, h, HEAD, C_HEAD, CEN, TOPB)
    ws.row_dimensions[hr].height = 26
    ws.freeze_panes = ws.cell(row=hr + 1, column=2)

    for j, s in enumerate(sorted(stocks, key=lambda x: -x['w'])):
        row = hr + 1 + j
        last = j == len(stocks) - 1
        one = s['px'] / NAV * 100
        entry = abs((int(s['w'] / one) + 1) * one - s['w'])
        verdict = ('매수 불가' if entry > HARD_CAP else
                   'IC 2/3' if entry > BUDGET_CAP else '가능')
        band = C_BAND if j % 2 else None
        vals = [None, s['name'], s['code'], s['px'], s['mcap'] / 1e6,
                s['w'] / 100, s['px'] / budget, verdict]
        fmts = {4: '#,##0', 5: '0.0', 6: '0.00%', 7: '0.0%'}
        for i, v in enumerate(vals, 1):
            given = COLS[i - 1][2]
            cell = put(ws, row, i, v, BODY, C_GIVEN if given else band,
                       COLS[i - 1][3], BOTB if last else BOX, fmts.get(i))
            if i == 8 and verdict != '가능':
                cell.font, cell.fill = BAD, C_BAD
        for i in range(9, N + 1):
            put(ws, row, i, None, BODY, band, WRAP, BOTB if last else BOX)

    end = hr + len(stocks)
    dv = DataValidation(type='list', formula1='"Top1,Top2,Top3,보류,탈락"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f'{get_column_letter(N)}{hr+1}:{get_column_letter(N)}{end}')

    b = end + 2
    put(ws, b, 1, '선정 결과', HEAD, C_HEAD, None, TOPB)
    for i in range(2, N + 1):
        put(ws, b, i, None, HEAD, C_HEAD, None, TOPB)
    ws.row_dimensions[b].height = 22
    block = [('Top 1', '선정 근거 (컨센서스와의 차이 중심, 2줄)'), ('Top 2', ''), ('Top 3', ''),
             ('탈락 1', '탈락 사유 (해당 지표와 수치를 명시)'), ('탈락 2', ''),
             ('탈락 3', ''), ('탈락 4', ''), ('탈락 5', '')]
    for k, (label, hint) in enumerate(block):
        rr = b + 1 + k
        last = k == len(block) - 1
        bd = BOTB if last else BOX
        put(ws, rr, 1, label, LABEL, C_LABEL, CEN, bd)
        put(ws, rr, 2, None, BODY, None, CEN, bd)
        put(ws, rr, 3, hint or None, SUB if hint else BODY, None, WRAP, bd)
        ws.merge_cells(start_row=rr, start_column=3, end_row=rr, end_column=N)
        for i in range(4, N + 1):
            ws.cell(row=rr, column=i).border = bd
        ws.row_dimensions[rr].height = 19
    return ws


def guide_sheet(wb):
    ws = wb.create_sheet('작성요령')
    ws.sheet_view.showGridLines = False
    ws.column_dimensions['A'].width = 3
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 88
    ws.cell(row=1, column=2, value='담당 산업 스크리닝 작성요령').font = TITLE
    ws.cell(row=2, column=2, value=f'ICOK Fund 26-2  ·  기준일 {ASOF} 종가').font = SUB
    for i in (2, 3):
        put(ws, 3, i, None, BODY, C_RULE, border=None)
    ws.row_dimensions[3].height = 3

    SEC = [
        ('과제 개요', [
            '담당 산업의 전 종목을 검토하여 발제 후보 3종목을 선정한다.',
            '선정한 3종목 중 1종목을 10월 13일 세션에서 발제한다.',
            '선정 근거와 함께 탈락 근거를 반드시 기재한다.',
        ]),
        ('작성 순서', [
            '1.  하위 테마를 2~4개로 분류한다.   예) 에너지 → 태양광 / 풍력 / 원자력 / ESS',
            '2.  매출 CAGR(3년) · 영업이익률 · ROE · PER(또는 PBR)을 기입한다.',
            '3.  주요 제품과 시장 포지셔닝을 각 한 줄로 기입한다.',
            '4.  판정 칸에 Top1~3 / 보류 / 탈락을 선택한다.',
            '5.  시트 하단 「선정 결과」에 Top 3 근거와 탈락 5종목 사유를 기입한다.',
        ]),
        ('기입 완료 항목', [
            '기업명 · 종목코드 · 주가 · 시가총액 · 지수 비중 · 1주가 팀 예산에서 차지하는 비중 · 매수 판정',
            '음영 처리된 셀이며 수정하지 않는다.',
        ]),
        ('지수 비중', [
            'KRX 300 비중은 해당 종목의 중립 비중이다.',
            '예)  비중 0.5% 종목을 1.5% 편입 → 액티브 +1.0%p  /  미편입 → 액티브 −0.5%p',
            '지수 미편입 종목은 중립 비중이 0이므로 편입 시 전량 액티브 포지션으로 기록된다.',
        ]),
        ('매수 판정', [
            '1주 가격이 높아 최소 매수 단위만으로 한도를 초과하는 종목이 있다. 종목 선정 전에 확인한다.',
            '가능 = 팀 재량  /  IC 2/3 = 펀드 IC 특별의결  /  매수 불가 = 1주도 편입 불가',
            '예)  효성중공업 : 지수 비중 0.47%, 1주 2,689,000원 → 1주 매수 시 한도 초과',
        ]),
        ('자료 기준', [
            '모든 수치에 출처와 기준일을 기재한다.',
            '1순위 자료는 DART 사업보고서이며, 증권사 리포트는 참고 자료로만 사용한다.',
        ]),
        ('작성 시 유의사항', [
            '증권사 리포트를 논지의 근거로 사용하지 않는다. 목표주가를 인용하지 않는다.',
            '검증 불가능한 표현(유망하다, 성장성이 크다, 저평가되어 있다 등)을 사용하지 않는다.',
            '수치를 개략값(약 ○조 등)으로 기재하지 않는다.',
        ]),
    ]
    r = 5
    for head, lines in SEC:
        put(ws, r, 2, head, LABEL, C_LABEL, CEN)
        put(ws, r, 3, lines[0], BODY, None, WRAP)
        ws.row_dimensions[r].height = 17
        for ln in lines[1:]:
            r += 1
            put(ws, r, 2, None, BODY, C_LABEL)
            put(ws, r, 3, ln, BODY, None, WRAP)
            ws.row_dimensions[r].height = 17
        ws.merge_cells(start_row=r - len(lines) + 1, start_column=2,
                       end_row=r, end_column=2)
        r += 2
    return ws


def main():
    rows = load(CSV)
    total = sum(float(r[5]) for r in rows)
    smap = build()
    S = {}
    for code, name, close, _, _, mcap in rows:
        if name in MEGA:
            continue
        sec = smap[name]
        if sec == '금융':
            sec = '금융 — 은행·지주' if name in BANK else '금융 — 보험·증권'
        elif sec in ('통신', '미디어·엔터·레저'):
            sec = '통신·미디어·엔터'
        S.setdefault(sec, []).append(
            dict(name=name, code=code, px=float(close),
                 w=float(mcap) / total * 100, mcap=float(mcap)))

    budgets = {t: sum(sum(x['w'] for x in S[k]) for k, v in MANDATE.items() if v == t)
                  / 100 * NAV for t in (1, 2, 3)}
    wb = Workbook(); wb.remove(wb.active)
    guide_sheet(wb)
    for t in (1, 2, 3):
        for sec in [k for k, v in MANDATE.items() if v == t]:
            build_sheet(wb, sec, t, S[sec], budgets[t])
    wb.save(OUT)
    print(f'저장: {OUT}  (시트 {len(wb.sheetnames)}개)')


if __name__ == '__main__':
    main()
