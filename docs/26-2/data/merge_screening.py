# -*- coding: utf-8 -*-
"""팀원이 제출한 스크리닝 파일을 팀 단위 한 파일로 취합한다.

각자 19시트 전체를 반환하므로 실제 작성한 시트만 뽑아 붙인다.
사용: python3 merge_screening.py <팀번호>
"""
import sys, json
from copy import copy
from openpyxl import load_workbook, Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter

UP = '/root/.claude/uploads/f0fae95f-39d4-5984-93ce-cf5a0635b8ac'
ASOF, MERGED = '2026-09-15', '2026-09-22'

# 팀 → [(출력 시트명, 원본 파일, 원본 시트, 담당자)]  담당자 None = 원본 기재값 사용
TEAMS = {
 1: ('테크·전동화', '배준서', [
    ('반도체·소부장',        '1e838a93-ICOK___________1___.xlsx', '1_반도체·소부장',        None),
    ('자동차·부품',          '1e838a93-ICOK___________1___.xlsx', '1_자동차·부품',          None),
    ('2차전지·소재',         '1e838a93-ICOK___________1___.xlsx', '1_2차전지·소재',         '배준서'),
    ('소프트웨어·인터넷·게임',  '1e838a93-ICOK___________1___.xlsx', '1_소프트웨어·인터넷·게임',  '배준서'),
    ('IT하드웨어·부품',       '1e838a93-ICOK___________1___.xlsx', '1_IT하드웨어·부품',       None),
    ('지주 — 테크·전동화',    'e0616c10-ICOK__________.xlsx',      '1_지주 — 테크·전동화',    '이재우 (팀 2 팀장)'),
 ]),
 2: ('중후장대·인프라', '이재우', [
    ('전력기기·유틸리티',     'e027218b-___ICOK______________.xlsx',       '2_전력기기·유틸리티',   '권나영'),
    ('조선·기자재',          '36589c84-ICOK________________________-1.xlsx','2_조선·기자재',      '이준성'),
    ('기계·건설·로봇',        '2439e087-____ICOK__________.xlsx',          '2_기계·건설·로봇',     '김범준'),
    ('방산·우주',            '1e838a93-ICOK___________1___.xlsx',         '2_방산·우주',          '심규환'),
    ('소재·에너지',          'da57c2cd-ICOK______________.xlsx',          '2_소재·에너지',        '권민재'),
    ('지주 — 산업재·인프라',   'e0616c10-ICOK__________.xlsx',              '2_지주 — 산업재·인프라','이재우'),
 ]),
}
GUIDE = ('e0616c10-ICOK__________.xlsx', '작성요령')

F = '맑은 고딕'
TITLE = Font(name=F, size=15, bold=True, color='1F2A44'); SUB = Font(name=F, size=9, color='5A5A5A')
HEAD  = Font(name=F, size=9, bold=True, color='FFFFFF');  LABEL = Font(name=F, size=9, bold=True, color='1F2A44')
BODY  = Font(name=F, size=9); BOLD = Font(name=F, size=9, bold=True)
BAD   = Font(name=F, size=9, bold=True, color='9C0006')
C_HEAD = PatternFill('solid', fgColor='44546A'); C_BAND = PatternFill('solid', fgColor='FAFAFA')
C_BAD  = PatternFill('solid', fgColor='FFC7CE'); C_RULE = PatternFill('solid', fgColor='1F2A44')
_t = Side(style='thin', color='BFBFBF'); _m = Side(style='medium', color='44546A')
BOX  = Border(left=_t, right=_t, top=_t, bottom=_t)
TOPB = Border(left=_t, right=_t, top=_m, bottom=_t); BOTB = Border(left=_t, right=_t, top=_t, bottom=_m)
CEN = Alignment(horizontal='center', vertical='center')
RGT = Alignment(horizontal='right', vertical='center')
WRAP = Alignment(vertical='top', wrap_text=True)


def clone(src, wb, title):
    d = wb.create_sheet(title[:31])
    for row in src.iter_rows():
        for c in row:
            t = d.cell(row=c.row, column=c.column, value=c.value)
            if c.has_style:
                t.font = copy(c.font); t.fill = copy(c.fill); t.border = copy(c.border)
                t.alignment = copy(c.alignment); t.number_format = c.number_format
    for k, v in src.column_dimensions.items():
        d.column_dimensions[k].width = v.width; d.column_dimensions[k].hidden = v.hidden
    for k, v in src.row_dimensions.items():
        d.row_dimensions[k].height = v.height
    for m in list(src.merged_cells.ranges):
        d.merge_cells(str(m))
    d.freeze_panes = src.freeze_panes
    d.sheet_view.showGridLines = src.sheet_view.showGridLines
    for dv in src.data_validations.dataValidation:
        n = DataValidation(type=dv.type, formula1=dv.formula1, allow_blank=dv.allow_blank)
        d.add_data_validation(n)
        for rng in dv.sqref.ranges:
            n.add(str(rng))
    return d


