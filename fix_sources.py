# -*- coding: utf-8 -*-
"""출처 표기를 DESIGN_SPEC §5 형식으로 정리.
- 원본 파일명/비공식('팀 PDF') 제거, 단일 증권사명 일반화('증권사'), 말미 ', ICOK' 보장.
- 런 단위로 첫 런 텍스트만 교체해 서식(그레이 8~9pt) 보존. ※ 주석 단락은 미변경.
"""
from pptx import Presentation

SRC = "/home/user/Margin04/ICOK_삼성SDI_006400.pptx"

# (slide_index, 현재텍스트 고유부분) -> 새 텍스트
FIX = [
    (2, "LS증권", "출처: SNE Research·BloombergNEF·증권사 전망(2026F), ICOK"),
    (4, "삼성증권", "출처: ACEA·SNE Research·증권사(2026.2월 기준), ICOK"),
    (8, "삼성SDI뉴스", "출처: 삼성SDI 실적발표(2025), ICOK"),
    (8, "SK증권 리서치 2025", "출처: 증권사 리서치, ICOK"),
    (9, "삼성SDI 실적발표·DART", "출처: 삼성SDI 실적발표·DART, ICOK"),
    (9, "팀 PDF(삼성SDI·IBK)", "출처: 삼성SDI·증권사, ICOK"),
    (10, "팀 PDF(삼성SDI 추정)", "출처: 삼성SDI·ICOK 추정"),
    (10, "출처: 팀 PDF", "출처: ICOK 추정"),
    (11, "DART·증권사. ROA", "출처: DART·증권사, ROA/ROE/회전율 ICOK 자체 산정"),
    (11, "DART·자체 산정", "출처: DART, ICOK 자체 산정"),
    (12, "DART·KB증권·컨센서스", "출처: DART·증권사 컨센서스, ICOK"),
    (12, "DART 사업보고서", "출처: DART 사업보고서, ICOK"),
]


def set_para_text(para, txt):
    """단락 첫 런 텍스트 교체 + 나머지 런 제거(서식 유지)."""
    if para.runs:
        para.runs[0].text = txt
        for r in para.runs[1:]:
            r._r.getparent().remove(r._r)
    else:
        para.add_run().text = txt


prs = Presentation(SRC)
done = []
for si, key, new in FIX:
    s = prs.slides[si]
    hit = False
    for sh in s.shapes:
        if not sh.has_text_frame:
            continue
        for para in sh.text_frame.paragraphs:
            if key in para.text and para.text.strip().startswith("출처"):
                old = para.text
                set_para_text(para, new)
                done.append((si, old[:40], new))
                hit = True
                break
        if hit:
            break
    if not hit:
        print(f"  [MISS] slide {si} key='{key}'")

for si, old, new in done:
    print(f"slide {si}: '{old}...' -> '{new}'")
print("fixed:", len(done), "/", len(FIX))
prs.save(SRC)
print("saved")
