# -*- coding: utf-8 -*-
"""KRX 300 섹터별 비중 산출 → 3팀 맨데이트 배분 검증.

사용: python3 analyze_sectors.py [NAV]   (기본 26,000,000)
"""
import csv, io, sys
from sector_map import build, MEGA

NAV = float(sys.argv[1]) if len(sys.argv) > 1 else 26_000_000
TEAMS = 3
SLEEVE = NAV / TEAMS

CSV = 'krx300_constituents_20260727.csv'

# 3팀 맨데이트 — 섹터 → 팀
MANDATE = {
    # 팀 1 · 전자·전동화 수출 밸류체인
    '반도체·소부장': 1, 'IT하드웨어·부품': 1, '소프트웨어·인터넷·게임': 1,
    '지주(반도체 프록시)': 1, '2차전지·소재': 1, '자동차·부품': 1,

    # 팀 2 · 중후장대·인프라 (자본재 사이클)
    '조선·기자재': 2, '방산·우주': 2, '전력기기·유틸리티': 2,
    '기계·건설·로봇': 2, '소재·화학·철강': 2, '에너지·상사·운송': 2,

    # 팀 3 · 내수·디펜시브 (금리·내수경기)
    '금융': 3, '헬스케어·바이오': 3, '소비재·유통': 3, '통신': 3, '미디어·엔터·레저': 3,
}
TEAM_NAME = {1: '테크·전동화', 2: '중후장대·인프라', 3: '내수·디펜시브'}

HARD_CAP = 8.0          # 진입틸트 8%p 초과 = 매수 불가 (08 기준)
TEAM_BUDGET = 6.0       # 팀 액티브 예산 ±6%p


