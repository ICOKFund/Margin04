# -*- coding: utf-8 -*-
"""
ICOK 리포트 QA 모듈/CLI (DESIGN_SPEC §9)
렌더 → 페이지 PNG → 자료 하단 크롭 → 폰트 임베딩 검증.

CLI:
    set PYTHONUTF8=1
    python qa.py "리포트.pptx"            # 전체 렌더 + 폰트검증
    python qa.py "리포트.pptx" 17         # 17페이지 하단(자료) 크롭까지

체크리스트(육안 점검):
  ① 차트 내 모든 라벨 또렷·겹침無 (특히 막대 위 라벨 = 흰 박스)
  ② 자료 하단 정렬·2-up 폭 일치   ③ 캡션/출처 형식
  ④ 본문 ICOK블루 소제목          ⑤ 수치 정합(차트=표=본문)
  ⑥ 폰트 임베딩 유지              ⑦ 슬라이드 순서·자료 번호 연속
"""
import os
import sys
import glob
import shutil
import subprocess
import zipfile

# Windows LibreOffice 기본 경로(필요시 수정). Unix 래퍼는 AF_UNIX 실패 → soffice.exe 직접.
SOFFICE = r"C:\Program Files\LibreOffice\program\soffice.exe"


def render(pptx, outdir="qa_out", dpi=160):
    """pptx → pdf → 페이지별 png. 생성된 png 경로 목록 반환."""
    os.makedirs(outdir, exist_ok=True)
    soffice = SOFFICE if os.path.exists(SOFFICE) else "soffice"
    subprocess.run([soffice, "--headless", "--convert-to", "pdf",
                    "--outdir", outdir, pptx], check=True)
    pdfs = sorted(glob.glob(os.path.join(outdir, "*.pdf")), key=os.path.getmtime)
    pdf = pdfs[-1]   # 한글 파일명 깨질 수 있어 최신본 사용
    subprocess.run(["pdftoppm", "-png", "-r", str(dpi), pdf,
                    os.path.join(outdir, "pg")], check=True)
    return sorted(glob.glob(os.path.join(outdir, "pg-*.png")))


def crop_bottom(png, frac=0.70, out=None):
    """자료(하단) 가독성 점검용 — 페이지 하단 영역만 크롭."""
    from PIL import Image
    im = Image.open(png)
    w, h = im.size
    out = out or png.replace(".png", "_crop.png")
    im.crop((0, int(h * frac), w, h)).save(out)
    return out


def verify_fonts(pptx):
    """임베딩 폰트(.fntdata) 크기 목록. 완전 임베드면 MB 단위 값 존재."""
    z = zipfile.ZipFile(pptx)
    return [z.getinfo(n).file_size for n in z.namelist() if n.endswith(".fntdata")]


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    pptx = sys.argv[1]
    fs = verify_fonts(pptx)
    ok = bool(fs) and max(fs) > 500_000
    print(f"[FONT] .fntdata {len(fs)}개, 최대 {max(fs) if fs else 0:,} bytes "
          f"→ {'임베딩 OK' if ok else '⚠ 임베딩 확인 필요'}")
    pngs = render(pptx)
    print(f"[RENDER] {len(pngs)} pages → qa_out/")
    if len(sys.argv) > 2:
        pg = int(sys.argv[2])
        cand = [p for p in pngs if f"-{pg}." in p or f"-{pg:02d}." in p]
        if cand:
            print(f"[CROP] {crop_bottom(cand[0])}")
        else:
            print(f"[CROP] page {pg} not found")


if __name__ == "__main__":
    main()
