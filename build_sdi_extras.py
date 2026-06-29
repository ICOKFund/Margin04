# -*- coding: utf-8 -*-
"""자료34(실적표)·자료35(리스크 매트릭스)를 ICOK 네이비 표 이미지로 재생성하고,
자료32·33(외부 출처 차트)은 데이터 보존한 채 색만 ICOK 토큰으로 보정.
DESIGN_SPEC §2 색 토큰 / §8 표 양식 준수.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Rectangle, Circle
from PIL import Image
import numpy as np

for c in ["Pretendard", "Malgun Gothic", "NanumGothic"]:
    if c in {f.name for f in fm.fontManager.ttflist}:
        plt.rcParams["font.family"] = c
        break
plt.rcParams["axes.unicode_minus"] = False

NAVY = "#002A52"; RED = "#C8101E"; ICOK = "#005EB8"; BLACK = "#1A1A1A"
BAND = "#CFE0F2"; SUB = "#EAF1FA"; LINE = "#C2CCD8"; GREY = "#8A97A6"
AST = "/home/user/Margin04/sdi_assets/"


# ── 자료34: 삼성SDI 분기·연간 실적 추이 (표) ──────────────────────────────
def build_ja34():
    rows = [
        ("25.1Q 전사", "3조 1,768억", "−4,341억", "", False),
        ("25.1Q 배터리부문", "2조 9,809억", "−4,524억", "YoY −34.9%, QoQ −16.4%", True),
        ("25.4Q 전사", "3조 8,587억", "−2,992억", "", False),
        ("25 연간", "13조 2,667억", "−1조 7,224억", "", True),
        ("26.1Q 전사", "3조 5,764억", "−1,556억", "적자 64.2% 축소·순익 흑전", False),
        ("26.1Q 배터리", "3조 3,544억", "−1,766억", "", True),
        ("26.1Q 전자재료", "2,220억", "+210억", "EV둔화 완충축", False),
    ]
    heads = ["구분", "매출", "영업손익", "비고"]
    xcol = [0.20, 2.6, 4.6, 6.55]   # 열 좌측 기준 x (총 10 단위)
    align = ["left", "right", "right", "left"]
    xref = [0.20, 4.4, 6.4, 6.55]   # 우측정렬 기준 x
    n = len(rows)
    fig, ax = plt.subplots(figsize=(8.2, 2.5), dpi=200)
    ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0, n + 1.2)
    rowh = 1.0
    top = n + 1.2
    # 헤더 바
    ax.add_patch(Rectangle((0, top - 1.0), 10, 1.0, color=NAVY, zorder=2))
    for j, htext in enumerate(heads):
        hx = xref[j] if align[j] == "right" else xcol[j]
        ax.text(hx, top - 0.5, htext, color="white", fontsize=11, fontweight="bold",
                va="center", ha=align[j], zorder=3)
    # 데이터 행
    for i, (g, rev, op, note, emph) in enumerate(rows):
        y = top - 1.0 - (i + 0.5) * rowh
        if emph:
            ax.add_patch(Rectangle((0, y - rowh/2), 10, rowh, color=BAND, zorder=0))
        elif i % 2 == 1:
            ax.add_patch(Rectangle((0, y - rowh/2), 10, rowh, color=SUB, zorder=0))
        fw = "bold" if emph else "normal"
        ax.text(xcol[0], y, g, fontsize=10.2, color=BLACK, va="center", ha="left",
                fontweight=fw, zorder=3)
        ax.text(xref[1], y, rev, fontsize=10.2, color=BLACK, va="center", ha="right",
                fontweight=fw, zorder=3)
        opcol = RED if op.strip().startswith("−") else NAVY
        ax.text(xref[2], y, op, fontsize=10.2, color=opcol, va="center", ha="right",
                fontweight="bold", zorder=3)
        if note:
            ax.text(xcol[3], y, note, fontsize=8.8, color=GREY, va="center", ha="left",
                    zorder=3)
    ax.add_patch(Rectangle((0, 0.2), 10, top - 0.2, fill=False, ec=LINE, lw=1, zorder=4))
    fig.tight_layout(pad=0.3)
    fig.savefig(AST + "ja34.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig); print("saved ja34.png")


# ── 자료35: 리스크 매트릭스 (가능성=네이비 점 / 영향도=레드 점, 5점 척도) ──
def build_ja35():
    rows = [
        ("EV 수요 회복 지연", 4, 5, "유럽·북미 BEV 월별 등록대수 MoM", "ESS 매출 비중 확대·고정비 절감"),
        ("헝가리 수율·가동률 지연", 4, 5, "분기 가동률 공시(목표 70%+)·수율 공개", "수율 개선 로드맵 공개·NDR 설명"),
        ("중국 업체 가격경쟁 심화", 5, 4, "CATL·BYD ASP, LFP 셀 스팟가격 추이", "하이엔드 믹스 강화·고객사 다변화"),
        ("IRA/AMPC 정책 변화", 3, 5, "미 의회 IRA 개정안 입법 동향(분기)", "스텔란티스 JV 구조·수혜사업 분산"),
        ("ESS 마진 기대치 하회", 3, 4, "ESS 사업부 OPM 5%+ 여부(분기)", "LFP SBB 원가 재설계·수주조건 검토"),
    ]
    heads = ["리스크 항목", "가능성", "영향도", "확인 지표", "회사 대응 포인트"]
    n = len(rows)
    fig, ax = plt.subplots(figsize=(8.4, 4.05), dpi=200)
    ax.axis("off"); ax.set_xlim(0, 20); ax.set_ylim(0, n + 1.3)
    # 열 x중심
    cx = {"name": 0.2, "poss": 5.6, "imp": 8.7, "ind": 11.0, "resp": 15.7}
    top = n + 1.3
    ax.add_patch(Rectangle((0, top - 1.0), 20, 1.0, color=NAVY, zorder=2))
    ax.text(cx["name"], top - 0.5, heads[0], color="white", fontsize=10.5, fontweight="bold", va="center", ha="left", zorder=3)
    ax.text(cx["poss"], top - 0.5, heads[1], color="white", fontsize=10.5, fontweight="bold", va="center", ha="center", zorder=3)
    ax.text(cx["imp"], top - 0.5, heads[2], color="white", fontsize=10.5, fontweight="bold", va="center", ha="center", zorder=3)
    ax.text(cx["ind"], top - 0.5, heads[3], color="white", fontsize=10.5, fontweight="bold", va="center", ha="left", zorder=3)
    ax.text(cx["resp"], top - 0.5, heads[4], color="white", fontsize=10.5, fontweight="bold", va="center", ha="left", zorder=3)

    def dots(ax, xc, y, k, color):
        gap = 0.62
        x0 = xc - gap * 2
        for d in range(5):
            filled = d < k
            ax.add_patch(Circle((x0 + d * gap, y), 0.20,
                                 facecolor=color if filled else "#FFFFFF",
                                 edgecolor=color if filled else "#C2CCD8",
                                 lw=1.0, zorder=3))

    for i, (name, poss, imp, ind, resp) in enumerate(rows):
        y = top - 1.0 - (i + 0.5) * 1.0
        if i % 2 == 1:
            ax.add_patch(Rectangle((0, y - 0.5), 20, 1.0, color=SUB, zorder=0))
        ax.text(cx["name"], y, name, fontsize=9.6, color=BLACK, va="center", ha="left", fontweight="bold", zorder=3)
        dots(ax, cx["poss"], y, poss, NAVY)
        dots(ax, cx["imp"], y, imp, RED)
        ax.text(cx["ind"], y, ind, fontsize=8.5, color="#333", va="center", ha="left", zorder=3)
        ax.text(cx["resp"], y, resp, fontsize=8.5, color="#333", va="center", ha="left", zorder=3)
    ax.add_patch(Rectangle((0, 0.15), 20, top - 0.15, fill=False, ec=LINE, lw=1, zorder=4))
    # 범례
    ax.text(0.2, 0.4, "● 가능성(네이비) · ● 영향도(레드) — 5점 척도", fontsize=8, color=GREY, va="center")
    fig.tight_layout(pad=0.3)
    fig.savefig(AST + "ja35.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig); print("saved ja35.png")


# ── 자료32/33: 색 보정 (데이터·형태 보존) ─────────────────────────────────
def recolor(src, dst, mapping, tol=40):
    im = Image.open(src).convert("RGB")
    a = np.array(im).astype(int)
    out = a.copy()
    for (sr, sg, sb), (tr, tg, tb) in mapping:
        d = (np.abs(a[:, :, 0] - sr) + np.abs(a[:, :, 1] - sg) + np.abs(a[:, :, 2] - sb))
        m = d < tol
        out[m] = [tr, tg, tb]
    Image.fromarray(out.astype("uint8")).save(dst)
    print("saved", dst.split("/")[-1])


def hexrgb(h):
    h = h.lstrip("#"); return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


# 자료32: 보라 PHEV → 네이비팔레트(#7399CE), 하이퍼링크 파랑 축라벨 → 검정
recolor("/tmp/qa_smoke/imgs/s20_0.png", AST + "ja32.png", [
    ((160, 107, 154), hexrgb("#7399CE")),   # PHEV 보라
    ((0, 34, 255), (51, 51, 51)),            # 축라벨 파랑
    ((13, 45, 255), (51, 51, 51)),
    ((8, 41, 255), (51, 51, 51)),
    ((135, 151, 255), (120, 120, 120)),      # 라벨 밑줄 연한 파랑
], tol=70)

# 자료33: 미디엄블루 라인 → NAVY, 면적 채움은 옅은 밴드 유지
recolor("/tmp/qa_smoke/imgs/s20_1.png", AST + "ja33.png", [
    ((25, 92, 165), hexrgb("#002A52")),      # 라인 블루 → 네이비
], tol=55)

build_ja34()
build_ja35()
print("extras done")