def scan(ws):
    """시트에서 담당자·BM비중·종목수·Top3·탈락수·미판정수·종목정보를 뽑는다."""
    hr = next(r for r in range(1, 15) if ws.cell(row=r, column=2).value == '기업명')
    px, judged = {}, 0
    r = hr + 1
    while r <= ws.max_row:
        a = str(ws.cell(row=r, column=1).value or ''); b = ws.cell(row=r, column=2).value
        if a.startswith(('Top', '탈락')) or not b:
            break
        px[b] = (ws.cell(row=r, column=4).value, ws.cell(row=r, column=8).value,
                 ws.cell(row=r, column=7).value)
        if ws.cell(row=r, column=17).value:
            judged += 1
        r += 1
    tops, drops = [], 0
    for r in range(r, ws.max_row + 1):
        a = str(ws.cell(row=r, column=1).value or ''); b = ws.cell(row=r, column=2).value
        if a.startswith('Top') and b: tops.append(b)
        elif a.startswith('탈락') and b: drops += 1
    return dict(who=ws.cell(row=4, column=5).value, bw=ws.cell(row=5, column=2).value,
                n=len(px), tops=tops, drops=drops, judged=judged, px=px, hr=hr)


def summary(wb, team, tname, lead, rows, notes):
    ws = wb.create_sheet('취합', 0); ws.sheet_view.showGridLines = False
    for i, w in enumerate((3, 21, 17, 9, 8, 16, 16, 16, 7, 11), 1):
        ws.column_dimensions[get_column_letter(i)].width = w

    def put(r, c, v=None, f=BODY, fi=None, al=None, bd=BOX):
        x = ws.cell(row=r, column=c, value=v); x.font = f
        if fi: x.fill = fi
        if al: x.alignment = al
        if bd: x.border = bd
        return x

    ws.cell(row=1, column=2, value=f'팀 {team} · {tname} — 담당 산업 스크리닝 취합').font = TITLE
    ws.row_dimensions[1].height = 22
    ws.cell(row=2, column=2,
            value=f'ICOK Fund 26-2  ·  기준일 {ASOF} 종가  ·  취합 {MERGED}  ·  팀장 {lead}').font = SUB
    for i in range(2, 11): put(3, i, None, BODY, C_RULE, bd=None)
    ws.row_dimensions[3].height = 3

    r = 5
    for i, h in enumerate(('담당 산업', '담당자', 'BM비중', '종목수',
                           'Top 1', 'Top 2', 'Top 3', '탈락', '상태'), 2):
        put(r, i, h, HEAD, C_HEAD, CEN, TOPB)
    ws.row_dimensions[r].height = 22

    cand, done = [], 0
    for j, (title, s) in enumerate(rows):
        r += 1; last = j == len(rows) - 1; bd = BOTB if last else BOX
        ok = len(s['tops']) == 3
        done += ok
        band = C_BAND if j % 2 else None
        put(r, 2, title, BOLD, band, None, bd)
        put(r, 3, s['who'] or '미기재', BODY if s['who'] else BAD,
            band if s['who'] else C_BAD, CEN, bd)
        put(r, 4, s['bw'], BODY, band, CEN, bd)
        put(r, 5, s['n'], BODY, band, CEN, bd)
        for k in range(3):
            put(r, 6 + k, s['tops'][k] if k < len(s['tops']) else None, BODY, band, CEN, bd)
        put(r, 9, s['drops'] or None, BODY, band, CEN, bd)
        st = '제출' if ok else (f"Top {len(s['tops'])}개" if s['tops'] else '선정 결과 없음')
        put(r, 10, st, BODY if ok else BAD, band if ok else C_BAD, CEN, bd)
        ws.row_dimensions[r].height = 18
        for nm in s['tops']:
            cand.append((title, s['who'], nm) + s['px'].get(nm, (None, None, None)))

    r += 2
    ws.cell(row=r, column=2, value=f'발제 후보 {len(cand)}종목 — 매수 가능 여부').font = LABEL
    r += 1
    for i, h in enumerate(('담당 산업', '담당자', '종목', '주가', '1주 / 팀예산', '매수 판정'), 2):
        put(r, i, h, HEAD, C_HEAD, CEN, TOPB)
    ws.row_dimensions[r].height = 22
    blocked = 0
    for j, (t, who, nm, p, v, ratio) in enumerate(cand):
        r += 1; last = j == len(cand) - 1; bd = BOTB if last else BOX
        band = C_BAND if j % 2 else None
        put(r, 2, t, BODY, band, None, bd); put(r, 3, who or '미기재', BODY, band, CEN, bd)
        put(r, 4, nm, BOLD, band, None, bd)
        put(r, 5, p, BODY, band, RGT, bd).number_format = '#,##0'
        put(r, 6, ratio, BODY, band, RGT, bd).number_format = '0.0%'
        bad = v and v != '가능'
        put(r, 7, v, BAD if bad else BODY, C_BAD if bad else band, CEN, bd)
        blocked += bool(bad)
        ws.row_dimensions[r].height = 17

    r += 2
    for ln, st in notes(done, len(rows), cand, blocked):
        c = ws.cell(row=r, column=2, value=ln); c.font = st; c.alignment = WRAP
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=10)
        ws.row_dimensions[r].height = 16; r += 1
    return done, cand, blocked