def main():
    raw = open(CSV, encoding='euc-kr').read()
    rows = list(csv.reader(io.StringIO(raw)))[1:]
    total = sum(float(r[5]) for r in rows)
    smap = build()

    stocks, unmapped = [], []
    for code, name, close, _, _, mcap in rows:
        w = float(mcap) / total * 100
        if name in MEGA:
            sec = '__MEGA__'
        else:
            sec = smap.get(name)
            if sec is None:
                unmapped.append((name, w)); sec = '미분류'
        stocks.append(dict(code=code, name=name, price=float(close), w=w, sec=sec))

    if unmapped:
        print('!! 미분류 종목:', unmapped)

    mega_w = sum(s['w'] for s in stocks if s['sec'] == '__MEGA__')
    univ_w = 100 - mega_w

    # --- 섹터별 ---
    secs = {}
    for s in stocks:
        if s['sec'] == '__MEGA__':
            continue
        d = secs.setdefault(s['sec'], dict(w=0.0, n=0, top=[]))
        d['w'] += s['w']; d['n'] += 1; d['top'].append(s)

    px = {s['name']: s['price'] for s in stocks}
    mega_cost = 10 * px['삼성전자'] + 1 * px['SK하이닉스']
    usable = SLEEVE - mega_cost
    usable_pct = usable / NAV * 100
    print(f'\nNAV {NAV:,.0f}원 · 팀 슬리브 {SLEEVE:,.0f}원 · 팀당 운용가능 {usable:,.0f}원')
    print(f'메가캡(삼성전자+SKH) {mega_w:.2f}%  ·  팀 유니버스 298종목 {univ_w:.2f}%')
    print(f'팀당 중립 목표 = {univ_w/TEAMS:.2f}%  (= 유니버스 ÷ 3)\n')

    print(f'{"섹터":<24s}{"종목":>4s}{"BM비중":>9s}{"유니버스내":>10s}{"NAV환산":>12s}  팀  대표 3종목')
    print('-' * 118)
    for sec, d in sorted(secs.items(), key=lambda kv: -kv[1]['w']):
        d['top'].sort(key=lambda s: -s['w'])
        top3 = ', '.join(s['name'] for s in d['top'][:3])
        t = MANDATE.get(sec, '?')
        print(f'{sec:<24s}{d["n"]:>4d}{d["w"]:>8.2f}%{d["w"]/univ_w*100:>9.1f}%'
              f'{d["w"]/100*NAV:>11,.0f}원  {t}  {top3}')

    # --- 팀별 집계 ---
    print('\n' + '=' * 118)
    print(f'{"팀":<20s}{"섹터수":>6s}{"종목수":>6s}{"중립비중":>10s}{"목표대비":>10s}'
          f'{"NAV환산":>13s}{"운용가능액대비":>14s}')
    print('-' * 118)
    target = univ_w / TEAMS
    for t in (1, 2, 3):
        ss = [k for k, v in MANDATE.items() if v == t]
        w = sum(secs[k]['w'] for k in ss if k in secs)
        n = sum(secs[k]['n'] for k in ss if k in secs)
        print(f'{t}. {TEAM_NAME[t]:<17s}{len(ss):>6d}{n:>6d}{w:>9.2f}%{w-target:>+9.2f}%p'
              f'{w/100*NAV:>12,.0f}원{w/usable_pct*100:>13.0f}%')
    print('-' * 118)
    print(f'팀 운용 가능액 {usable:,.0f}원 = NAV의 {usable_pct:.2f}% '
          f'(슬리브 {SLEEVE:,.0f} − 메가캡 필수 {mega_cost:,.0f})')
    print(f'중립 목표 {target:.2f}% vs 운용 가능액 {usable_pct:.2f}% '
          f'→ 여유 {usable_pct-target:+.2f}%p')

    # --- 팀별 매수 가능성 진단 ---
    print('\n' + '=' * 118)
    print('팀별 매수 가능성 — 진입틸트 = |(중립주수 올림) × 1주NAV% − 중립%|')
    print(f'{"팀":<20s}{"총종목":>7s}{"자유사이징":>10s}{"펀드IC 2/3":>11s}{"매수불가":>9s}'
          f'{"최저단가":>11s}{"중앙단가":>11s}')
    print('-' * 118)
    for t in (1, 2, 3):
        ss = [k for k, v in MANDATE.items() if v == t]
        picks = [s for s in stocks if s['sec'] in ss]
        free = ic = no = 0
        for s in picks:
            one_nav = s['price'] / NAV * 100
            entry = abs((int(s['w'] / one_nav) + 1) * one_nav - s['w'])
            if entry > HARD_CAP:   no += 1
            elif entry > TEAM_BUDGET: ic += 1
            else: free += 1
        px_s = sorted(s['price'] for s in picks)
        print(f'{t}. {TEAM_NAME[t]:<17s}{len(picks):>7d}{free:>10d}{ic:>11d}{no:>9d}'
              f'{px_s[0]:>10,.0f}원{px_s[len(px_s)//2]:>10,.0f}원')

    # --- 팀별 상위 종목 ---
    for t in (1, 2, 3):
        ss = [k for k, v in MANDATE.items() if v == t]
        picks = sorted([s for s in stocks if s['sec'] in ss], key=lambda s: -s['w'])[:8]
        print(f'\n[팀 {t} · {TEAM_NAME[t]}] 상위 8종목')
        print(f'  {"종목":<20s}{"주가":>11s}{"BM비중":>8s}{"1주=운용가능액":>13s}'
              f'{"중립주수":>9s}{"진입틸트":>10s}  판정')
        for s in picks:
            one_use = s['price'] / usable * 100      # 1주 = 팀 운용가능액의 몇 %
            one_nav = s['price'] / NAV * 100
            need = s['w'] / one_nav
            entry = abs((int(need) + 1) * one_nav - s['w'])
            flag = ('매수 불가' if entry > HARD_CAP else
                    '펀드 IC 2/3' if entry > TEAM_BUDGET else '팀 재량')
            print(f'  {s["name"]:<20s}{s["price"]:>10,.0f}원{s["w"]:>7.2f}%'
                  f'{one_use:>12.1f}%{need:>9.1f}주{entry:>+9.2f}%p  {flag}')

    # --- SK스퀘어 룩스루 ---
    sq = next(s for s in stocks if s['name'] == 'SK스퀘어')
    skh = next(s for s in stocks if s['name'] == 'SK하이닉스')
    STAKE = 0.2007        # SK스퀘어의 SK하이닉스 지분율 (공시 확인 필요)
    lev = skh['w'] * STAKE / sq['w']
    print('\n' + '=' * 118)
    print('SK스퀘어 룩스루 점검 — 지주회사가 메가캡 노출을 우회 반입한다')
    print(f'  SKH 시총 대비 SK스퀘어 보유지분 가치 = SKH의 {STAKE:.2%}')
    print(f'  SK스퀘어 1주({sq["price"]:,.0f}원) = NAV의 {sq["price"]/NAV*100:.2f}%')
    print(f'  → 내포 SKH 노출 = NAV의 {sq["price"]/NAV*100*lev:.2f}%  (레버리지 {lev:.2f}배)')
    print(f'  현재 펀드 SKH 직접보유 3주 = 20.95% (중립 {skh["w"]:.2f}%, {20.95-skh["w"]:+.2f}%p)')
    print(f'  SK스퀘어 1주 추가 시 실질 SKH = {20.95 + sq["price"]/NAV*100*lev:.2f}% '
          f'({20.95 + sq["price"]/NAV*100*lev - skh["w"]:+.2f}%p)')


if __name__ == '__main__':
    main()
