# -*- coding: utf-8 -*-
"""KRX 300 비중 산출 — 시장·집중도·섹터·팀 예산·정수주 제약.

사용: python3 weights.py [CSV] [NAV]
예:   python3 weights.py krx300_constituents_20260915.csv 28000000

원자료 CSV는 KRX 정보데이터시스템 지수구성종목 다운로드 형식
(종목코드, 종목명, 종가, 대비, 등락률, 상장시가총액). 인코딩은 UTF-8/CP949 자동 판별.
"""
import csv, io, sys
from sector_map import build, MEGA

CSV = sys.argv[1] if len(sys.argv) > 1 else 'krx300_constituents_20260915.csv'
NAV = float(sys.argv[2]) if len(sys.argv) > 2 else 28_000_000

MANDATE = {
    '반도체·소부장': 1, 'IT하드웨어·부품': 1, '소프트웨어·인터넷·게임': 1,
    '지주(반도체 프록시)': 1, '2차전지·소재': 1, '자동차·부품': 1,
    '조선·기자재': 2, '방산·우주': 2, '전력기기·유틸리티': 2,
    '기계·건설·로봇': 2, '소재·화학·철강': 2, '에너지·상사·운송': 2,
    '헬스케어·바이오': 3, '소비재·유통': 3,
}
# 팀 3은 금융을 은행·지주 / 보험·증권으로 쪼개고 통신+미디어를 묶는다 (09 §6)
BANK = set('KB금융 신한지주 하나금융지주 우리금융지주 기업은행 BNK금융지주 '
           'JB금융지주 iM금융지주 카카오뱅크'.split())
TEAM = {1: '테크·전동화', 2: '중후장대·인프라', 3: '내수·디펜시브'}
HARD_CAP = 8.0      # 진입틸트 8%p 초과 = 매수 불가
TEAM_BUDGET = 6.0   # 팀 액티브 예산 ±6%p


def load(fn):
    for enc in ('utf-8-sig', 'cp949'):
        try:
            rows = list(csv.reader(io.StringIO(open(fn, encoding=enc).read())))[1:]
            return [r for r in rows if r and r[0]]
        except UnicodeDecodeError:
            continue
    raise SystemExit(f'{fn} 인코딩 판별 실패')


def main():
    rows = load(CSV)
    total = sum(float(r[5]) for r in rows)
    smap = build()

    stocks, unmapped = [], []
    for code, name, close, _, chg, mcap in rows:
        w = float(mcap) / total * 100
        sec = '__MEGA__' if name in MEGA else smap.get(name)
        if sec is None:
            unmapped.append(name); sec = '미분류'
        stocks.append(dict(name=name, px=float(close), w=w, sec=sec, chg=float(chg)))
    if unmapped:
        print(f'!! 섹터 미분류 {len(unmapped)}종목: {unmapped}\n')

    # 팀 3 금융 분할 · 통신+미디어 병합
    for s in stocks:
        if s['sec'] == '금융':
            s['sec'] = '금융 — 은행·지주' if s['name'] in BANK else '금융 — 보험·증권'
        elif s['sec'] in ('통신', '미디어·엔터·레저'):
            s['sec'] = '통신·미디어·엔터'
    for k in ('금융 — 은행·지주', '금융 — 보험·증권', '통신·미디어·엔터'):
        MANDATE[k] = 3

    mega = [s for s in stocks if s['sec'] == '__MEGA__']
    mega_w = sum(s['w'] for s in mega)
    univ_w = 100 - mega_w

    print(f'{"="*92}\nKRX 300 비중 산출 — {CSV}  ·  NAV {NAV:,.0f}원  ·  {len(stocks)}종목')
    print('='*92)
    print(f'\n[메가캡] 펀드 IC 관할')
    for s in mega:
        need = s['w'] / (s['px'] / NAV * 100)
        print(f'  {s["name"]:<12s}{s["px"]:>10,.0f}원  {s["w"]:>6.2f}%  '
              f'{s["w"]/100*NAV:>11,.0f}원  중립 {need:>4.1f}주')
    print(f'  {"합계":<12s}{"":>11s}  {mega_w:>6.2f}%  {mega_w/100*NAV:>11,.0f}원')
    print(f'\n[팀 유니버스] {len(stocks)-2}종목  {univ_w:.2f}%  {univ_w/100*NAV:,.0f}원')

    # 집중도
    top = sorted(stocks, key=lambda s: -s['w'])
    print(f'\n[집중도]')
    print(f'  상위 3종목  {sum(s["w"] for s in top[:3]):>6.2f}%   '
          f'상위 10종목 {sum(s["w"] for s in top[:10]):>6.2f}%   '
          f'하위 200종목 {sum(s["w"] for s in top[-200:]):>5.2f}%')

    # 섹터 집계
    secs = {}
    for s in stocks:
        if s['sec'] == '__MEGA__':
            continue
        secs.setdefault(s['sec'], []).append(s)

    print(f'\n{"="*92}\n[팀별 담당 산업]  팀 예산 = 담당 산업 BM비중 합 × NAV')
    for t in (1, 2, 3):
        ss = sorted([k for k, v in MANDATE.items() if v == t],
                    key=lambda k: -sum(x['w'] for x in secs[k]))
        bw = sum(sum(x['w'] for x in secs[k]) for k in ss)
        print(f'\n■ 팀 {t} · {TEAM[t]}   {bw:.2f}%   {bw/100*NAV:,.0f}원')
        print(f'  {"담당 산업":<20s}{"BM비중":>7s}{"배정액":>12s}{"종목":>5s}'
              f'{"매수불가":>7s}{"최저가":>10s}  대표 종목')
        for k in ss:
            v = sorted(secs[k], key=lambda x: -x['w'])
            w = sum(x['w'] for x in v)
            no = 0
            for x in v:
                one = x['px'] / NAV * 100
                if abs((int(x['w']/one)+1)*one - x['w']) > HARD_CAP:
                    no += 1
            print(f'  {k:<20s}{w:>6.2f}%{w/100*NAV:>11,.0f}원{len(v):>5d}{no:>7d}'
                  f'{min(x["px"] for x in v):>9,.0f}원  '
                  + ', '.join(x['name'] for x in v[:4]))

    # 매수 불가 종목
    print(f'\n{"="*92}\n[매수 불가 종목]  1주 진입틸트 > {HARD_CAP}%p')
    print(f'  {"종목":<16s}{"팀":>3s}{"주가":>12s}{"BM비중":>8s}{"1주=NAV":>9s}{"진입틸트":>10s}')
    found = False
    for s in sorted(stocks, key=lambda x: -x['px']):
        if s['sec'] in ('__MEGA__', '미분류'):
            continue
        one = s['px'] / NAV * 100
        entry = abs((int(s['w']/one)+1)*one - s['w'])
        if entry > HARD_CAP:
            found = True
            print(f'  {s["name"]:<16s}{MANDATE.get(s["sec"],"?"):>3}{s["px"]:>11,.0f}원'
                  f'{s["w"]:>7.2f}%{one:>8.2f}%{entry:>+9.2f}%p')
    if not found:
        print('  없음')


if __name__ == '__main__':
    main()