NOTES = {
 1: lambda d, n, c, b: [
    (f'완료 {d}/{n}.  반도체·소부장(박채현)은 38종목 전 항목을 채웠으나 판정과 선정 결과가 비어 있다. '
     '2차전지·소재도 같다. 데이터는 있고 결론이 없으므로 Top 3와 탈락 5만 채우면 끝난다.', BAD),
    ('소프트웨어·인터넷·게임은 Top 2종목까지만 기재됐다. Top 3을 채운다.', BAD),
    ('배준서 팀장이 2차전지·소재와 소프트웨어·인터넷·게임 2개를 겸임한다. 지주는 팀 2 팀장이 맡았으므로 '
     '담당 산업 6개에 팀 1 인원은 4명이다. 1인 1산업 전제가 성립하지 않는다.', BAD),
    ('「지주 — 테크·전동화」는 팀 2 팀장(이재우)이 작성한 것이다. 팀 1 담당자 작업과 중복이면 하나를 택한다.', BODY),
    ('방산·우주 시트가 이 팀 파일에 작성돼 있었다. 팀 2 맨데이트이므로 팀 2 취합본으로 옮겼다.', BODY),
    ('IT하드웨어·부품은 판정 칸에 드롭다운 대신 자유 입력("선정 (Top 1)" 등)을 썼다. 집계 시 주의한다.', SUB),
 ],
 2: lambda d, n, c, b: [
    (f'완료 {d}/{n}.  방산·우주(심규환)는 팀 1 정리본에 작성돼 있어 여기로 옮겼다.', BODY),
    ('방산·우주는 8종목 중 6종목만 판정했다(Top 3 · 보류 2 · 탈락 1). STX엔진·쎄트렉아이와 탈락 사유를 채운다.', BAD),
    ('방산·우주의 한국항공우주 탈락 사유가 "증권사 제시 목표가에 근접"이다. 과제 규칙상 목표주가는 근거로 쓸 수 없다. ROE·영업이익률 등 재무 근거로 다시 쓴다.', BAD),
    (f'발제 후보 {len(c)}종목 중 매수 제약에 걸리는 종목은 {b}종목이다.', BODY),
    ('HD현대일렉트릭은 1주 70만원이 팀 예산의 14.8%다. 편입 시 나머지 후보의 자리를 먼저 계산한다.', BODY),
    ('조선·기자재는 HD현대마린솔루션 탈락 사유를 업종 평균 PER·PBR 대비 배수로 다시 쓴 수정본을 반영했다.', SUB),
    ('원본 파일은 각자 19시트 전체를 반환했다. 이 파일은 팀 담당 6시트와 작성요령만 남긴 것이다.', SUB),
 ],
}


def main():
    team = int(sys.argv[1])
    tname, lead, specs = TEAMS[team]
    wb = Workbook(); wb.remove(wb.active)
    clone(load_workbook(f'{UP}/{GUIDE[0]}')[GUIDE[1]], wb, '작성요령')
    rows = []
    for title, f, sheet, who in specs:
        d = clone(load_workbook(f'{UP}/{f}')[sheet], wb, title)
        if who and not d.cell(row=4, column=5).value:
            d.cell(row=4, column=5, value=who)
        rows.append((title, scan(d)))
    done, cand, blocked = summary(wb, team, tname, lead, rows, NOTES[team])
    out = f'ICOK_{team}팀_담당산업_스크리닝.xlsx'
    wb.save(out)
    print(f'저장: {out}  시트 {len(wb.sheetnames)}개  완료 {done}/{len(rows)}  '
          f'후보 {len(cand)}종목 (제약 {blocked})')
    for t, s in rows:
        print(f'   {t:22s}{str(s["who"] or "미기재"):18s}{s["n"]:3d}종목  '
              f'판정 {s["judged"]:2d}  Top {len(s["tops"])}  탈락 {s["drops"]}')


if __name__ == '__main__':
    main()
