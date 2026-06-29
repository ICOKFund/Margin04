# -*- coding: utf-8 -*-
"""삼성SDI 리포트 — 네이티브 차트(자료13/14/16/18/19/20)를 ICOK 양식 PNG로 재생성.
DESIGN_SPEC §2(색 토큰)·§4(차트 규칙) 준수: 차트 내 타이틀 금지(캡션 바가 제목),
네이비 팔레트, Pretendard, top/right 스파인 제거 + 옅은 y그리드, 막대/밀집 라벨 흰 박스.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import numpy as np

for c in ["Pretendard", "Malgun Gothic", "NanumGothic"]:
    if c in {f.name for f in fm.fontManager.ttflist}:
        plt.rcParams["font.family"] = c
        break
plt.rcParams["axes.unicode_minus"] = False

# ── ICOK 색 토큰 (DESIGN_SPEC §2) ──────────────────────────────────────────
NAVY = "#002A52"; RED = "#C8101E"; ICOK = "#005EB8"; BLACK = "#1A1A1A"
GREY = "#8A97A6"; GRID = "#E6E9EE"
PAL = ["#002A52", "#00509D", "#2E76C1", "#5C8DCA", "#7399CE", "#8AA5D3", "#ABB9DB"]
WB = dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.92)
AST = "/home/user/Margin04/sdi_assets/"
import os
os.makedirs(AST, exist_ok=True)


def strip(ax, ygrid=True):
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color("#888"); ax.spines["bottom"].set_color("#888")
    if ygrid:
        ax.grid(axis="y", color=GRID, lw=0.6, zorder=0)
    ax.tick_params(colors=BLACK, labelsize=9.5)


def save(fig, name):
    fig.tight_layout(pad=0.4)
    fig.savefig(AST + name, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", name)


# ── 자료13: 연간 매출(bar, 좌) + 영업이익(line, 우) ─────────────────────────
cats = ['’21', '’22', '’23', '’24', '’25', '’26E', '’27E']
rev = [13.6, 20.1, 22.7, 16.6, 13.3, 15.1, 19.2]
op = [1.07, 1.81, 1.63, 0.36, -1.72, -0.48, 1.07]
x = np.arange(len(cats))
fig, ax = plt.subplots(figsize=(4.2, 3.3), dpi=200)
ax.bar(x, rev, width=0.62, color=NAVY, zorder=2)
for i, v in enumerate(rev):
    ax.annotate(f"{v:.1f}", (i, v), textcoords="offset points", xytext=(0, 3),
                ha="center", fontsize=9, color=NAVY, fontweight="bold", bbox=WB, zorder=6)
ax.set_ylabel("매출액 (조원)", fontsize=11, color=NAVY)
ax.set_ylim(0, 27)
ax.set_xticks(x); ax.set_xticklabels(cats, fontsize=9.8)
strip(ax)
ax2 = ax.twinx()
ax2.spines["top"].set_visible(False)
ax2.plot(x, op, color=RED, lw=2.4, marker="o", ms=6, zorder=4)
ax2.axhline(0, color="#888", lw=0.8, zorder=1)
for i, v in enumerate(op):
    dy = 10 if v >= 0 else -14
    ax2.annotate(f"{v:.2f}", (i, v), textcoords="offset points", xytext=(0, dy),
                 ha="center", fontsize=8.6, color=RED, fontweight="bold", bbox=WB, zorder=6)
ax2.set_ylabel("영업이익 (조원)", fontsize=11, color=RED)
ax2.set_ylim(-2.6, 2.6)
ax2.tick_params(labelsize=9.5)
save(fig, "ja13.png")

# ── 자료14: 2025 분기별 사업부 매출 (stacked) ──────────────────────────────
q = ['1Q', '2Q', '3Q', '4Q']
seg = {'소형전지': [713, 920, 972, 957], '자동차(EV)': [1666, 1397, 1202, 1662],
       'ESS': [602, 644, 646, 1004], '전자재료': [196, 218, 232, 237]}
x = np.arange(len(q))
fig, ax = plt.subplots(figsize=(4.2, 3.3), dpi=200)
bottom = np.zeros(len(q))
for i, (k, v) in enumerate(seg.items()):
    ax.bar(x, v, 0.6, bottom=bottom, label=k, color=PAL[i], zorder=2)
    bottom += np.array(v)
for i in range(len(q)):
    ax.annotate(f"{int(bottom[i]):,}", (i, bottom[i]), textcoords="offset points",
                xytext=(0, 3), ha="center", fontsize=8.8, color=NAVY, fontweight="bold",
                bbox=WB, zorder=6)
ax.set_ylabel("매출 (십억원)", fontsize=11, color=NAVY)
ax.set_ylim(0, max(bottom) * 1.15)
ax.set_xticks(x); ax.set_xticklabels(q, fontsize=9.8)
ax.legend(fontsize=8.2, frameon=False, ncol=2, loc="upper center",
          bbox_to_anchor=(0.5, -0.08))
strip(ax)
save(fig, "ja14.png")

# ── 자료16: 가동률별 영업이익 (단일 막대, 음수 그레이) ──────────────────────
util = ['30%', '50%', '60%', '80%', '100%']
opv = [-0.9, -0.2, 0.2, 1.9, 2.6]
x = np.arange(len(util))
cols = [GREY if v < 0 else NAVY for v in opv]
fig, ax = plt.subplots(figsize=(4.2, 3.3), dpi=200)
ax.bar(x, opv, 0.62, color=cols, zorder=2)
ax.axhline(0, color="#444", lw=0.9)
for i, v in enumerate(opv):
    dy = 4 if v >= 0 else -13
    col = RED if v < 0 else NAVY
    ax.annotate(f"{v:+.1f}", (i, v), textcoords="offset points", xytext=(0, dy),
                ha="center", fontsize=9.2, color=col, fontweight="bold", bbox=WB, zorder=6)
ax.text(2.0, -0.75, "BEP ≈ 60%", fontsize=9.5, color=RED, fontweight="bold", ha="center")
ax.set_ylabel("영업이익 (조원)", fontsize=11, color=NAVY)
ax.set_xlabel("가동률", fontsize=10, color=BLACK)
ax.set_ylim(-1.4, 3.1)
ax.set_xticks(x); ax.set_xticklabels(util, fontsize=9.8)
strip(ax)
save(fig, "ja16.png")

# ── 자료18: 수익성 지표 추이 (line markers, 3 series) ──────────────────────
yrs = ['2023', '2024', '2025']
ser = {'영업이익률': [7.2, 2.2, -13.0], '순이익률': [9.1, 3.5, -4.4], 'ROE': [10.4, 2.8, -2.5]}
x = np.arange(len(yrs))
fig, ax = plt.subplots(figsize=(4.2, 3.3), dpi=200)
mk = ['o', 's', '^']
for i, (k, v) in enumerate(ser.items()):
    ax.plot(x, v, color=PAL[i], lw=2.3, marker=mk[i], ms=6, label=k, zorder=4)
    for j in (0, len(v) - 1):   # 끝점만 라벨 (2024 수렴 구간 겹침 방지)
        val = v[j]
        ax.annotate(f"{val:.1f}", (j, val), textcoords="offset points",
                    xytext=(-2 if j == 0 else 2, 8 if val >= 0 else -14),
                    ha="right" if j == 0 else "left", fontsize=8.4,
                    color=PAL[i], fontweight="bold", bbox=WB, zorder=6)
ax.axhline(0, color="#888", lw=0.8)
ax.set_ylabel("비율 (%)", fontsize=11, color=NAVY)
ax.set_ylim(-17, 15)
ax.set_xticks(x); ax.set_xticklabels(yrs, fontsize=9.8)
ax.legend(fontsize=8.4, frameon=False, ncol=3, loc="upper center",
          bbox_to_anchor=(0.5, -0.08))
strip(ax)
save(fig, "ja18.png")

# ── 자료19: 매출·총자산 추이 (clustered 2 series) ──────────────────────────
yrs = ['’23', '’24', '’25', '’26E', '’27E']
rev = [22.7, 16.6, 13.3, 15.1, 19.2]
asset = [34.0, 38.4, 42.0, 43.7, 47.1]
x = np.arange(len(yrs)); w = 0.38
fig, ax = plt.subplots(figsize=(4.2, 3.3), dpi=200)
b1 = ax.bar(x - w/2, rev, w, label="매출액", color=NAVY, zorder=2)
b2 = ax.bar(x + w/2, asset, w, label="총자산", color=PAL[3], zorder=2)
for b in list(b1) + list(b2):
    ax.annotate(f"{b.get_height():.1f}", (b.get_x()+b.get_width()/2, b.get_height()),
                textcoords="offset points", xytext=(0, 2), ha="center", fontsize=7.8,
                color=NAVY, fontweight="bold", bbox=WB, zorder=6)
ax.set_ylabel("금액 (조원)", fontsize=11, color=NAVY)
ax.set_ylim(0, 53)
ax.set_xticks(x); ax.set_xticklabels(yrs, fontsize=9.8)
ax.legend(fontsize=8.6, frameon=False, ncol=2, loc="upper left")
strip(ax)
save(fig, "ja19.png")

# ── 자료20: CAPEX 추이 (단일 막대) ─────────────────────────────────────────
yrs = ['’21', '’22', '’23', '’24', '’25']
capex = [2.25, 2.63, 4.05, 6.27, 3.27]
x = np.arange(len(yrs))
fig, ax = plt.subplots(figsize=(4.2, 3.3), dpi=200)
ax.bar(x, capex, 0.62, color=NAVY, zorder=2)
for i, v in enumerate(capex):
    ax.annotate(f"{v:.2f}", (i, v), textcoords="offset points", xytext=(0, 3),
                ha="center", fontsize=9, color=NAVY, fontweight="bold", bbox=WB, zorder=6)
ax.set_ylabel("CAPEX (조원)", fontsize=11, color=NAVY)
ax.set_ylim(0, 7.2)
ax.set_xticks(x); ax.set_xticklabels(yrs, fontsize=9.8)
strip(ax)
save(fig, "ja20.png")

print("all SDI charts done")
