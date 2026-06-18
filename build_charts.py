#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PDF 삽입용 차트 이미지 생성 (ICOK 네이비 팔레트 + 한글 폰트)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import numpy as np

# 한글 폰트
for path in ["/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
             "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"]:
    try:
        fm.fontManager.addfont(path)
    except Exception:
        pass
plt.rcParams["font.family"] = "NanumGothic"
plt.rcParams["axes.unicode_minus"] = False

PAL = ["#002A52", "#003F7B", "#00509D", "#2E76C1", "#5C8DCA", "#7399CE", "#8AA5D3", "#ABB9DB"]
AST = "/home/user/Margin04/report_assets/"


def base_ax(ax):
    for sp in ["top", "right"]:
        ax.spines[sp].set_visible(False)
    ax.spines["left"].set_color("#666"); ax.spines["bottom"].set_color("#666")
    ax.tick_params(colors="#222", labelsize=9)
    ax.grid(False)


def save(fig, name):
    fig.tight_layout()
    fig.savefig(AST + name, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", name)


# 자료1 연간 실적 (매출 bar + GM% line)
yrs = ["2024A", "2025A", "2026E", "2027E", "2028E"]
rev = [25111, 37378, 115003, 197500, 210000]
gm = [22.4, 39.8, 76.9, 82.9, 80.7]
fig, ax = plt.subplots(figsize=(6.2, 3.0))
base_ax(ax)
ax.bar(yrs, rev, color=PAL[0], width=0.6)
ax.set_ylabel("매출 ($mn)", fontsize=9)
for i, v in enumerate(rev):
    ax.text(i, v, f"{v:,}", ha="center", va="bottom", fontsize=8, color="#002A52")
ax2 = ax.twinx(); ax2.spines["top"].set_visible(False)
ax2.plot(yrs, gm, color=PAL[3], marker="o", ms=6, lw=2, mfc="white")
ax2.set_ylabel("GM%", fontsize=9); ax2.set_ylim(0, 100)
ax2.tick_params(labelsize=9)
for i, v in enumerate(gm):
    ax2.text(i, v + 3, f"{v:.0f}%", ha="center", fontsize=8, color="#2E76C1")
save(fig, "ja1_annual.png")

# 자료7 분기 실적 (매출/OP bar + OPM% line)
q = ["1QFY26", "2QFY26", "3QFY26e", "4QFY26e"]
qrev = [13.6, 23.9, 35.3, 41.7]
qop = [6.4, 16.5, 27.3, 32.4]
opm = [47, 69, 77, 78]
x = np.arange(len(q)); w = 0.38
fig, ax = plt.subplots(figsize=(6.2, 3.0))
base_ax(ax)
ax.bar(x - w/2, qrev, w, label="매출($bn)", color=PAL[0])
ax.bar(x + w/2, qop, w, label="영업이익($bn)", color=PAL[3])
ax.set_xticks(x); ax.set_xticklabels(q); ax.set_ylabel("$bn", fontsize=9)
ax.legend(fontsize=8, frameon=False, loc="upper left")
ax2 = ax.twinx(); ax2.spines["top"].set_visible(False)
ax2.plot(x, opm, color=PAL[5], marker="o", ms=6, lw=2, mfc="white")
ax2.set_ylabel("OPM%", fontsize=9); ax2.set_ylim(0, 100); ax2.tick_params(labelsize=9)
for i, v in enumerate(opm):
    ax2.text(i, v + 3, f"{v}%", ha="center", fontsize=8, color="#7399CE")
save(fig, "ja7_quarter.png")

# 자료8 F3Q26 GS vs Street
cats = ["매출($bn)", "EPS($)"]
gs = [37.6, 22.07]; st = [34.4, 19.74]
x = np.arange(len(cats)); w = 0.36
fig, ax = plt.subplots(figsize=(4.4, 3.0))
base_ax(ax)
b1 = ax.bar(x - w/2, gs, w, label="GS 추정", color=PAL[0])
b2 = ax.bar(x + w/2, st, w, label="스트리트", color=PAL[6])
ax.set_xticks(x); ax.set_xticklabels(cats); ax.legend(fontsize=8, frameon=False)
for b in list(b1) + list(b2):
    ax.text(b.get_x()+b.get_width()/2, b.get_height(), f"{b.get_height():g}", ha="center", va="bottom", fontsize=8)
ax.set_title("F3Q26: GS 추정 vs 스트리트", fontsize=10, color="#002A52")
save(fig, "ja8_beat.png")

# 자료9 F4Q26 guidance vs Street
gs = [48.8, 29.95]; st = [40.4, 23.68]
fig, ax = plt.subplots(figsize=(4.4, 3.0))
base_ax(ax)
b1 = ax.bar(x - w/2, gs, w, label="GS 예상", color=PAL[0])
b2 = ax.bar(x + w/2, st, w, label="스트리트", color=PAL[6])
ax.set_xticks(x); ax.set_xticklabels(cats); ax.legend(fontsize=8, frameon=False)
for b in list(b1) + list(b2):
    ax.text(b.get_x()+b.get_width()/2, b.get_height(), f"{b.get_height():g}", ha="center", va="bottom", fontsize=8)
ax.set_title("F4Q26 가이던스 전망 vs 스트리트", fontsize=10, color="#002A52")
save(fig, "ja9_guide.png")

# 자료11 목표주가
brk = ["Citi", "HSBC", "Goldman Sachs"]; tp = [1200, 1100, 900]
fig, ax = plt.subplots(figsize=(4.6, 2.6))
base_ax(ax)
bars = ax.barh(brk, tp, color=[PAL[0], PAL[2], PAL[4]], height=0.6)
ax.invert_yaxis()
for b, v in zip(bars, tp):
    ax.text(v, b.get_y()+b.get_height()/2, f" ${v:,}", va="center", fontsize=9, color="#002A52")
ax.set_xlim(0, 1400)
ax.set_title("증권사별 목표주가", fontsize=10, color="#002A52")
save(fig, "ja11_tp.png")

# 자료12 EPS 비교
yrs2 = ["FY25A", "FY26E", "FY27E", "FY28E"]
series = {
    "Goldman Sachs": [7.42, 67.48, 138.86, 137.51],
    "HSBC": [7.59, 61.88, 126.82, 142.91],
    "Citi": [7.43, 60.73, 114.73, 117.83],
    "컨센서스": [8.0, 58.0, 106.0, 105.0],
}
x = np.arange(len(yrs2)); w = 0.2
fig, ax = plt.subplots(figsize=(6.2, 3.0))
base_ax(ax)
for i, (k, v) in enumerate(series.items()):
    ax.bar(x + (i-1.5)*w, v, w, label=k, color=PAL[i*2])
ax.set_xticks(x); ax.set_xticklabels(yrs2); ax.set_ylabel("EPS($)", fontsize=9)
ax.legend(fontsize=8, frameon=False, ncol=2)
ax.set_title("증권사별 EPS 추정 비교 (Non-GAAP)", fontsize=10, color="#002A52")
save(fig, "ja12_eps.png")

print("all charts done")
