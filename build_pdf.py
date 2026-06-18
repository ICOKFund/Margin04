#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ICOK 레이아웃 HTML → PDF (weasyprint)."""
from weasyprint import HTML
import os

A = "report_assets"  # 차트 폴더 (상대경로, base_url 기준)

HTML_DOC = f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="utf-8"><style>
@page {{
  size: A4; margin: 16mm 14mm 18mm 14mm;
  @bottom-left {{ content: "Company Research Report | Micron Technology (MU)";
    font-family: 'Nanum Gothic'; font-size: 7pt; color: #888; }}
  @bottom-right {{ content: counter(page); font-family:'Nanum Gothic'; font-size:8pt; color:#555; }}
}}
@page cover {{ margin: 0; }}
* {{ box-sizing: border-box; }}
body {{ font-family: 'Nanum Gothic','Noto Sans CJK KR',sans-serif; color:#1a1a1a; font-size:9.2pt; line-height:1.5; }}
h1,h2,h3,h4 {{ color:#002A52; margin:0 0 6px; }}
.navy {{ color:#002A52; }}
.muted {{ color:#777; font-size:7.6pt; }}
.section-break {{ break-before: page; }}

/* ---------- COVER ---------- */
.cover {{ page: cover; height:297mm; padding:0; position:relative; }}
.cover-band {{ background:#002A52; color:#fff; padding:26mm 16mm 12mm; }}
.cover-band .tag {{ font-size:8pt; letter-spacing:2px; opacity:.8; }}
.cover-band h1 {{ color:#fff; font-size:23pt; margin:6px 0 4px; line-height:1.25; }}
.cover-band .sub {{ font-size:11pt; color:#cdddf0; }}
.cover-body {{ padding: 8mm 16mm; }}
.flexrow {{ display:flex; gap:6mm; }}
.box {{ border:1px solid #d9d9d9; border-radius:3px; padding:8px 10px; }}
.kv {{ display:flex; justify-content:space-between; padding:2px 0; border-bottom:1px dotted #e3e3e3; }}
.kv:last-child {{ border-bottom:none; }}
.kv b {{ color:#002A52; }}
.rating {{ background:#002A52; color:#fff; font-weight:bold; padding:3px 12px; border-radius:3px; font-size:11pt; }}
.big {{ font-size:18pt; font-weight:bold; color:#002A52; }}
.up {{ color:#0a7a32; font-weight:bold; }}

/* ---------- TABLES ---------- */
table {{ border-collapse:collapse; width:100%; margin:6px 0 4px; font-size:8.4pt; }}
th {{ background:#002A52; color:#fff; padding:5px 6px; text-align:center; font-weight:600; }}
td {{ border:1px solid #e0e0e0; padding:4px 6px; text-align:center; }}
td.l {{ text-align:left; }}
tr:nth-child(even) td {{ background:#f6f8fb; }}
.hl {{ color:#002A52; font-weight:bold; }}

/* ---------- POINTS ---------- */
.point {{ border-left:4px solid #002A52; background:#f6f8fb; padding:8px 12px; margin:7px 0; }}
.point h4 {{ margin:0 0 3px; font-size:10pt; }}
.fig {{ text-align:center; margin:8px 0 2px; }}
.fig img {{ width:100%; max-width:165mm; }}
.figcap {{ font-size:7.6pt; color:#444; font-weight:600; margin-top:2px; }}
.src {{ font-size:7pt; color:#999; }}
.sec-label {{ display:inline-block; background:#002A52; color:#fff; font-size:8pt; padding:2px 10px; border-radius:2px; margin-bottom:4px; }}
ul {{ margin:4px 0 4px 16px; padding:0; }}
li {{ margin:2px 0; }}
.note {{ font-size:7.6pt; color:#a15; background:#fff6f6; border:1px solid #f0d6d6; padding:5px 8px; border-radius:3px; }}
hr.s {{ border:none; border-top:1px solid #e6e6e6; margin:10px 0; }}
</style></head><body>

<!-- ============ COVER ============ -->
<div class="cover">
  <div class="cover-band">
    <div class="tag">GLOBAL · SEMICONDUCTORS (MEMORY) · 2026.06.18</div>
    <h1>Micron Technology (MU)<br>F3Q26 Earnings Preview</h1>
    <div class="sub">AI가 만든 슈퍼사이클 — "비트(Beat)로 벌고, 가이던스(Guide-up)로 키운다"</div>
  </div>
  <div class="cover-body">
    <div class="flexrow">
      <div class="box" style="flex:1.1;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <span class="rating">BUY</span>
          <div style="text-align:right;"><div class="muted">목표주가 / Target</div><div class="big">US$1,200</div></div>
        </div>
        <div class="kv"><span>현재주가 (6/16)</span><b>US$1,020.76</b></div>
        <div class="kv"><span>상승여력</span><span class="up">+17.6%</span></div>
        <div class="kv"><span>52주 최고 / 최저</span><b>$1,020.76 / $93.37</b></div>
        <div class="kv"><span>시가총액</span><b>US$1,151bn</b></div>
        <div class="kv"><span>발행주식수</span><b>~1,078m</b></div>
        <div class="kv"><span>결산월</span><b>8월 (Fiscal Aug)</b></div>
      </div>
      <div class="box" style="flex:1;">
        <div class="muted" style="margin-bottom:4px;">기업 개요</div>
        <div class="kv"><span>사업구조</span><b>DRAM ~79% / NAND ~20%</b></div>
        <div class="kv"><span>시장지위</span><b>DRAM 3위 / NAND 4위</b></div>
        <div class="kv"><span>DRAM 점유율(CY25)</span><b>23%</b></div>
        <div class="muted" style="margin:6px 0 4px;">커버리지 (참고 IB)</div>
        <div class="kv"><span>Citi</span><b>Buy · $1,200</b></div>
        <div class="kv"><span>HSBC</span><b>Buy · $1,100</b></div>
        <div class="kv"><span>Goldman Sachs</span><b>Neutral · $900</b></div>
      </div>
    </div>

    <h3 style="margin-top:10px;">투자포인트 (Investment Points)</h3>
    <div class="point"><h4>1. Beat — 또 한 번의 어닝 서프라이즈</h4>
      6/24 발표될 F3Q26(May-Q)은 컨센서스를 큰 폭 상회 전망. GS 기준 매출 <b>+9%</b>, EPS <b>+12%</b> 상회.
      HSBC 영업이익 <b>$27bn(+66% q/q)</b>으로 직전 추정 대비 +16% 상향.</div>
    <div class="point"><h4>2. Guide-up — 컨센을 압도하는 낙관적 가이던스</h4>
      8월 분기 가이던스가 핵심 변수. GS 기준 매출 컨센 대비 <b>+21%</b>, EPS <b>+26%</b>.
      발표 직전 EPS 추정 일제히 두 자릿수 % 상향(GS +36%, HSBC +23~29%, Citi +10%).</div>
    <div class="point"><h4>3. Durability — 구조적 슈퍼사이클 + 장기계약(SCA/LTA)</h4>
      AI 수요가 GPU(HBM)→CPU·agentic으로 확산되며 commodity DRAM 동반 수혜.
      CSP capex <b>+71% y/y</b>, DRAM <b>5% 공급부족</b>이 CY27까지 지속. SCA/LTA가 이익 가시성 담보.</div>

    <h3 style="margin-top:8px;">재무 요약 <span class="muted">(단위: US$mn, EPS는 US$, Non-GAAP)</span></h3>
    <table>
      <tr><th>항목 (FY, 8월)</th><th>2024A</th><th>2025A</th><th>2026E</th><th>2027E</th><th>2028E</th></tr>
      <tr><td class="l">매출액</td><td>25,111</td><td>37,378</td><td class="hl">115,003</td><td>197,500</td><td>210,000</td></tr>
      <tr><td class="l">매출총이익률(GM%)</td><td>22.4%</td><td>39.8%</td><td class="hl">76.9%</td><td>82.9%</td><td>80.7%</td></tr>
      <tr><td class="l">영업이익(EBIT)</td><td>1,114</td><td>9,871</td><td class="hl">81,767</td><td>154,805</td><td>159,007</td></tr>
      <tr><td class="l">Core EPS</td><td>0.54</td><td>7.43</td><td class="hl">60.73</td><td>114.73</td><td>117.83</td></tr>
      <tr><td class="l">PER(x)</td><td>n/a</td><td>n/a</td><td>16.8</td><td>8.9</td><td>8.7</td></tr>
      <tr><td class="l">ROE(%)</td><td>1.7</td><td>17.2</td><td>76.6</td><td>67.5</td><td>40.9</td></tr>
    </table>
    <div class="fig"><img src="{A}/ja1_annual.png"></div>
    <div class="figcap">자료1. Micron 연간 실적 추이 (매출 vs GM%) <span class="src">· 출처: Citi Research, ICOK</span></div>
    <div class="muted" style="margin-top:6px;">팀: ICOK Research · 본 자료는 GS·Citi·HSBC·BofA 리포트를 종합한 내부 참고용 프리뷰</div>
  </div>
</div>

<!-- ============ CONTENTS ============ -->
<div class="section-break">
  <span class="sec-label">CONTENTS</span>
  <h2>목차</h2>
  <table style="font-size:10pt; width:70%;">
    <tr><th style="width:15%;">No.</th><th>Section</th><th style="width:15%;">Page</th></tr>
    <tr><td>1</td><td class="l">산업분석 — 메모리 슈퍼사이클</td><td>3</td></tr>
    <tr><td>2</td><td class="l">기업분석 — Micron Technology</td><td>4</td></tr>
    <tr><td>3</td><td class="l">투자포인트 — Beat / Guide-up / Durability</td><td>5</td></tr>
    <tr><td>4</td><td class="l">Valuation</td><td>6</td></tr>
    <tr><td>5</td><td class="l">Risk Point</td><td>7</td></tr>
  </table>
</div>

<!-- ============ 1. 산업분석 ============ -->
<div class="section-break">
  <span class="sec-label">산업분석</span>
  <h2>1. 산업분석 (Industry Analysis)</h2>
  <h3>1.1 메모리 슈퍼사이클 — 구조적 국면</h3>
  <p>메모리(DRAM·NAND) 산업은 AI 데이터센터 투자의 핵심 수혜처다. 과거 PC·모바일 교체수요 중심의 단순
  순환과 달리, 현재는 AI 추론 수요가 GPU에서 CPU·일반 서버로 확산되며 commodity DRAM까지 동반 상승하는
  <b>구조적 국면</b>이다. HSBC는 이를 1990–95년 DRAM 슈퍼사이클과 유사한 "사이클 중간 지점"으로 진단한다.</p>
  <h3>1.2 가격 (Pricing)</h3>
  <ul>
    <li>Citi: 2026년 <b>DRAM ASP +200%</b>, <b>NAND ASP +186%</b> (분기별 DRAM 2Q +37% → 3Q +13% → 4Q +11%)</li>
    <li>DRAM 현물가 연초 대비 <b>+52%</b>, 4월 대비 +22% / <b>현물가가 계약가 대비 +21% 높음</b> → 계약가 추가 상승 시사</li>
    <li>HSBC: 서버 DRAM 계약가(DDR5 32GB) <b>1Q26 +95% q/q</b></li>
  </ul>
  <h3>1.3 수급 (Supply/Demand)</h3>
  <ul>
    <li>Citi: 2026년 글로벌 DRAM <b>5% 공급부족</b>, 업사이클 CY27까지 지속</li>
    <li>BofA(Tech Conf.): 공급 전반 타이트하나 각 업체가 1–2년치 capacity 확보(NVDA $124bn 구매약정)</li>
  </ul>
  <h3>1.4 수요 동인 (Demand Drivers)</h3>
  <ul>
    <li>CSP capex: 미국 <b>$642bn(+71% y/y)</b>, 글로벌 $739bn(+81% y/y) — HSBC</li>
    <li>AI Broadening: GPU(HBM)→CPU·agentic 확산 → AI:일반 서버 비중 4–8:1 → <b>1:1</b>로 이동</li>
    <li><b>SO-CAMM2</b>: ARM 서버 CPU용 신규 표준, 2027년 DRAM 수요의 ~10% — "컨센이 놓친 구조적 동인"(HSBC)</li>
    <li>HBM: 2027년 시장 <b>$163bn</b>, 비트수요 CAGR 67%</li>
  </ul>
</div>

<!-- ============ 2. 기업분석 ============ -->
<div class="section-break">
  <span class="sec-label">기업분석</span>
  <h2>2. 기업분석 (Company Analysis)</h2>
  <h3>2.1 기업개요</h3>
  <p>미국 아이다호 보이시 소재 메모리 전문기업. <b>DRAM 세계 3위·NAND 세계 4위</b>. 미·일·싱가포르·대만에
  전공정 팹, 중·말레이시아·인도·싱가포르에 후공정 라인을 둔 수직계열화 구조. 매출의 약 79%가 DRAM.</p>
  <ul>
    <li>DRAM 점유율(CY25): Samsung 34% / SK hynix 35% / <b>Micron 23%</b> / 기타 8%</li>
    <li>eSSD 점유율(CY25): Samsung 38% / SK hynix 28% / <b>Micron 16%</b> / Kioxia 14%</li>
  </ul>
  <h3>2.2 분기 실적 추이</h3>
  <table>
    <tr><th>항목</th><th>1QFY26</th><th>2QFY26</th><th>3QFY26e</th><th>4QFY26e</th></tr>
    <tr><td class="l">매출($bn)</td><td>13.6</td><td>23.9</td><td class="hl">35.3</td><td class="hl">41.7</td></tr>
    <tr><td class="l">GPM%</td><td>57%</td><td>75%</td><td class="hl">82%</td><td class="hl">84%</td></tr>
    <tr><td class="l">영업이익($bn)</td><td>6.4</td><td>16.5</td><td class="hl">27.3</td><td class="hl">32.4</td></tr>
    <tr><td class="l">OPM%</td><td>47%</td><td>69%</td><td class="hl">77%</td><td class="hl">78%</td></tr>
  </table>
  <div class="fig"><img src="{A}/ja7_quarter.png"></div>
  <div class="figcap">자료7. Micron 분기 실적 추이 <span class="src">· 출처: HSBC estimates, ICOK</span></div>
  <h3>2.3 재무분석</h3>
  <p>FY26E 매출 $115bn(+208% y/y), 영업이익률 71%로 사상 최대. 가격 상승 + 고정비 레버리지로 GM이
  FY24 22%→FY26E 77%로 점프. 강한 FCF로 FY26E부터 순현금 전환 전망(Citi: 순부채 -$31.6bn).</p>
</div>

<!-- ============ 3. 투자포인트 ============ -->
<div class="section-break">
  <span class="sec-label">투자포인트</span>
  <h2>3. 투자포인트 (Investment Points)</h2>
  <h3>3.1 Beat — 컨센서스 상회</h3>
  <div class="flexrow">
    <div style="flex:1;">
      <table>
        <tr><th>F3Q26 (GS)</th><th>GS</th><th>스트리트</th><th>차이</th></tr>
        <tr><td class="l">매출</td><td>$37.6bn</td><td>$34.4bn</td><td class="hl">+9%</td></tr>
        <tr><td class="l">GM</td><td>83.4%</td><td>81.9%</td><td>+150bp</td></tr>
        <tr><td class="l">EPS</td><td>$22.07</td><td>$19.74</td><td class="hl">+12%</td></tr>
      </table>
    </div>
    <div style="flex:1;"><div class="fig"><img src="{A}/ja8_beat.png"></div></div>
  </div>
  <div class="figcap">자료8. F3Q26 GS 추정 vs 스트리트 <span class="src">· 출처: Goldman Sachs, Visible Alpha, ICOK</span></div>
  <p style="margin-top:6px;"><b>연간 컨센 대비 괴리(시간이 갈수록 확대):</b> GS CY26 매출/EPS <b>+30%/+36%</b>,
  HSBC FY26/27/28e OP <b>+3%/+14%/+29%</b>, Citi F27E EPS +4%. → 컨센이 사이클 지속성을 과소반영.</p>

  <h3>3.2 Guide-up — 낙관적 가이던스</h3>
  <div class="flexrow">
    <div style="flex:1;">
      <table>
        <tr><th>F4Q26 가이던스(GS)</th><th>GS</th><th>스트리트</th><th>차이</th></tr>
        <tr><td class="l">매출</td><td>$48.8bn</td><td>$40.4bn</td><td class="hl">+21%</td></tr>
        <tr><td class="l">GM</td><td>86.1%</td><td>84.0%</td><td>+204bp</td></tr>
        <tr><td class="l">EPS</td><td>$29.95</td><td>$23.68</td><td class="hl">+26%</td></tr>
      </table>
    </div>
    <div style="flex:1;"><div class="fig"><img src="{A}/ja9_guide.png"></div></div>
  </div>
  <div class="figcap">자료9. F4Q26 가이던스 전망 vs 스트리트 <span class="src">· 출처: Goldman Sachs, ICOK</span></div>

  <h3>3.3 Durability — 구조적 수요 & SCA/LTA</h3>
  <ul>
    <li>SCA/LTA가 향후 수년 매출·이익 지속성 담보. 관심: 가격 보장 수준·추가 계약. <b>Citi는 Dell 서명 추정.</b></li>
    <li>AI broadening + SO-CAMM2 + HBM이 수요를 다변화 → 단일 응용처 의존도 완화.</li>
  </ul>
</div>

<!-- ============ 4. Valuation ============ -->
<div class="section-break">
  <span class="sec-label">Valuation</span>
  <h2>4. Valuation</h2>
  <h3>4.1 증권사별 목표주가 비교</h3>
  <div class="flexrow">
    <div style="flex:1.2;">
      <table>
        <tr><th>증권사</th><th>의견</th><th>목표주가(이전)</th><th>방법론</th></tr>
        <tr><td class="l">Citi</td><td>Buy</td><td class="hl">$1,200 ($840)</td><td class="l">CY27E EPS×10x</td></tr>
        <tr><td class="l">HSBC</td><td>Buy</td><td class="hl">$1,100 ($750)</td><td class="l">FY27/28 BVPS×3.8x PB</td></tr>
        <tr><td class="l">Goldman Sachs</td><td>Neutral</td><td>$900 ($400)</td><td class="l">정상화 EPS$50×18x</td></tr>
      </table>
    </div>
    <div style="flex:1;"><div class="fig"><img src="{A}/ja11_tp.png"></div></div>
  </div>
  <div class="figcap">자료11. 증권사별 목표주가 <span class="src">· 출처: 각사, ICOK</span></div>
  <p style="margin-top:4px;">세 증권사 모두 목표주가 2~2.7배 상향. Citi의 10x는 과거 peak(17x) 대비 할인 → 추가 상단 여력.
  현 PER(FY26E 16.8x, FY27E 8.9x)은 이익 급증 감안 시 낮은 구간. <b>→ 목표주가 $1,200, BUY.</b></p>

  <h3>4.2 증권사별 EPS 추정 비교</h3>
  <table>
    <tr><th>EPS($)</th><th>FY25A</th><th>FY26E</th><th>FY27E</th><th>FY28E</th></tr>
    <tr><td class="l">Goldman Sachs</td><td>7.42</td><td>67.48</td><td>138.86</td><td>137.51</td></tr>
    <tr><td class="l">HSBC</td><td>7.59</td><td>61.88</td><td>126.82</td><td>142.91</td></tr>
    <tr><td class="l">Citi</td><td>7.43</td><td>60.73</td><td>114.73</td><td>117.83</td></tr>
    <tr><td class="l">컨센서스(VA/IBES)</td><td>~8.0</td><td>~58</td><td>~106</td><td>~105</td></tr>
  </table>
  <div class="fig"><img src="{A}/ja12_eps.png"></div>
  <div class="figcap">자료12. 증권사별 EPS 추정 비교 <span class="src">· 출처: 각사, Visible Alpha, LSEG IBES, ICOK</span></div>
</div>

<!-- ============ 5. Risk Point ============ -->
<div class="section-break">
  <span class="sec-label">Risk Point</span>
  <h2>5. Risk Point</h2>
  <h3>5.1 공급 측 — CXMT / 증설</h3>
  <p>중국 CXMT의 DRAM 점유율 확대 시 가격 dynamics 훼손(GS). 공격적 증설로 bit 공급과잉 시 하향 리스크(Citi).
  TrendForce는 Micron 2026년 비트 공급 +42% y/y 전망.</p>
  <h3>5.2 HBM 점유율 경쟁</h3>
  <p>Samsung·SK hynix 대비 HBM 점유율(~20%) 확보·확대 실패 시 리스크. HBM4 세대 경쟁력이 관건.</p>
  <h3>5.3 매크로 / 포지셔닝</h3>
  <p>neo-CSP·OpenAI의 재무적 투자자 의존 → 미 금리 상승 시 capex 둔화 가능(HSBC).
  주가 급등으로 기대치가 높아 "buy the rumor" 차익실현 가능성.</p>
  <hr class="s">
  <h3>자료 출처</h3>
  <ul class="muted">
    <li>Goldman Sachs — MU 3Q Preview, 2026.06.08</li>
    <li>Citi — MU Preview: Investor Focus on LTA Commentary, 2026.06.17</li>
    <li>HSBC — MU Buy: Another record high earnings in 3Q, 2026.05.18</li>
    <li>BofA — US Semis Tech Conf. Takeaways, 2026.06.08</li>
  </ul>
  <div class="note">⚠ Disclaimer: 본 문서는 상기 증권사 리서치를 요약·재구성한 내부 참고용 프리뷰이며 투자 권유가 아님.
  목표주가/투자의견은 첨부 IB 자료를 종합한 예시이며 ICOK 공식 견해가 아님.</div>
</div>

</body></html>"""

base = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(base, "Micron_3Q26_Earnings_Preview.pdf")
HTML(string=HTML_DOC, base_url=base).write_pdf(out)
print("saved:", out)
