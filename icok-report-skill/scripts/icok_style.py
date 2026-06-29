# -*- coding: utf-8 -*-
"""
ICOK 리포트 차트 양식 모듈 (DESIGN_SPEC §1·2·4)
- 모든 ICOK 자료(exhibit) 차트는 이 모듈로 생성한다.
- 원칙: "표시 크기로 그리고 폰트를 키운다." 자료는 슬라이드에서 절반 폭(W3.29")로
  축소되므로 figure를 작게(종횡비 ~1.6) + 폰트를 크게 그려야 글씨가 읽힌다.
- 차트 내 타이틀 금지(제목은 자료 캡션 바가 담당). 색은 아래 토큰만 사용.

사용 예:
    from icok_style import setup, band_chart, bar_line, waterfall, factor_table
    setup()
    band_chart("자료30.png", dates, pbr, 0.8, 3.8, median=2.3, current="현재 8.0x")
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager as fm
from matplotlib.patches import Rectangle
import numpy as np
from datetime import datetime

# ── 색상 토큰 (DESIGN_SPEC §2) — 테마 사용 금지, HEX 직접 지정 ──────────────
NAVY = "#002A52"   # 차트 주색(막대/라인/기준값)
RED  = "#C8101E"   # 강조(돌파/핵심 콜아웃/해소요인)
ICOK = "#005EB8"   # ICOK 블루(목표선/중앙값/캡션 헤더)
BLUE = ICOK        # alias
BLACK= "#1A1A1A"
BAND = "#CFE0F2"   # 밴드 음영
SUB  = "#EAF1FA"   # 표 교차행
LINE = "#C2CCD8"   # 보더
GREY = "#8A97A6"   # 주석/NM/적자
GRID = "#E6E9EE"

# 막대 위/밀집 라벨은 항상 흰 박스로 가독성 확보(저대비 가림 방지)
WB = dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.9)

FIGSIZE = (4.0, 2.5)   # 종횡비 ≈ 1.6 고정 → W3.29" 배치 시 H≈2.05"


def setup():
    """matplotlib 공통 셋업. 모든 차트 생성 전 1회 호출."""
    for c in ["Pretendard", "Malgun Gothic"]:
        if c in {f.name for f in fm.fontManager.ttflist}:
            plt.rcParams["font.family"] = c
            break
    plt.rcParams["axes.unicode_minus"] = False


def _strip(ax, ygrid=True):
    """top·right 스파인 제거 + y축 옅은 그리드."""
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    if ygrid:
        ax.grid(axis="y", color=GRID, lw=0.6, zorder=0)


def _save(fig, path):
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", dpi=200)
    plt.close(fig)
    return path


# ── 패턴 1: 시계열 밴드 차트 (PBR/PER 밴드, 역사 범위 돌파) ────────────────
def band_chart(path, dates, values, band_lo, band_hi, median=None,
               current=None, current_xy=None, ylabel="PBR (배)",
               ymax=None, note=None, note_xy=None):
    """
    dates  : list[datetime] 또는 list["YYYY-MM"]
    values : list[float]  (밴드 상단 초과 구간은 자동 레드 하이라이트)
    band_lo/band_hi : 역사 밴드 범위
    median : 중앙값 점선(옵션)
    current: 현재값 콜아웃 텍스트(옵션) — 화살표로 마지막 점 지시
    """
    if dates and isinstance(dates[0], str):
        dates = [datetime.strptime(d, "%Y-%m") for d in dates]
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=200)
    ax.axhspan(band_lo, band_hi, color=BAND, alpha=0.7, zorder=0)
    if median is not None:
        ax.axhline(median, color=BLUE, lw=1, ls=(0, (4, 3)), zorder=1)
        ax.text(dates[1], median + 0.15, f"중앙값 {median:.1f}x",
                fontsize=9.5, color=BLUE, va="bottom")
    ax.plot(dates, values, color=NAVY, lw=2.2, zorder=3)
    ax.plot(dates, [v if v > band_hi else np.nan for v in values],
            color=RED, lw=3, zorder=4)
    ax.scatter([dates[-1]], [values[-1]], color=RED, s=40, zorder=5)
    ax.text(dates[1], band_hi + 0.2, f"역사 밴드 {band_lo:g}~{band_hi:g}x",
            fontsize=10.5, color=NAVY, va="bottom", fontweight="bold")
    anchor = dates[int(len(dates) * 0.58)]   # 콜아웃 텍스트 x앵커(시리즈 길이 무관)
    if current:
        cxy = current_xy or (dates[-1], values[-1])
        ax.annotate(current, xy=cxy, xytext=(anchor, values[-1] * 0.9),
                    ha="left", va="center", fontsize=13, color=RED, fontweight="bold",
                    arrowprops=dict(arrowstyle="-", color=RED, lw=1.1))
    if note:
        nx, ny = note_xy or (anchor, (band_hi + (ymax or max(values))) / 2)
        ax.text(nx, ny, note, fontsize=10, color=RED, ha="left")
    ax.set_ylim(0, ymax or max(values) * 1.12)
    ax.set_ylabel(ylabel, fontsize=11)
    _strip(ax)
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.tick_params(labelsize=9.8)
    return _save(fig, path)


# ── 패턴 2: 이중축 막대+라인 (이익 vs 멀티플) ─────────────────────────────
def bar_line(path, cats, bars, line, bar_label="EPS (만원)", line_label="Fwd P/E (배)",
             target=None, target_label=None, bar_unit=1.0, neg_note=None, neg_note_xy=None,
             line_offsets=None, target_xy=None, bar_ylim=None, line_ylim=None):
    """
    cats : x축 카테고리 라벨
    bars : 막대값(음수는 자동 그레이 + 'NM' 주석용)
    line : 우축 라인값(None 허용=결측 구간, 예: 적자해 NM)
    target : 우축 목표선(점선)  / target_label : 목표 라벨
    line_offsets : {i:(dx,dy)} 라인 라벨 오프셋(겹침 방지). 미지정 시 자동.
    라인 라벨·목표 라벨은 항상 흰 박스(WB).
    """
    x = np.arange(len(cats))
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=200)
    cols = [NAVY if b >= 0 else GREY for b in bars]
    ax.bar(x, [b / bar_unit for b in bars], color=cols, width=0.64, zorder=2)
    ax.axhline(0, color="#444", lw=0.8)
    ax.set_ylabel(bar_label, fontsize=10.5, color=NAVY)
    if bar_ylim:
        ax.set_ylim(*bar_ylim)
    if neg_note:
        nx, ny = neg_note_xy or (x[len(x) // 2], -abs(max(b / bar_unit for b in bars)) * 0.12)
        ax.text(nx, ny, neg_note, ha="center", va="center",
                fontsize=9, color=GREY, fontweight="bold")
    ax2 = ax.twinx()
    xx = [i for i in range(len(line)) if line[i] is not None]
    yy = [line[i] for i in xx]
    ax2.plot(xx, yy, color=RED, lw=2.4, marker="o", ms=6, zorder=4)
    off = line_offsets or {i: (0, -14) for i in xx}
    for i in xx:
        ax2.annotate(f"{line[i]:.1f}x", (i, line[i]), textcoords="offset points",
                     xytext=off.get(i, (0, -14)), ha="center", fontsize=9.5,
                     color=RED, fontweight="bold", bbox=WB, zorder=6)
    if target is not None:
        ax2.axhline(target, color=BLUE, lw=1.2, ls=(0, (4, 3)))
        if target_label:
            tx, ty = target_xy or (len(cats) * 0.4, target * 1.5)
            ax2.text(tx, ty, target_label, fontsize=9.5, color=BLUE,
                     ha="center", fontweight="bold", bbox=WB, zorder=6)
    if line_ylim:
        ax2.set_ylim(*line_ylim)
    ax2.set_ylabel(line_label, fontsize=10.5, color=RED)
    ax.set_xticks(x)
    ax.set_xticklabels(cats, fontsize=9.8)
    ax.spines["top"].set_visible(False)
    ax2.spines["top"].set_visible(False)
    ax.grid(axis="y", color="#EEF1F4", lw=0.6, zorder=0)
    return _save(fig, path)


# ── 패턴 3: 워터폴 (re-rating: 시작→증분→합계) ───────────────────────────
def waterfall(path, labels, start, steps, target, ceiling=None,
              ylabel="Fwd P/E (배)", ymax=None):
    """
    labels : 5개 권장 ['현 멀티플','+요인A','+요인B','+요인C','목표']
    start  : 시작값(네이비)
    steps  : 증분 리스트(레드) — len(labels)-2 개
    target : 합계값(블루)
    ceiling: 천장 점선(옵션)
    """
    n = len(labels)
    base, height, cols = [0.0] * n, [0.0] * n, [NAVY]
    base[0], height[0] = 0, start
    run = start
    for k, s in enumerate(steps):
        base[1 + k], height[1 + k] = run, s
        cols.append(RED)
        run += s
    base[-1], height[-1] = 0, target
    cols.append(BLUE)
    x = np.arange(n)
    fig, ax = plt.subplots(figsize=(4.3, 2.65), dpi=200)
    for i in range(n):
        ax.bar(x[i], height[i], bottom=base[i], width=0.66, color=cols[i], zorder=3)
        top = base[i] + height[i]
        lab = (f"{top:.1f}x") if i in (0, n - 1) else (f"+{height[i]:.1f}")
        ax.text(x[i], top + 0.18, lab, ha="center", fontsize=11.5, fontweight="bold",
                color=(NAVY if i in (0, n - 1) else RED))
    for i in range(n - 1):
        y = base[i] + height[i]
        ax.plot([x[i] + 0.33, x[i + 1] - 0.33], [y, y],
                color="#9AA7B4", lw=0.9, ls=(0, (3, 2)), zorder=2)
    if ceiling is not None:
        ax.axhline(ceiling, color=GREY, lw=1, ls=(0, (4, 3)))
        ax.text(0.0, ceiling + 0.25, f"천장 {ceiling:.1f}x", fontsize=9.5, color=GREY, ha="left")
    ax.set_ylim(0, ymax or (max(target, (ceiling or 0)) * 1.18))
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9.3)
    ax.set_ylabel(ylabel, fontsize=10.5)
    _strip(ax)
    ax.tick_params(axis="y", labelsize=9.5)
    return _save(fig, path)


# ── 패턴 4: 정성 분해표 이미지 (디스카운트 6요인 등) ──────────────────────
def factor_table(path, rows, title="디스카운트 6요인", dir_header="방향", footnote=None):
    """
    rows : list[(name, tag, kind)] — kind in {'keep'(잔존=네이비), 'resolve'(해소=레드)}
    """
    fig, ax = plt.subplots(figsize=(4.3, 2.6), dpi=200)
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8.4)
    ax.add_patch(Rectangle((0, 7.25), 10, 1.15, color=NAVY))
    ax.text(0.3, 7.82, title, color="white", fontsize=12.5, fontweight="bold", va="center")
    ax.text(9.7, 7.82, dir_header, color="white", fontsize=11.5, fontweight="bold",
            va="center", ha="right")
    for i, (name, tag, kind) in enumerate(rows):
        y = 6.3 - i * 1.07
        col = RED if kind == "resolve" else NAVY
        if i % 2 == 0:
            ax.add_patch(Rectangle((0, y - 0.44), 10, 0.88, color=SUB, zorder=0))
        ax.text(0.3, y, name, fontsize=11.5, color="#1a1a1a", va="center")
        ax.text(9.7, y, tag, fontsize=12, color=col, fontweight="bold", va="center", ha="right")
    if footnote:
        ax.text(0.3, 0.12, footnote, fontsize=8.6, color=GREY, va="center")
    ax.add_patch(Rectangle((0, 0), 10, 8.4, fill=False, ec=LINE, lw=1))
    return _save(fig, path)
