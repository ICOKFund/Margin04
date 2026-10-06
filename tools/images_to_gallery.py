#!/usr/bin/env python3
"""여러 장의 이미지를 한 페이지에 순서대로 모은 HTML 파일 1개를 만듭니다.

naver_blog_to_html.py 와 같은 방식으로 이미지를 파일 안에 넣기 때문에(base64)
결과 .html 파일 하나만 카카오톡으로 보내면 받는 사람이 바로 볼 수 있습니다.

사용법:
  python3 tools/images_to_gallery.py 이미지폴더/ --title "제목" --source https://m.blog.naver.com/...
  python3 tools/images_to_gallery.py 1.png 2.png 3.jpg --order given -o shared/이미지모음.html

순서(--order): name = 파일 이름순(기본, 숫자는 크기순), time = 촬영/수정 시각순, given = 입력한 순서
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import re
import sys
from pathlib import Path
from string import Template

from PIL import Image

from naver_blog_to_html import KST, dated_filename, esc, optimize_image

try:  # photos straight from an iPhone/iPad camera may be HEIC
    import pillow_heif

    pillow_heif.register_heif_opener()
except ImportError:
    pillow_heif = None

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".heic", ".heif"}


def natural_key(path: Path):
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", path.name)]


def taken_time(path: Path) -> float:
    try:
        exif = Image.open(path).getexif()
        stamp = exif.get(36867) or exif.get(306)  # DateTimeOriginal, DateTime
        if stamp:
            return dt.datetime.strptime(str(stamp), "%Y:%m:%d %H:%M:%S").timestamp()
    except Exception:
        pass
    return path.stat().st_mtime


def collect(inputs: list[str], order: str) -> list[Path]:
    files: list[Path] = []
    for item in inputs:
        path = Path(item)
        if path.is_dir():
            files += sorted((f for f in path.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTS),
                            key=natural_key)
        elif path.is_file():
            files.append(path)
        else:
            sys.exit(f"파일이나 폴더를 찾을 수 없습니다: {item}")
    if order == "name":
        files.sort(key=natural_key)
    elif order == "time":
        files.sort(key=taken_time)
    return files


PAGE = Template("""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<meta name="referrer" content="no-referrer">
<meta name="robots" content="noindex, nofollow">
<title>$title</title>
<meta property="og:type" content="article">
<meta property="og:title" content="$title">
<meta property="og:description" content="이미지 $count장">
<style>
:root{--bg:#f4f5f7;--card:#fff;--text:#1d2129;--muted:#6b7280;--line:#e2e5e9}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--text);font-size:16px;line-height:1.7;
  font-family:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Pretendard","Noto Sans KR","Malgun Gothic","맑은 고딕",sans-serif;
  word-break:keep-all;overflow-wrap:anywhere}
.wrap{max-width:860px;margin:0 auto;padding:24px 12px 56px}
.head{padding:4px 6px 20px}
.kicker{font-size:13px;font-weight:600;color:var(--muted)}
h1{margin:6px 0 8px;font-size:22px;line-height:1.4;letter-spacing:-.02em}
.meta{font-size:13.5px;color:var(--muted)}
.src{display:inline-block;margin-top:12px;padding:6px 14px;border:1px solid var(--line);border-radius:999px;
  background:var(--card);font-size:13.5px;color:var(--text);text-decoration:none}
figure{margin:0 0 14px;overflow:hidden;border-radius:10px;background:var(--card);box-shadow:0 1px 2px rgba(0,0,0,.06)}
figure img{display:block;max-width:100%;height:auto;margin:0 auto}
figcaption{padding:6px 12px;font-size:12px;color:var(--muted);text-align:right}
footer{margin-top:28px;padding:16px 6px 0;border-top:1px solid var(--line);font-size:12.5px;line-height:1.7;color:var(--muted)}
footer p{margin:0 0 4px}
footer a{color:inherit}
@media (min-width:768px){.wrap{padding-top:40px}h1{font-size:28px}}
</style>
</head>
<body>
<div class="wrap">
<header class="head">
$kicker
<h1>$title</h1>
<div class="meta">$meta</div>
$source_button
</header>
<main>
$figures
</main>
<footer>
$credit
<p>만든 시각: $created (KST)</p>
</footer>
</div>
</body>
</html>
""")


def build_page(files: list[Path], title: str, source: str, author: str, max_width: int, quality: int):
    figures, total_bytes = [], 0
    for i, path in enumerate(files, 1):
        try:
            data, mime, w, h = optimize_image(path.read_bytes(), max_width, quality)
        except Exception as e:
            hint = " (HEIC는 pillow-heif 설치 필요)" if path.suffix.lower() in (".heic", ".heif") else ""
            sys.exit(f"이미지를 읽지 못했습니다: {path}{hint} — {e}")
        total_bytes += len(data)
        src = f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}"
        figures.append(f'<figure id="p{i}"><img src="{src}" alt="이미지 {i}" width="{w}" height="{h}">'
                       f"<figcaption>{i} / {len(files)}</figcaption></figure>")
    link = esc(source)
    source_button = (f'<a class="src" href="{link}" target="_blank" rel="noopener noreferrer">원문 보기 ↗</a>'
                     if source else "")
    # Credit lines only when a source/author is given; leave both out for your own images.
    credit = ""
    if source or author:
        who = (f'<a href="{link}" target="_blank" rel="noopener noreferrer">{esc(author or source)}</a>'
               if source else esc(author))
        credit = f"<p>출처: {who}</p>\n<p>이미지의 저작권은 원작자에게 있습니다.</p>"
    label = author or "이미지 모음"  # small line above the title; skipped when it would repeat the title
    page = PAGE.substitute(
        title=esc(title), count=len(files), meta=f"이미지 {len(files)}장",
        kicker=f'<div class="kicker">{esc(label)}</div>' if label != title else "",
        source_button=source_button, credit=credit, figures="\n".join(figures),
        created=dt.datetime.now(KST).strftime("%Y-%m-%d %H:%M"),
    )
    return page, total_bytes


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="이미지 여러 장을 한 페이지에 모은 단일 HTML 파일을 만듭니다.")
    ap.add_argument("inputs", nargs="+", help="이미지 파일 또는 폴더")
    ap.add_argument("--title", default="이미지 모음", help="페이지 제목")
    ap.add_argument("--source", default="", help="원문 주소 (상단 '원문 보기' 버튼과 하단 출처에 사용)")
    ap.add_argument("--author", default="", help="작성자/블로그 이름")
    ap.add_argument("--order", choices=("name", "time", "given"), default="name", help="이미지 순서")
    ap.add_argument("-o", "--output", help="저장할 파일 경로 (기본: YYMMDD_제목.html)")
    ap.add_argument("--max-width", type=int, default=1440, help="이미지 최대 가로 픽셀 (기본 1440)")
    ap.add_argument("--quality", type=int, default=85, help="JPEG 품질 1-95 (기본 85)")
    args = ap.parse_args(argv)

    files = collect(args.inputs, args.order)
    if not files:
        sys.exit("이미지 파일이 없습니다.")
    page, total_bytes = build_page(files, args.title, args.source, args.author, args.max_width, args.quality)
    out = Path(args.output) if args.output else Path(dated_filename(args.title, fallback="images"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")

    print(f"이미지 {len(files)}장 ({total_bytes / 1024 / 1024:.1f} MB) — 순서:")
    for i, path in enumerate(files, 1):
        print(f"  {i:>2}. {path.name}")
    print(f"저장: {out} ({out.stat().st_size / 1024 / 1024:.2f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
