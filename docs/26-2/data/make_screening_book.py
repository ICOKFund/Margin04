# -*- coding: utf-8 -*-
"""담당 산업 스크리닝 워크북 생성 — 기계적 항목은 미리 채우고 판단 칼럼만 비운다.

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
TIP = {
    '반도체·소부장': '41종목으로 가장 많습니다. 전공정(장비·소재)과 후공정(기판·테스트·패키징) '
                  '둘로 나눠 2명이 맡는 것을 권장합니다.',
    '지주(반도체 프록시)': 'SK스퀘어 1종목뿐입니다. SK하이닉스 룩스루가 1.8배라 1주만 사도 펀드 전체의 '
                     'SKH 노출이 크게 움직입니다. 팀장이 직접 관리합니다.',
    '헬스케어·바이오': '44종목 중 상당수가 매출이 없는 임상 단계 회사입니다. 매출·영업이익률·PER이 '
                  '산출되지 않는 회사는 하위테마를 「파이프라인」으로 표기하고 별도로 다룹니다.',
    '금융 — 은행·지주': '은행은 매출·영업이익률 대신 NIM·대손비용률·CET1·주주환원율을 씁니다. '
                   '밸류에이션은 PER이 아니라 PBR-ROE로 봅니다.',
    '금융 — 보험·증권': '보험은 IFRS17 기준이라 CSM·보험계약마진을 봐야 합니다. 어려우면 증권부터 '
                   '보고 보험은 팀장과 상의하세요.',
}

HEAD = Font(name='맑은 고딕', size=9, bold=True, color='FFFFFF')
BODY = Font(name='맑은 고딕', size=9)
BOLD = Font(name='맑은 고딕', size=9, bold=True)
TITLE = Font(name='맑은 고딕', size=14, bold=True)
GREY = Font(name='맑은 고딕', size=9, color='777777')
FILL_H = PatternFill('solid', fgColor='2F3C7E')
FILL_GIVEN = PatternFill('solid', fgColor='EDEDED')
FILL_WRITE = PatternFill('solid', fgColor='FFFFFF')
FILL_NOTE = PatternFill('solid', fgColor='FFF8E1')
THIN = Side(style='thin', color='BFBFBF')
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
CEN = Alignment(horizontal='center', vertical='center')
WRAP = Alignment(vertical='top', wrap_text=True)

# (헤더, 폭, 채움여부)
COLS = [
    ('하위 테마', 12, False), ('기업명', 16, True), ('코드', 8, True),
    ('주가', 11, True), ('시총(조)', 9, True), ('KRX300 비중', 11, True),
    ('1주=팀예산', 11, True), ('매수 판정', 11, True),
    ('3년 매출CAGR', 12, False), ('영업이익률', 10, False), ('ROE', 9, False),
    ('PER / PBR', 11, False), ('주요 제품', 22, False), ('시장 포지셔닝', 26, False),
    ('투자포인트 / 탈락 사유', 34, False), ('출처 · 기준일', 18, False),
    ('판정', 10, False),
]


def put(ws, r, c, v, font=BODY, fill=None, align=None, border=True, fmt=None):
    cell = ws.cell(row=r, column=c, value=v)
    cell.font = font
    if fill: cell.fill = fill
    if align: cell.alignment = align
    if border: cell.border = BOX
    if fmt: cell.number_format = fmt
    return cell


def build_sheet(wb, sec, team, stocks, budget):
    ws = wb.create_sheet(f'{team}_{sec}'[:31].replace('/', '·'))
    ws.sheet_view.showGridLines = False
    ws.freeze_panes = 'B9'

    ws.cell(row=1, column=1, value=f'{sec}').font = TITLE
    ws.cell(row=2, column=1,
            value=f'팀 {team} · {TEAM[team]}   |   담당자: ____________   |   '
                  f'제출: 세션 전날 자정   |   기준일 {ASOF} 종가').font = GREY
    w = sum(s['w'] for s in stocks)
    ws.cell(row=3, column=1,
            value=f'이 산업의 벤치마크 비중 {w:.2f}%  =  배정액 {w/100*NAV:,.0f}원   |   '
                  f'{len(stocks)}종목   |   팀 예산 {budget:,.0f}원').font = BOLD

    note = TIP.get(sec)
    r = 5
    if note:
        c = put(ws, r, 1, '※ ' + note, GREY, FILL_NOTE, WRAP, border=False)
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=len(COLS))
        ws.row_dimensions[r].height = 30
        r += 2
    else:
        r = 6

    put(ws, r, 1, '회색 칸은 채워져 있습니다. 흰 칸만 작성하세요.  '
                  '모든 숫자에 출처와 기준일을 답니다 — DART 사업보고서가 1순위입니다.  '
                  '증권사 리포트를 논지의 근거로 쓰지 않습니다.',
        GREY, None, WRAP, border=False)
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=len(COLS))
    hr = r + 2

    for i, (h, wdt, _) in enumerate(COLS, 1):
        put(ws, hr, i, h, HEAD, FILL_H, CEN)
        ws.column_dimensions[get_column_letter(i)].width = wdt
    ws.row_dimensions[hr].height = 24

    for j, s in enumerate(sorted(stocks, key=lambda x: -x['w'])):
        row = hr + 1 + j
        one = s['px'] / NAV * 100
        entry = abs((int(s['w'] / one) + 1) * one - s['w'])
        verdict = ('매수 불가' if entry > HARD_CAP else
                   'IC 2/3' if entry > BUDGET_CAP else '가능')
        vals = [None, s['name'], s['code'], s['px'], round(s['mcap'] / 1e6, 1),
                s['w'] / 100, s['px'] / budget, verdict]
        for i, v in enumerate(vals, 1):
            given = COLS[i - 1][2]
            cell = put(ws, row, i, v, BODY, FILL_GIVEN if given else FILL_WRITE,
                       CEN if i in (3, 8) else None)
            if i == 4: cell.number_format = '#,##0'
            if i == 5: cell.number_format = '0.0'
            if i in (6, 7): cell.number_format = '0.00%'
            if i == 8 and verdict != '가능':
                cell.font = Font(name='맑은 고딕', size=9, bold=True, color='990011')
        for i in range(9, len(COLS) + 1):
            put(ws, row, i, None, BODY, FILL_WRITE, WRAP)

    last = hr + len(stocks)
    dv = DataValidation(type='list', formula1='"Top1,Top2,Top3,보류,탈락"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f'Q{hr+1}:Q{last}')

    # 하단 결론 블록
    b = last + 2
    put(ws, b, 1, '결론 — 위 표를 채운 다음 작성합니다', BOLD, None, None, border=False)
    rows = [
        ('Top 1', '선정 근거 2줄 — 컨센서스와 무엇이 다른가'),
        ('Top 2', ''), ('Top 3', ''),
        ('탈락 1', '뺀 이유 한 줄 — "지표가 나빠서"는 사유가 아니다. 어떤 지표가 왜 나쁜지 쓴다'),
        ('탈락 2', ''), ('탈락 3', ''), ('탈락 4', ''), ('탈락 5', ''),
    ]
    for k, (label, hint) in enumerate(rows):
        rr = b + 1 + k
        put(ws, rr, 1, label, BOLD, FILL_GIVEN, CEN)
        put(ws, rr, 2, None, BODY, FILL_WRITE, CEN)
        put(ws, rr, 3, hint or None, GREY if hint else BODY, FILL_WRITE, WRAP)
        ws.merge_cells(start_row=rr, start_column=3, end_row=rr, end_column=len(COLS))
        ws.row_dimensions[rr].height = 20
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

    wb = Workbook()
    wb.remove(wb.active)

    gd = wb.create_sheet('0_작성요령')
    gd.sheet_view.showGridLines = False
    gd.column_dimensions['A'].width = 4
    gd.column_dimensions['B'].width = 104
    gd.cell(row=1, column=2, value='담당 산업 스크리닝 — 작성 요령').font = TITLE
    lines = [
        ('', ''),
        ('무엇을 하는 과제인가', 'h'),
        ('담당 산업의 전 종목을 훑고, 발제할 만한 3종목까지 좁힌다. '
         '여기서 고른 3종목 중 하나를 10월 13일에 발제한다.', ''),
        ('스크리닝은 고르는 작업이 아니라 떨어뜨리는 작업이다. '
         '전 종목에 좋은 이야기만 적혀 있으면 그것은 종목 소개서지 스크리닝이 아니다.', ''),
        ('', ''),
        ('작성 순서', 'h'),
        ('1.  하위 테마를 먼저 나눈다 — 산업을 통째로 보지 말고 2~4개 갈래로 쪼갠다.', ''),
        ('     예: 에너지 → 태양광 / 풍력 / 원자력 / ESS    조선 → 상선 / 특수선 / 기자재', ''),
        ('2.  숫자 칸을 채운다 — 3년 매출 CAGR · 영업이익률 · ROE · PER(또는 PBR).', ''),
        ('     모든 숫자에 출처와 기준일을 단다. DART 사업보고서가 1순위, 증권사 리포트는 참고만.', ''),
        ('3.  주요 제품과 시장 포지셔닝을 한 줄씩 쓴다 — 무엇을 팔아 돈을 버는가.', ''),
        ('4.  판정 칸에 Top1~3 / 보류 / 탈락을 고른다.', ''),
        ('5.  맨 아래 결론 블록에 Top 3 근거와 탈락 5종목의 사유를 쓴다.', ''),
        ('', ''),
        ('이미 채워져 있는 것 (회색 칸)', 'h'),
        ('기업명 · 코드 · 주가 · 시총 · KRX300 비중 · 1주가 팀 예산에서 차지하는 비중 · 매수 판정', ''),
        ('찾는 데 시간 쓰지 말고 판단하는 데 쓰라고 미리 넣었다. 기준일은 ' + ASOF + ' 종가다.', ''),
        ('', ''),
        ('KRX300 비중이 왜 중요한가', 'h'),
        ('그 종목의 KRX300 비중이 곧 우리의 중립 비중이다. 아무 판단도 하지 않으면 그만큼 들고 있는 것이다.', ''),
        ('비중 0.5%인 종목을 1.5% 담으면 +1.0%p 액티브 베팅이고, 안 담으면 −0.5%p 숏이다.', ''),
        ('지수에 없는 종목은 중립이 0이므로 1주만 사도 100% 액티브 베팅이 된다. 금지는 아니지만 알고 사야 한다.', ''),
        ('', ''),
        ('매수 판정 — 분석하기 전에 먼저 본다', 'h'),
        ('1주 가격이 너무 높아 중립을 넘겨버리는 종목이 있다. 4주 분석하고 못 사면 전부 버리게 된다.', ''),
        ('「가능」 = 팀 재량   「IC 2/3」 = 펀드 IC 특별의결 필요   「매수 불가」 = 1주도 살 수 없다', ''),
        ('실제 사례 — 효성중공업은 KRX300 비중이 0.47%인데 1주가 268만원이라 1주만 사도 한도를 넘는다.', ''),
        ('', ''),
        ('하지 말 것', 'h'),
        ('증권사 리포트를 논지의 근거로 쓰지 않는다. 목표주가를 인용하지 않는다.', ''),
        ('「유망하다 · 성장성이 크다 · 저평가되어 있다」처럼 검증할 수 없는 말을 쓰지 않는다.', ''),
        ('숫자를 「약 ~조」로 뭉개지 않는다. 출처와 기준일이 없으면 틀려도 아무도 못 잡는다.', ''),
    ]
    r = 2
    for text, kind in lines:
        if not text:
            r += 1; continue
        c = gd.cell(row=r, column=2, value=text)
        c.font = BOLD if kind == 'h' else BODY
        c.alignment = WRAP
        if kind == 'h':
            c.fill = FILL_GIVEN
        r += 1

    for t in (1, 2, 3):
        for sec in [k for k, v in MANDATE.items() if v == t]:
            build_sheet(wb, sec, t, S[sec], budgets[t])

    wb.save(OUT)
    print(f'저장: {OUT}  (시트 {len(wb.sheetnames)}개)')
    for t in (1, 2, 3):
        ks = [k for k, v in MANDATE.items() if v == t]
        print(f'  팀{t} {TEAM[t]}: {len(ks)}개 산업, 예산 {budgets[t]:,.0f}원')


if __name__ == '__main__':
    main()
