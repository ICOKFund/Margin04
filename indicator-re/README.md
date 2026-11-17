# 2023 개인투자자 보조지표 역설계 — 검증 보고서

목표: Obsidian 노트·차트 캡처로 남아 있는 2023년 보조지표를 TradingView Pine Script v6로 재구현.
이 폴더는 그 1단계(화면 값 ↔ 실제 시세 대조 검증) 결과물이다.

## 폴더 구성

| 경로 | 내용 |
|---|---|
| `tools/` | 다운로더, 지표 재구현, 이미지 분석 도구, 분석 스크립트(`v1.py`~`v30.py`) |
| `data/bn_1d`, `data/bn_4h` | 바이낸스 USD-M 선물 BTCUSDT 월별 klines zip (2020-01~2023-06). TradingView `BINANCE:BTCUSDT.P`와 동일 |
| `data/yahoo/` | Yahoo v8 일봉 CSV: `^IXIC`, `SOXL`, `HG=F`(연속 근월물 — 차트의 HGK2023과 다름) |
| `data/*.json` | 나스닥 LHB 패널 검은선/주황선 픽셀 추적 결과 |
| `crops/` | 원본 캡처에서 잘라낸 확대 이미지 |

원본 노트(14개)와 차트 캡처 원본은 포함하지 않았다(사용자 보유).

## 실행 방법

Python 3 필요. 이미지 도구는 Pillow(`pip install pillow`) 필요.

```bash
cd indicator-re/tools
# 데이터 재다운로드 (선택)
python3 fetch_binance.py BTCUSDT 1d ../data/bn_1d 2020 1 2023 6
python3 fetch_binance.py BTCUSDT 4h ../data/bn_4h 2020 1 2023 6
python3 fetch_yahoo.py ^IXIC ../data/yahoo/IXIC_1d.csv <period1> <period2> 1d
# 분석 스크립트 예: 인자로 데이터 경로를 넘김 (각 vN.py 상단의 sys.argv 사용부 참고)
```

주요 모듈:
- `bn.py` — `load(dir)` → `(open_ms, O,H,L,C,V)` 튜플 목록, `cut(bars, end_ms, last=(O,H,L,C))`로 캡처 시점 진행 중 봉 덮어쓰기, `ms(y,m,d,h)`
- `yh.py` — `load_daily(path)`, `to_weekly`(월요일 기준), `cut`
- `ta.py` — `sma`, `ema`/`rma`(SMA 시드), `wma`, `stdev`(모집단), `pivots(x,left,right,high)` (오른쪽 엄격·왼쪽 비엄격 = Pine `ta.pivothigh/low`와 동일)
- `ds.py` — `bundle(ixic_csv, soxl_csv, bn_1d_dir, bn_4h_dir)`: 4개 검증 데이터셋(캡처 시점에서 절단)
- `srv2.py` — LonesomeTheBlue "Support Resistance – Dynamic v2" 재구현
- `v26lib.py` — fareid MRC의 SuperSmoother `ss_fareid(src,n)`
- `mas.py` — HMA, DEMA, TEMA, T3, ALMA, LSMA, ZLEMA, KAMA, McGinley, SuperSmoother, Laguerre, JMA, VWMA
- 이미지: `crop.py`, `colruns.py`(한 열의 색 구간), `marks.py`, `trace.py`, `scan.py`, `dots.py`

### 검증 데이터셋 (캡처 시점 진행 봉 O/H/L/C 및 미해결 목표값)

| 데이터 | 절단 시점 | 진행 봉 O/H/L/C | TLLJ | SRS d |
|---|---|---|---|---|
| IXIC 1D | 2023-05-10 | 12286.66 / 12324.01 / 12211.58 / 12240.73 | 12061.70 | 385.50 |
| SOXL 1W | 2023-04-17 주 | 15.10 / 16.36 / 14.48 / 14.67 | 13.06 | 2.73 |
| BTC 1D | 2023-04-17 | 30286.6 / 30307.4 / 29714.1 / 29835.3 | 27974.5 | 2755.0 |
| BTC 4H | 2023-04-17 08:00 | 29831.2 / 29913.6 / 29781.6 / 29835.1 | 30413.7 | 644.9 |

## 확정된 구성요소 (계산식까지 화면 값과 일치)

