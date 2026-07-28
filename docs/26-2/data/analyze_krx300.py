"""KRX 300 구성종목 분석 — 시장별·집중도·정수주 제약 산출

사용법:  python3 analyze_krx300.py [NAV원화]
원자료:  krx300_constituents_20260727.csv  (KRX 정보데이터시스템 → 지수 → 지수구성종목)
         krx300_index_daily_20260728.csv   (KRX 정보데이터시스템 → 지수 → 일별시세)
인코딩:  EUC-KR
단위:    상장시가총액 = 백만원

매 반기(또는 NAV ±20% 변동 시) 재실행해 맨데이트 중립 자본과 정수주 임계값을 갱신한다.
"""
import csv, sys, pathlib

HERE = pathlib.Path(__file__).parent
CONST = HERE / 'krx300_constituents_20260727.csv'
INDEX = HERE / 'krx300_index_daily_20260728.csv'
NAV = int(sys.argv[1]) if len(sys.argv) > 1 else 26_000_000

# 코스닥 구성종목 (종목명 기반 분류 · 경계 13종목 오차 여지 0.62%)
# W1에서 KRX 시장구분 데이터로 확정할 것
KOSDAQ = set("""196170 086520 247540 277810 036930 058470 240810 319660 028300 298380
214450 039030 141080 000250 222800 214370 403870 087010 145020 214150 108490 095340
095610 347850 084370 080220 178320 257720 319400 226950 031980 067310 310210 263750
064760 005290 357780 237690 098460 140860 068760 032820 041510 035900 058610 089030
060370 290650 131970 007390 096530 082920 083650 030530 183300 043260 039200 218410
078600 166090 195940 437730 458870 475830 323280 034230 347700 101490 036540 293490
085660 099320 090710 417200 232140 122870 281740 065350 213420 388720 100790 328130
137400 445680 376900 115180 075580 253450 036830 466100 161580 397030 358570 456160
082270 348370 174900""".split())

MEGACAP = ['005930', '000660']          # 삼성전자, SK하이닉스
TEAM_ACTIVE_BUDGET = 6.0                 # 팀 액티브 예산 ±%p → 정수주 임계값의 상한

def load(path, enc='euc-kr'):
    return list(csv.reader(path.read_bytes().decode(enc).splitlines()))

def main():
    rows = load(CONST)[1:]
    tot = sum(float(r[5]) for r in rows)
    w = {r[0]: float(r[5]) / tot * 100 for r in rows}
    px = {r[0]: float(r[2]) for r in rows}
    nm = {r[0]: r[1] for r in rows}

    irows = load(INDEX)[1:]
    match = [r for r in irows if abs(float(r[9]) - tot) / tot < 1e-6]
    asof = match[0][0] if match else '(지수파일과 불일치 — 기준일 확인 필요)'
    print(f'기준일(지수 시총 대조): {asof}   구성종목 {len(rows)}   시총합 {tot/1e6:,.1f}조\n')

    kq = [r for r in rows if r[0] in KOSDAQ]
    kqc = sum(float(r[5]) for r in kq)
    print('[시장별]')
    print(f'  코스피 {len(rows)-len(kq):>3}종목  {(tot-kqc)/1e6:>8,.1f}조  {(tot-kqc)/tot*100:>5.2f}%')
    print(f'  코스닥 {len(kq):>3}종목  {kqc/1e6:>8,.1f}조  {kqc/tot*100:>5.2f}%\n')

    rows.sort(key=lambda r: -float(r[5]))
    mega = sum(w[c] for c in MEGACAP)
    print('[집중도]')
    for c in MEGACAP:
        print(f'  {nm[c]:<12} {w[c]:>5.2f}%')
    print(f'  메가캡 합       {mega:>5.2f}%')
    for k in (10, 50, 100):
        print(f'  상위 {k:>3}종목    {sum(float(r[5]) for r in rows[:k])/tot*100:>5.2f}%')
    print(f'  하위 200종목    {sum(float(r[5]) for r in rows[100:])/tot*100:>5.2f}%')
    print(f'  잔여 유니버스   {100-mega:>5.2f}%  ({len(rows)-len(MEGACAP)}종목)\n')

    # 두 가지를 따로 본다.
    #   (a) 중립오차  = |가장 가까운 정수주 비중 − 중립|  → 중립을 맞출 수 있는가
    #   (b) 진입틸트  = |1주 추가 비중 − 중립|            → 매수하면 얼마나 베팅하게 되는가
    # (b)가 하드캡(8%p) 초과면 매수 불가, 팀 예산 초과면 펀드 IC 2/3 사안이다.
    HARD_CAP = 8.0
    print(f'[정수주 제약]  NAV {NAV:,}원 · 팀 예산 ±{TEAM_ACTIVE_BUDGET}%p · 단일종목 하드캡 {HARD_CAP}%p')
    buckets = {'팀 ±1주': [], '펀드 IC 2/3': [], '매수 불가': []}
    for r in rows:
        c = r[0]; one = px[c] / NAV * 100
        if one < 3.0:
            continue
        need = w[c] / 100 * NAV / px[c]
        lo, hi = int(need), int(need) + 1
        err = min(abs(lo * one - w[c]), abs(hi * one - w[c]))       # (a) 중립오차
        entry = abs((int(need) + 1) * one - w[c])                    # (b) 진입틸트
        zone = ('매수 불가' if entry > HARD_CAP
                else '펀드 IC 2/3' if (entry > TEAM_ACTIVE_BUDGET or err > TEAM_ACTIVE_BUDGET)
                else '팀 ±1주')
        buckets[zone].append((nm[c], one, w[c], need, lo, hi, err, entry))
    for zone in ('팀 ±1주', '펀드 IC 2/3', '매수 불가'):
        if not buckets[zone]:
            continue
        print(f'  ── {zone} ({len(buckets[zone])}종목)')
        for n, one, wn, need, lo, hi, err, entry in sorted(buckets[zone], key=lambda x: -x[7]):
            pct = entry / TEAM_ACTIVE_BUDGET * 100
            print(f'     {n:<14} 1주 {one:>5.2f}%p  중립 {wn:>5.2f}%  중립오차 {err:>4.2f}%p'
                  f'  진입틸트 {entry:>5.2f}%p (팀 예산의 {pct:>3.0f}%)')
    n_free = len([r for r in rows if px[r[0]] / NAV * 100 < 3.0])
    print(f'  ── 자유 사이징 (1주 < NAV 3%): {n_free}종목')

if __name__ == '__main__':
    main()