| 구성요소 | 계산식 | 근거 |
|---|---|---|
| MA3~MA600 | 종가 SMA 3·5·10·20·60·120·240·360·480·600 (MA20c = MA20, 검은 점) | 나스닥·SOXL 라벨 18개 0.01 이내 |
| 볼린저밴드 | SMA20 ± 2σ(모집단) | IXIC 12349.80/11864.91, SOXL 상단 18.93 정확 |
| 프랙탈 박스 HH/LL (=FrH/FrL) | `pivothigh(high,2,2)`/`pivotlow(low,2,2)` 값 유지 | BTC 1D 31059.0/27166.0, 4H 30560.0/29714.1, IXIC 12261.32/11925.37, SOXL 18.34/13.15 |
| HL20/LL20 (주황/하늘 +) | `pivot(9,9)` 값 유지, 십자 표식 | 4개 데이터 일치. 오른쪽 9: 나스닥 표식 4/14·5/8 시작. 왼쪽 9: BTC 4H 4/5 값 28845.3(왼쪽 8이면 28540.0) |
| Fast/Mid/Slow | 앨리게이터: SMMA(=rma)(hl2) 5/8/13, 표시 오프셋 3/5/8 | 4개 데이터 12개 값 정확 |
| 빨강·파랑 수평선 (가격(%)) | LonesomeTheBlue S/R Dynamic v2 기본값(색만 변경). %는 마지막 종가 대비 | BTC 1D 24490.7/20986.8/18208.9/15452.9 정확, IXIC 5개 0.01 이내 |
| 평균회귀 채널 (A~H 구역) | fareid MRC 기본값: SuperSmoother(hlc3,200) ± π·mult·SuperSmoother(TR,200), mult 1.0/2.415 | BTC 1D 계산 34533.2/29671.9/26236.4/22800.9/17939.7 vs 화면 34517/29676/26228/22814/17938 (0.5px 이내) |
| 하단 P/R1/S1 | 내장 Pivot Points Standard, Traditional, Auto(1D → 월간) | BTC 2023-04 월간 P 29067.1/R1 31214.9/S1 27075.2와 정성 일치. 주간(R1 30541.0)은 불일치 |
| LHB 패널 주황선 | SMA20 | 나스닥 추적 RMS 2.30pt |

### S/R Dynamic v2 재구현 요점 (`srv2.py`)
- 피벗 기간 10(high/low), 최근 피벗 20개(최신순, 같은 봉 고·저 동시면 고점 우선)
- 채널 폭 = (highest(high,300) − lowest(low,300)) × 10%, 마지막 피벗 확정 봉 기준
- 강도 내림차순 유지, loc<5 & strength≥2 이면 삽입, 5개로 절단, 겹치면 강도 ≥ 일 때만 교체
- 표시값 `floor((hi+lo)/2/tick + 0.5)*tick`

## 미해결 (구조만 확인, 작성자 자작 추정)

| 구성요소 | 확인된 구조 | 기각된 가설 |
|---|---|---|
| SRS (녹색 점) | FrH + d, FrL − d (위아래 같은 d). d는 천천히 변하는 절대값 — IXIC 385.50, SOXL 2.73(6개월간 2.61→2.73), BTC 1D 2755.0, 4H 644.9, 구리 0.1610 | TR/H−L/\|ΔC\|/\|C−O\|/가격/박스 파생값의 분위수·z·σ·k·평균(전 룩백), MRC 폭, 스윙·돌파 초과폭 분포. 최근접 SMA(H−L,655)×1.69 (편차 10%) |
| TLLJ (검은선) | 비교적 빠른 평활선. 나스닥 궤적: ≈12072, 12085, 12085, 12076.5, 12063.7, 12050.8, 12046.5, 12055.1 → 최종 12061.70 | 이동평균 약 17종 × 길이 2~120 × 시프트, 기존 선 2~4개 평균(최근접 0.57%) |
| LS/SS (빨간 점) | LS = 마지막 매수 신호봉 저가, SS = 마지막 매도 신호봉 고가. 값 바뀐 봉에 점 | 봉 색, BB 위치, 진폭/ATR, 거래량 배수, 앨리게이터 위치, MFI 봉 유형 |
| LHB 밴드 | 위아래 5겹(보라 + 외곽, 파란 실선 2, 파란 점선 2) 대칭 | SOXL 반폭 7.373/6.554/5.735/4.46/3.277 (중심 ≈14.33), IXIC 672/620.7/568.1/490.9/411.6 — 비율 불일치 |
| JLK (리버모어 키) | 기준 ± 1·2·3단계 7개 선, 9~10봉마다 계단 갱신·원 표식. 구리 기준 4.0090, 단계 ≈0.1025 | 구리 HGK2023 데이터 없어 미검증 |

LS/SS 단서: BTC 4H 4/10 12:00~4/11 00:00 연속 장대 상승봉에 매수 점. SOXL 2022 매도 점 9주(2/28, 4/18, 4/25, 5/2, 5/9, 6/6, 6/13, 6/27, 10/3) 모두 전주 대비 거래량 증가.

## 다음 단계

1. 확정 구성요소 Pine v6 작성: 메인 오버레이(MA·BB·프랙탈 박스·pivot(9,9)·앨리게이터), S/R v2, MRC. 공개 스크립트는 원본 소스를 받아 이식(라이선스 고지 포함).
2. SRS는 d를 input으로 노출한 골격으로 작성.
3. 미해결 5개 복원용 추가 자료 요청: 범례("v 8") 펼친 화면·설정 창(Inputs/Style) 캡처, Pine 소스, 구리·WTI CSV 내보내기, MACD 박스·JLK·르네상스 차트 이미지.

## 출처
- Mean Reversion Channel (fareid): https://kr.tradingview.com/script/5uaoczeP-Mean-Reversion-Channel-fareid-s-MRI-Variant
- Support Resistance – Dynamic v2 (LonesomeTheBlue): https://in.tradingview.com/script/va09eWAp-Support-Resistance-Dynamic-v2
- 위 S/R 지표 설명: https://www.luxalgo.com/library/indicator/va09eWAp-support-resistance-dynamic-v2/

공개 스크립트 두 개는 tradingview.com 접속이 막힌 환경에서 기억으로 재구현해 화면 값과 대조했다. 원본 소스와는 아직 대조하지 않았다.
