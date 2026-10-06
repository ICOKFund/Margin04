#!/usr/bin/env python3
"""네이버 블로그 글 하나를 '본문만' 담은 HTML 파일 1개로 저장합니다.

이미지까지 파일 안에 넣기 때문에(base64) 결과 .html 파일 하나만 카카오톡
채팅방에 보내면 받는 사람이 탭해서 바로 볼 수 있습니다. 외부 CSS·폰트·
JavaScript를 쓰지 않으므로 오프라인에서도, 어느 브라우저에서도 같은 모습입니다.

사용법:
  python3 tools/naver_blog_to_html.py https://m.blog.naver.com/<블로그ID>/<글번호>
  python3 tools/naver_blog_to_html.py <글 주소> -o shared/파일이름.html
  python3 tools/naver_blog_to_html.py <글 주소> --input 저장해둔페이지.html

필요 패키지: requests, beautifulsoup4, lxml, Pillow
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import html
import io
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from string import Template
from urllib.parse import parse_qs, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup, Comment, NavigableString, Tag
from PIL import Image, ImageOps

KST = dt.timezone(dt.timedelta(hours=9))
MOBILE_UA = (
    "Mozilla/5.0 (Linux; Android 14; SM-S918N) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36"
)
DESKTOP_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
)
REFERER = "https://blog.naver.com/"
BODY_SELECTORS = (
    "div.se-main-container",  # SmartEditor ONE (2018~)
    "div.se_component_wrap.sect_dsc",  # SmartEditor 3
    "div#postViewArea",  # SmartEditor 2
    "div.post_ct",  # old mobile layout
)
NAVER_IMAGE_HOSTS = ("postfiles.pstatic.net", "mblogthumb-phinf.pstatic.net")
INVISIBLE = dict.fromkeys(map(ord, "\u200b\u200c\u200d\u2060\ufeff"), None)
COLOR = r"(#[0-9a-fA-F]{3,8}\b|rgba?\([\d\s.,%]+\))"
FS_BASE = 15  # SmartEditor ONE default body size (se-fs-fs15)
BLANK = '<p class="blank"></p>'
GENERIC_BLOCKS = {
    "p", "div", "section", "article", "center", "h1", "h2", "h3", "h4", "h5", "h6",
    "blockquote", "table", "ul", "ol", "hr", "figure", "pre",
}


# --------------------------------------------------------------------------- helpers

def esc(s) -> str:
    return html.escape(str(s or ""), quote=True)


def squash(s) -> str:
    return re.sub(r"\s+", " ", str(s or "").translate(INVISIBLE)).strip()


def classes(el) -> list[str]:
    return el.get("class", []) if isinstance(el, Tag) else []


def absolute(url) -> str:
    url = (url or "").strip()
    return "https:" + url if url.startswith("//") else url


def safe_href(href) -> str:
    href = absolute(href)
    return href if urlparse(href).scheme.lower() in ("http", "https", "mailto", "tel") else ""


def img_src(img) -> str:
    if not isinstance(img, Tag):
        return ""
    for attr in ("data-lazy-src", "data-src", "data-original", "src"):
        value = (img.get(attr) or "").strip()
        if value and not value.startswith("data:"):
            return absolute(value)
    return ""


def upgrade_naver_image(url: str, size: str = "w966") -> str:
    """Ask Naver's image CDN for a large rendition instead of the lazy-load placeholder."""
    u = urlparse(url)
    return urlunparse(u._replace(query=f"type={size}")) if u.hostname in NAVER_IMAGE_HOSTS else url


def image_candidates(url: str) -> list[str]:
    """postfiles/mblogthumb serve the same files; try the other host if one refuses."""
    u = urlparse(url)
    if u.hostname not in NAVER_IMAGE_HOSTS:
        return [url]
    other = next(h for h in NAVER_IMAGE_HOSTS if h != u.hostname)
    return [url, urlunparse(u._replace(netloc=other))]


def json_attr(el, attr) -> dict:
    raw = el.get(attr) if isinstance(el, Tag) else None
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def module_data(comp) -> dict:
    """SmartEditor ONE keeps media metadata as JSON in a data-module attribute."""
    el = comp.select_one("script.__se_module_data[data-module]") or comp.select_one("[data-module]")
    data = json_attr(el, "data-module")
    return data["data"] if isinstance(data.get("data"), dict) else data


def first_text(root, *selectors) -> str:
    for sel in selectors:
        for el in root.select(sel):
            text = squash(el.get_text(" "))
            if text:
                return text
    return ""


def get_meta(soup, *keys) -> str:
    for key in keys:
        tag = soup.find("meta", attrs={"property": key}) or soup.find("meta", attrs={"name": key})
        if tag and (tag.get("content") or "").strip():
            return tag["content"].strip()
    return ""


def align_of(el) -> str:
    for cls in classes(el):
        m = re.search(r"align-(left|center|right|justify)$", cls)
        if m:
            return m.group(1)
    style = el.get("style", "") if isinstance(el, Tag) else ""
    m = re.search(r"text-align\s*:\s*(left|center|right|justify)", style or "")
    return m.group(1) if m else ""


def align_style(el) -> str:
    align = align_of(el)
    return f' style="text-align:{align}"' if align in ("center", "right", "justify") else ""


def font_size_em(el):
    for cls in classes(el):
        m = re.fullmatch(r"se-fs-?(?:fs)?(\d{2})", cls)
        if m:
            px = int(m.group(1))
            return None if px == FS_BASE else round(max(0.8, min(px / FS_BASE, 2.0)), 3)
    return None


def inline_style(el) -> str:
    """Keep only the presentational bits that carry meaning: colour, emphasis, size."""
    style = el.get("style", "") or ""
    css = []
    m = re.search(r"(?<![\w-])color\s*:\s*" + COLOR, style)
    if m:
        css.append(f"color:{m.group(1)}")
    m = re.search(r"background(?:-color)?\s*:\s*" + COLOR, style)
    if m:
        css.append(f"background-color:{m.group(1)}")
    if re.search(r"font-weight\s*:\s*(bold|[6-9]00)", style):
        css.append("font-weight:700")
    if re.search(r"font-style\s*:\s*italic", style):
        css.append("font-style:italic")
    m = re.search(r"text-decoration(?:-line)?\s*:\s*([^;]+)", style)
    if m:
        lines = [d for d in ("underline", "line-through") if d in m.group(1)]
        if lines:
            css.append("text-decoration:" + " ".join(lines))
    size = font_size_em(el)
    if size:
        css.append(f"font-size:{size}em")
    return ";".join(css)


def is_blank(fragment: str) -> bool:
    if "<img" in fragment:
        return False
    text = html.unescape(re.sub(r"<[^>]+>", "", fragment))
    return not text.replace("\xa0", " ").strip()


def tidy_blanks(blocks: list[str], keep_blank: bool = True) -> list[str]:
    """Blank paragraphs are the author's spacing: keep at most two in a row, trim the ends."""
    out, run = [], 0
    for block in blocks:
        if block == BLANK:
            run += 1
            if keep_blank and run <= 2:
                out.append(block)
        else:
            run = 0
            out.append(block)
    while out and out[0] == BLANK:
        out.pop(0)
    while out and out[-1] == BLANK:
        out.pop()
    return out


def optimize_image(data: bytes, max_width: int, quality: int):
    """Return (bytes, mime, width, height), downscaled to max_width and re-encoded compactly."""
    im = Image.open(io.BytesIO(data))
    fmt = (im.format or "").upper()
    if fmt == "GIF" and getattr(im, "n_frames", 1) > 1:
        return data, "image/gif", im.width, im.height  # keep the animation
    im = ImageOps.exif_transpose(im)
    alpha = im.mode in ("RGBA", "LA", "PA") or (im.mode == "P" and "transparency" in im.info)
    im = im.convert("RGBA" if alpha else "RGB")
    if alpha and im.getextrema()[3][0] == 255:  # alpha channel present but fully opaque
        alpha, im = False, im.convert("RGB")
    resized = im.width > max_width
    if resized:
        im = im.resize((max_width, round(im.height * max_width / im.width)), Image.LANCZOS)

    def encode(kind, **opts):
        buf = io.BytesIO()
        im.save(buf, kind, **opts)
        return buf.getvalue()

    if alpha:
        return encode("PNG", optimize=True), "image/png", im.width, im.height
    jpeg = encode("JPEG", quality=quality, optimize=True, progressive=True)
    if fmt == "JPEG" and not resized and len(data) <= len(jpeg) * 1.25:
        return data, "image/jpeg", im.width, im.height  # original is already compact
    if fmt != "JPEG":
        # Screenshots and charts stay sharp as PNG unless that is much heavier.
        png = encode("PNG", optimize=True)
        if len(png) <= len(jpeg) * 1.3:
            return png, "image/png", im.width, im.height
    return jpeg, "image/jpeg", im.width, im.height


def parse_naver_date(text: str, now: dt.datetime | None = None):
    """Return (datetime, exact) from '2026. 10. 5. 21:30' or relative forms like '3시간 전'."""
    now = now or dt.datetime.now(KST)
    t = squash(text)
    m = re.search(r"(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})\.?(?:\s*(\d{1,2}):(\d{2}))?", t)
    if m:
        moment = dt.datetime(int(m[1]), int(m[2]), int(m[3]), int(m[4] or 0), int(m[5] or 0), tzinfo=KST)
        return moment, m[4] is not None
    m = re.search(r"(\d+)\s*(분|시간|일)\s*전", t)
    if m:
        unit = {"분": "minutes", "시간": "hours", "일": "days"}[m[2]]
        return now - dt.timedelta(**{unit: int(m[1])}), False
    if "방금" in t:
        return now, False
    return None, False


# --------------------------------------------------------------------------- fetching

def parse_post_url(url: str) -> tuple[str, str]:
    u = urlparse(url)
    qs = parse_qs(u.query)
    if qs.get("blogId") and qs.get("logNo"):
        return qs["blogId"][0], qs["logNo"][0]
    m = re.match(r"/([A-Za-z0-9_-]+)/(\d+)", u.path)
    if (u.hostname or "").endswith("blog.naver.com") and m:
        return m.group(1), m.group(2)
    sys.exit(f"네이버 블로그 글 주소 형식이 아닙니다: {url}")


def fetch_post(session: requests.Session, blog_id: str, log_no: str) -> tuple[str, str]:
    candidates = [
        (f"https://m.blog.naver.com/{blog_id}/{log_no}", MOBILE_UA),
        (f"https://blog.naver.com/PostView.naver?blogId={blog_id}&logNo={log_no}"
         "&redirect=Dlog&widgetTypeCall=true&directAccess=false", DESKTOP_UA),
    ]
    errors = []
    for url, ua in candidates:
        try:
            r = session.get(url, headers={"User-Agent": ua, "Referer": REFERER}, timeout=30)
            r.raise_for_status()
        except requests.RequestException as e:
            errors.append(f"{url}\n    -> {e}")
            continue
        text = r.content.decode("utf-8", errors="replace")
        if any(marker in text for marker in ("se-main-container", "se_component_wrap", "postViewArea", "post_ct")):
            return text, url
        errors.append(f"{url}\n    -> 본문 영역이 없습니다 (비공개 글이거나 주소가 다를 수 있습니다)")
    sys.exit("글을 가져오지 못했습니다.\n  " + "\n  ".join(errors))


def find_body(soup):
    for sel in BODY_SELECTORS:
        el = soup.select_one(sel)
        if el is not None:
            return sel, el
    return None, None


@dataclass
class PostMeta:
    url: str
    title: str = ""
    blog_name: str = ""
    author: str = ""
    date: dt.datetime | None = None
    date_exact: bool = False
    category: str = ""
    tags: list[str] = field(default_factory=list)

    @property
    def date_label(self) -> str:
        if not self.date:
            return ""
        d = self.date
        label = f"{d.year}. {d.month}. {d.day}."
        return f"{label} {d:%H:%M}" if self.date_exact else label


def extract_meta(soup, blog_id: str, log_no: str) -> PostMeta:
    meta = PostMeta(url=f"https://m.blog.naver.com/{blog_id}/{log_no}")
    suffix = re.compile(r"\s*[:|]\s*네이버\s*블로그\s*$")
    meta.title = (
        first_text(soup, ".se-documentTitle .se-title-text", ".se-title-text", ".se_title .se_textarea",
                   ".pcol1.itemSubjectBoldfont", ".htitle", ".tit_h3")
        or suffix.sub("", get_meta(soup, "og:title"))
        or suffix.sub("", squash(soup.title.string if soup.title else ""))
        or "제목 없음"
    )
    meta.author = (
        get_meta(soup, "naverblog:nickname")
        or first_text(soup, ".se-documentTitle .nick", ".blog_author .ell", ".nick", ".writer")
        or blog_id
    )
    site = get_meta(soup, "og:site_name")
    names = [p.strip() for p in re.split(r"[|:]", site) if p.strip() and "네이버" not in p and "NAVER" not in p.upper()]
    meta.blog_name = names[0] if names else ""

    _, body = find_body(soup)
    for el in soup.select('[class*="date"]'):
        if body is not None and any(parent is body for parent in el.parents):
            continue  # a date written inside the post body is not the publish date
        moment, exact = parse_naver_date(el.get_text(" "))
        if moment:
            meta.date, meta.date_exact = moment, exact
            break

    category = first_text(soup, ".blog_category", ".category_name", "a.pcol2[href*='categoryNo']")
    meta.category = category if len(category) <= 40 else ""

    seen = []
    for el in soup.select(".post_tag a, .wrap_tag a, [id^='tagList_'] a, .tag_area a, .item_tag"):
        tag = squash(el.get_text(" "))
        if tag:
            tag = tag if tag.startswith("#") else "#" + tag
            if tag not in seen:
                seen.append(tag)
    meta.tags = seen
    return meta


# --------------------------------------------------------------------------- body conversion

class Converter:
    def __init__(self, session, page_url, max_width=1080, quality=85, embed=True):
        self.session = session
        self.page_url = page_url
        self.max_width = max_width
        self.quality = quality
        self.embed = embed
        self.cache: dict[str, tuple[str, int | None, int | None]] = {}
        self.stats: Counter = Counter()
        self.warnings: list[str] = []
        self.handlers = {
            "documentTitle": lambda comp: "",  # shown in the page header instead
            "text": self.c_text,
            "sectionTitle": self.c_section_title,
            "quotation": self.c_quotation,
            "image": self.c_image,
            "imageStrip": self.c_image_strip,
            "imageGroup": self.c_image_group,
            "sticker": self.c_sticker,
            "horizontalLine": lambda comp: '<hr class="c">',
            "table": self.c_table,
            "oglink": self.c_oglink,
            "video": self.c_video,
            "gif": self.c_gif,
            "oembed": self.c_oembed,
            "code": self.c_code,
            "file": self.c_file,
            "placesMap": self.c_place,
            "map": self.c_place,
            "material": self.c_material,
        }

    # ---- images

    def fetch_image(self, url: str):
        """Return (src, width, height); src is a data: URI when the download succeeded."""
        url = absolute(url)
        if url in self.cache:
            return self.cache[url]
        result, error = (url, None, None), None
        if self.embed:
            for candidate in image_candidates(url):
                try:
                    r = self.session.get(candidate, headers={"User-Agent": MOBILE_UA, "Referer": REFERER},
                                         timeout=30)
                    r.raise_for_status()
                    data, mime, w, h = optimize_image(r.content, self.max_width, self.quality)
                except Exception as e:  # network error, HTML error page, unreadable image...
                    error = e
                    continue
                result = (f"data:{mime};base64,{base64.b64encode(data).decode('ascii')}", w, h)
                self.stats["images_embedded"] += 1
                self.stats["image_bytes"] += len(data)
                break
            else:
                self.stats["images_linked"] += 1
                self.warnings.append(f"이미지를 내려받지 못해 원본 주소로 연결했습니다: {url} ({error})")
        self.cache[url] = result
        return result

    def img_tag(self, url: str, alt: str = "", cls: str = "", style: str = "") -> str:
        src, w, h = self.fetch_image(url)
        attrs = [f'src="{esc(src)}"', f'alt="{esc(alt)}"']
        if w and h:
            attrs += [f'width="{w}"', f'height="{h}"']
        if cls:
            attrs.append(f'class="{cls}"')
        if style:
            attrs.append(f'style="{style}"')
        return f"<img {' '.join(attrs)}>"

    def image_info(self, mod):
        img = mod.find("img")
        info = json_attr(mod.select_one("a[data-linkdata]"), "data-linkdata")
        url = absolute(info.get("src")) or img_src(img)
        href = safe_href(info.get("link")) if str(info.get("linkUse", "")).lower() == "true" else ""
        alt = (img.get("alt") or "") if img else ""
        return (upgrade_naver_image(url) if url else ""), alt, href

    def image_html(self, mod, style: str = "") -> str:
        url, alt, href = self.image_info(mod)
        if not url:
            return ""
        if not href:
            return self.img_tag(url, alt, style=style)
        style_attr = f' style="{style}"' if style else ""
        return (f'<a href="{esc(href)}" target="_blank" rel="noopener noreferrer"{style_attr}>'
                f'{self.img_tag(url, alt)}</a>')

    def caption(self, el) -> str:
        lines = self.paragraph_inners(el) if el is not None else []
        return f"<figcaption>{'<br>'.join(lines)}</figcaption>" if lines else ""

    # ---- text

    def inline(self, el) -> str:
        return "".join(self.inline_node(node) for node in el.children)

    def inline_node(self, node) -> str:
        if isinstance(node, Comment):
            return ""
        if isinstance(node, NavigableString):
            return html.escape(str(node).translate(INVISIBLE), quote=False)
        if not isinstance(node, Tag) or node.name in ("script", "style", "button", "noscript", "iframe"):
            return ""
        name = node.name
        if name == "br":
            return "<br>"
        if name == "img":
            url = img_src(node)
            if not url:
                return ""
            small = (node.get("width") or "").isdigit() and int(node["width"]) <= 64
            return self.img_tag(url, node.get("alt", ""), cls="emoticon" if small else "blockimg")
        inner = self.inline(node)
        if not inner:
            return ""
        if name == "a":
            href = safe_href(node.get("href"))
            return f'<a href="{esc(href)}" target="_blank" rel="noopener noreferrer">{inner}</a>' if href else inner
        if name in ("b", "strong"):
            return f"<b>{inner}</b>"
        if name in ("i", "em"):
            return f"<i>{inner}</i>"
        if name == "u":
            return f"<u>{inner}</u>"
        if name in ("s", "strike", "del"):
            return f"<s>{inner}</s>"
        if name in ("sup", "sub", "code"):
            return f"<{name}>{inner}</{name}>"
        style = inline_style(node)
        return f'<span style="{style}">{inner}</span>' if style else inner

    def paragraph(self, p) -> str:
        inner = self.inline(p).strip(" \t\r\n")
        return BLANK if is_blank(inner) else f"<p{align_style(p)}>{inner}</p>"

    def paragraph_inners(self, el) -> list[str]:
        inners = (self.inline(p).strip(" \t\r\n") for p in (el.select("p.se-text-paragraph") or [el]))
        return [inner for inner in inners if not is_blank(inner)]

    def text_blocks(self, container, keep_blank: bool = True) -> list[str]:
        blocks = []
        for mod in container.select("div.se-module-text") or [container]:
            for child in mod.children:
                if isinstance(child, Comment):
                    continue
                if isinstance(child, NavigableString):
                    if squash(child):
                        blocks.append(f"<p>{html.escape(str(child).translate(INVISIBLE), quote=False)}</p>")
                elif child.name in ("ul", "ol"):
                    items = "".join(f"<li>{self.inline(li).strip()}</li>" for li in child.find_all("li", recursive=False))
                    if items:
                        blocks.append(f"<{child.name}>{items}</{child.name}>")
                elif child.name not in ("script", "style"):
                    blocks.append(self.paragraph(child))
        return tidy_blanks(blocks, keep_blank)

    # ---- SmartEditor ONE components

    def component_kind(self, comp) -> str:
        known = sorted(self.handlers, key=len, reverse=True)  # longest first: imageStrip before image
        for cls in classes(comp):
            if not cls.startswith("se-") or cls == "se-component" or cls.startswith("se-l-"):
                continue
            name = cls[3:]
            return next((k for k in known if name == k or name.startswith(k)), name)
        return "unknown"

    def convert_se_one(self, main) -> str:
        parts = []
        top_level = [c for c in main.select("div.se-component") if c.find_parent(class_="se-component") is None]
        for comp in top_level:
            kind = self.component_kind(comp)
            self.stats[f"component:{kind}"] += 1
            handler = self.handlers.get(kind)
            out = handler(comp) if handler else self.c_unknown(comp, kind)
            if out:
                parts.append(out)
        return "\n".join(parts)

    def c_text(self, comp) -> str:
        blocks = self.text_blocks(comp)
        return f'<div class="c t">{"".join(blocks)}</div>' if blocks else ""

    def c_section_title(self, comp) -> str:
        lines = self.paragraph_inners(comp)
        if not lines:
            return ""
        p = comp.select_one("p.se-text-paragraph")
        return f'<h2 class="c"{align_style(p) if p else ""}>{"<br>".join(lines)}</h2>'

    def c_quotation(self, comp) -> str:
        quote, cite = comp.select_one(".se-quote"), comp.select_one(".se-cite")
        body = "".join(self.text_blocks(quote, keep_blank=False)) if quote else ""
        cite_lines = self.paragraph_inners(cite) if cite else []
        if not body and not cite_lines:
            return ""
        layout = "default"  # se-l-default is the big quote-mark style
        for el in [comp, *comp.select('[class*="quotation_"]')]:
            found = [c.split("quotation_", 1)[1] for c in classes(el) if "quotation_" in c]
            if found:
                layout = re.sub(r"[^\w-]", "", found[0]) or "default"
                break
        cite_html = f"<cite>{'<br>'.join(cite_lines)}</cite>" if cite_lines else ""
        return f'<blockquote class="c q-{layout}">{body}{cite_html}</blockquote>'

    def c_image(self, comp) -> str:
        images = [self.image_html(mod) for mod in comp.select("div.se-module-image")]
        images = [i for i in images if i]
        if not images:
            return self.c_unknown(comp, "image")
        return f'<figure class="c">{"".join(images)}{self.caption(comp.select_one(".se-caption"))}</figure>'

    def c_image_strip(self, comp) -> str:
        cells = []
        for mod in comp.select("div.se-module-image"):
            url, _, _ = self.image_info(mod)
            if not url:
                continue
            _, w, h = self.fetch_image(url)
            # flex-grow proportional to aspect ratio gives every photo in the row the same height
            cells.append(self.image_html(mod, style=f"flex:{(w / h) if w and h else 1:.4f} 1 0%"))
        if not cells:
            return self.c_unknown(comp, "imageStrip")
        caption = self.caption(comp.select_one(".se-caption"))
        return f'<figure class="c"><div class="row">{"".join(cells)}</div>{caption}</figure>'

    def c_image_group(self, comp) -> str:
        figures = []
        items = comp.select(".se-imageGroup-item") or comp.select("div.se-module-image")
        for item in items:
            mod = item if "se-module-image" in classes(item) else item.select_one("div.se-module-image")
            image = self.image_html(mod) if mod is not None else ""
            if image:
                cap = self.caption(item.select_one(".se-caption, .se-imageGroup-caption")) if mod is not item else ""
                figures.append(f"<figure>{image}{cap}</figure>")
        if not figures:
            return self.c_unknown(comp, "imageGroup")
        shared = [c for c in comp.select(".se-caption") if not c.find_parent(class_="se-imageGroup-item")]
        caption = self.caption(shared[0]) if shared else ""
        return f'<div class="c group">{"".join(figures)}{caption}</div>'

    def c_sticker(self, comp) -> str:
        img = comp.select_one("img.se-sticker-image") or comp.find("img")
        url = img_src(img)
        if not url:
            return ""
        sec = comp.select_one('[class*="se-section-align-"]')
        align = (align_of(sec) if sec else "") or "left"
        return f'<p class="c sticker" style="text-align:{align}">{self.img_tag(url, img.get("alt", ""))}</p>'

    def c_table(self, comp) -> str:
        table = comp.find("table")
        if table is None:
            return self.c_unknown(comp, "table")
        rows = []
        for tr in table.find_all("tr"):
            cells = []
            for td in tr.find_all(["td", "th"], recursive=False):
                attrs = ""
                for span in ("colspan", "rowspan"):
                    value = str(td.get(span) or "")
                    if value.isdigit() and int(value) > 1:
                        attrs += f' {span}="{int(value)}"'
                bg = re.search(r"background(?:-color)?\s*:\s*" + COLOR, td.get("style", "") or "")
                if bg:
                    attrs += f' style="background-color:{bg.group(1)}"'
                cells.append(f"<{td.name}{attrs}>{''.join(self.text_blocks(td, keep_blank=False))}</{td.name}>")
            if cells:
                rows.append(f"<tr>{''.join(cells)}</tr>")
        return f'<div class="c table-wrap"><table>{"".join(rows)}</table></div>' if rows else ""

    def link_card(self, href, title, desc, host, thumb_url) -> str:
        thumb = f'<span class="thumb">{self.img_tag(thumb_url)}</span>' if thumb_url else ""
        body = f'<span class="title">{esc(title)}</span>'
        if desc:
            body += f'<span class="desc">{esc(desc)}</span>'
        if host:
            body += f'<span class="host">{esc(host)}</span>'
        inner = f'{thumb}<span class="body">{body}</span>'
        if href:
            return f'<a class="c card" href="{esc(href)}" target="_blank" rel="noopener noreferrer">{inner}</a>'
        return f'<div class="c card">{inner}</div>'

    def media_card(self, href, thumb_url, title, note) -> str:
        image = self.img_tag(thumb_url) if thumb_url else ""
        heading = f"<b>{esc(title)}</b>" if title else ""
        label = f'<span class="label">{heading}<span>{esc(note)}</span></span>'
        cls = "c media" if image else "c media noimg"
        return f'<a class="{cls}" href="{esc(href)}" target="_blank" rel="noopener noreferrer">{image}{label}</a>'

    def c_oglink(self, comp) -> str:
        anchor = comp.select_one("a.se-oglink-info") or comp.select_one("a[href]")
        href = safe_href(anchor.get("href")) if anchor else ""
        title = first_text(comp, ".se-oglink-title") or href
        if not title:
            return self.c_unknown(comp, "oglink")
        desc = first_text(comp, ".se-oglink-summary")
        host = first_text(comp, ".se-oglink-url") or (urlparse(href).hostname or "")
        thumb = comp.select_one("img.se-oglink-thumbnail-resource") or comp.select_one(".se-oglink-thumbnail img")
        return self.link_card(href, title, desc, host, img_src(thumb))

    def c_video(self, comp) -> str:
        data = module_data(comp)
        media = data.get("mediaMeta") if isinstance(data.get("mediaMeta"), dict) else {}
        title = media.get("title") or data.get("title") or first_text(comp, ".se-media-title", ".se-video-title")
        thumb = absolute(data.get("thumbnail")) or img_src(comp.find("img"))
        return self.media_card(self.page_url, thumb, title, "▶ 동영상은 원문에서 재생할 수 있습니다")

    def c_gif(self, comp) -> str:
        if comp.select_one("div.se-module-image"):
            return self.c_image(comp)
        img = comp.find("img")
        if img_src(img):
            return f'<figure class="c">{self.img_tag(img_src(img), img.get("alt", ""))}</figure>'
        return self.c_video(comp)

    def c_oembed(self, comp) -> str:
        data = module_data(comp)
        url = safe_href(data.get("inputUrl") or data.get("originalUrl") or data.get("url"))
        if not url:
            iframe = comp.find("iframe") or BeautifulSoup(data.get("html") or "", "lxml").find("iframe")
            url = safe_href(iframe.get("src")) if iframe else ""
            yt = re.match(r"https?://(?:www\.)?youtube(?:-nocookie)?\.com/embed/([\w-]+)", url)
            if yt:
                url = f"https://www.youtube.com/watch?v={yt.group(1)}"
        title = data.get("title") or first_text(comp, ".se-oembed-title")
        thumb = absolute(data.get("thumbnailUrl")) or img_src(comp.find("img"))
        return self.media_card(url or self.page_url, thumb, title, "▶ 탭하면 원래 영상으로 이동합니다")

    def c_code(self, comp) -> str:
        source = comp.select_one(".se-code-source") or comp.select_one("pre") or comp
        lines = source.find_all(["div", "p"], recursive=False)
        text = "\n".join(l.get_text() for l in lines) if lines else source.get_text()
        text = text.translate(INVISIBLE).strip("\n")
        return f'<pre class="c code"><code>{html.escape(text, quote=False)}</code></pre>' if text.strip() else ""

    def c_file(self, comp) -> str:
        name = (first_text(comp, ".se-file-name") + first_text(comp, ".se-file-extension")) or "첨부파일"
        return (f'<div class="c box">첨부파일 · {esc(name)} · <a href="{esc(self.page_url)}" target="_blank" '
                f'rel="noopener noreferrer">원문에서 내려받기</a></div>')

    def c_place(self, comp) -> str:
        titles, addresses = comp.select(".se-map-title"), comp.select(".se-map-address")
        places = []
        for i, title in enumerate(titles):
            addr = squash(addresses[i].get_text(" ")) if i < len(addresses) else ""
            places.append(f'<div class="c box">장소 · <b>{esc(squash(title.get_text(" ")))}</b>'
                          f'{f"<br>{esc(addr)}" if addr else ""}</div>')
        return "\n".join(places) if places else self.c_unknown(comp, "map")

    def c_material(self, comp) -> str:
        title = first_text(comp, ".se-material-title")
        if not title:
            return self.c_unknown(comp, "material")
        anchor = comp.select_one("a[href]")
        href = safe_href(anchor.get("href")) if anchor else ""
        details = [squash(d.get_text(" ")) for d in comp.select(".se-material-detail")]
        return self.link_card(href, title, " · ".join(d for d in details if d), urlparse(href).hostname or "",
                              img_src(comp.find("img")))

    def c_unknown(self, comp, kind) -> str:
        self.warnings.append(f"전용 변환 규칙이 없는 구성요소 '{kind}' — 글자와 이미지만 옮겼습니다.")
        blocks = self.text_blocks(comp) if comp.select_one("div.se-module-text") else []
        images = [self.img_tag(img_src(i), i.get("alt", "")) for i in comp.find_all("img")
                  if img_src(i) and i.find_parent(class_="se-module-text") is None]
        if not blocks and not images:
            text = squash(comp.get_text(" "))
            blocks = [f"<p>{html.escape(text, quote=False)}</p>"] if text else []
        parts = [f'<div class="c t">{"".join(blocks)}</div>'] if blocks else []
        parts += [f'<figure class="c">{image}</figure>' for image in images]
        return "\n".join(parts)

    # ---- older editors: keep a safe subset of ordinary HTML

    def convert_generic(self, root) -> str:
        self.warnings.append("SmartEditor ONE 형식이 아니어서 일반 HTML 규칙으로 변환했습니다. 결과를 한 번 확인해 주세요.")
        blocks: list[str] = []
        self.generic_blocks(root, blocks)
        out, run = [], []
        for block in tidy_blanks(blocks) + [""]:
            if block.startswith("<p"):
                run.append(block)
                continue
            if run:
                out.append(f'<div class="c t">{"".join(run)}</div>')
                run = []
            if block:
                out.append(block)
        return "\n".join(out)

    def generic_blocks(self, el, out: list[str]) -> None:
        buffer: list[str] = []

        def flush():
            fragment = "".join(buffer).strip(" \t\r\n")
            buffer.clear()
            if fragment:
                out.append(BLANK if is_blank(fragment) else f"<p>{fragment}</p>")

        for node in el.children:
            if not (isinstance(node, Tag) and node.name in GENERIC_BLOCKS):
                buffer.append(self.inline_node(node))
                continue
            flush()
            name = node.name
            if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                inner = self.inline(node).strip()
                if not is_blank(inner):
                    out.append(f'<h2 class="c">{inner}</h2>')
            elif name == "hr":
                out.append('<hr class="c">')
            elif name == "table":
                out.append(self.generic_table(node))
            elif name in ("ul", "ol"):
                items = "".join(f"<li>{self.inline(li).strip()}</li>" for li in node.find_all("li", recursive=False))
                if items:
                    out.append(f'<div class="c t"><{name}>{items}</{name}></div>')
            elif name == "blockquote":
                inner = self.inline(node).strip()
                if not is_blank(inner):
                    out.append(f'<blockquote class="c q-line"><p>{inner}</p></blockquote>')
            elif name == "pre":
                out.append(f'<pre class="c code"><code>{html.escape(node.get_text(), quote=False)}</code></pre>')
            elif node.find(list(GENERIC_BLOCKS)):
                self.generic_blocks(node, out)
            else:
                out.append(self.paragraph(node))
        flush()

    def generic_table(self, table) -> str:
        rows = []
        for tr in table.find_all("tr"):
            cells = "".join(f"<{td.name}>{self.inline(td).strip()}</{td.name}>"
                            for td in tr.find_all(["td", "th"], recursive=False))
            if cells:
                rows.append(f"<tr>{cells}</tr>")
        return f'<div class="c table-wrap"><table>{"".join(rows)}</table></div>' if rows else ""


# --------------------------------------------------------------------------- output

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
<meta property="og:description" content="$description">
<style>
:root{--bg:#fff;--text:#1d2129;--muted:#6b7280;--line:#e6e8eb;--soft:#f4f5f7;--link:#1a5fd0}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--text);font-size:17px;line-height:1.8;
  font-family:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Pretendard","Noto Sans KR","Malgun Gothic","맑은 고딕",sans-serif;
  word-break:keep-all;overflow-wrap:anywhere}
.wrap{max-width:720px;margin:0 auto;padding:28px 18px 64px}
.head{padding-bottom:20px;margin-bottom:28px;border-bottom:1px solid var(--line)}
.kicker{font-size:13px;font-weight:600;color:var(--muted)}
h1{margin:6px 0 10px;font-size:24px;line-height:1.4;letter-spacing:-.02em}
.meta{font-size:13.5px;line-height:1.6;color:var(--muted)}
.src{display:inline-block;margin-top:14px;padding:6px 14px;border:1px solid var(--line);border-radius:999px;
  font-size:13.5px;color:var(--text);text-decoration:none}
article a{color:var(--link)}
.c{margin:0 0 1.2em}
.t p{margin:0}
.t p.blank{height:1.8em}
.t ul,.t ol{margin:0;padding-left:1.4em}
figure{margin:1.6em 0}
figure img,img.blockimg{display:block;max-width:100%;height:auto;margin:0 auto}
img.emoticon{display:inline;height:1.4em;width:auto;vertical-align:-.3em}
figcaption{margin-top:8px;font-size:13.5px;line-height:1.6;color:var(--muted);text-align:center}
.row{display:flex;gap:4px;align-items:flex-start}
.row>*{min-width:0}
.row img{width:100%;height:auto}
.group figure{margin:0 0 8px}
.sticker img{display:inline-block;max-width:160px;height:auto}
h2.c{margin:1.8em 0 .8em;font-size:1.2em;line-height:1.5}
blockquote.c{margin:1.6em 0;padding:2px 0 2px 16px;border-left:3px solid #c9ced6;color:#374151}
blockquote p{margin:0}
blockquote.q-default{border:0;padding:4px 8px;text-align:center}
blockquote.q-default::before{content:"\\201C";display:block;font:2.4em/1 Georgia,serif;color:#c3c8d0}
blockquote.q-bubble,blockquote.q-postit,blockquote.q-corner{border:0;padding:14px 16px;border-radius:10px;background:var(--soft)}
blockquote.q-underline{border:0;padding:0 0 10px;border-bottom:2px solid #c9ced6}
blockquote cite{display:block;margin-top:8px;font-size:13.5px;font-style:normal;color:var(--muted)}
hr.c{margin:2.2em 0;border:0;border-top:1px solid var(--line)}
.table-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch}
.table-wrap table{min-width:100%;border-collapse:collapse;font-size:14.5px;line-height:1.6}
.table-wrap td,.table-wrap th{padding:8px 10px;border:1px solid #d5d9df;vertical-align:top}
.table-wrap td p,.table-wrap th p{margin:0}
.card{display:flex;align-items:stretch;overflow:hidden;border:1px solid var(--line);border-radius:10px;
  color:inherit;text-decoration:none;background:#fff}
article a.card{color:inherit}
.card .thumb{flex:0 0 96px;background:var(--soft)}
.card .thumb img{display:block;width:100%;height:100%;max-width:none;object-fit:cover}
.card .body{display:block;min-width:0;padding:12px 14px;line-height:1.5}
.card .title,.card .desc,.card .host{display:block}
.card .title{font-size:15px;font-weight:600;overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.card .desc{margin-top:4px;font-size:13px;color:var(--muted);overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}
.card .host{margin-top:6px;font-size:12px;color:var(--muted)}
.media{position:relative;display:block;overflow:hidden;border-radius:8px;background:#1d2129;text-decoration:none}
article a.media{color:#fff}
.media img{display:block;width:100%;height:auto;opacity:.55}
.media .label{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;
  gap:4px;padding:16px;font-size:14px;line-height:1.5;text-align:center}
.media .label b{font-size:16px}
.media.noimg .label{position:static;padding:28px 16px}
pre.code{overflow-x:auto;padding:12px 14px;border-radius:8px;background:var(--soft);font-size:13.5px;line-height:1.6}
.box{padding:12px 14px;border-radius:10px;background:var(--soft);font-size:15px;line-height:1.6}
.tags{display:flex;flex-wrap:wrap;gap:6px;margin-top:2.4em}
.tags span{padding:3px 10px;border-radius:999px;background:var(--soft);font-size:13px;color:#4b5563}
footer{margin-top:3em;padding-top:18px;border-top:1px solid var(--line);font-size:12.5px;line-height:1.7;color:var(--muted)}
footer p{margin:0 0 4px}
footer a{color:inherit}
@media (min-width:768px){body{font-size:18px}h1{font-size:30px}.wrap{padding-top:48px}}
</style>
</head>
<body>
<div class="wrap">
<header class="head">
<div class="kicker">$kicker</div>
<h1>$title</h1>
<div class="meta">$meta_line</div>
<a class="src" href="$url" target="_blank" rel="noopener noreferrer">원문 보기 ↗</a>
</header>
<article>
$body
</article>
$tags
<footer>
<p>출처: <a href="$url" target="_blank" rel="noopener noreferrer">$author, 「$title」 — 네이버 블로그</a></p>
<p>이 파일은 위 게시글의 본문을 옮겨 담은 사본이며, 글과 이미지의 저작권은 원작자에게 있습니다.</p>
<p>변환 시각: $converted (KST)</p>
</footer>
</div>
</body>
</html>
""")


def render_document(meta: PostMeta, body_html: str) -> str:
    text = squash(BeautifulSoup(body_html, "lxml").get_text(" "))
    description = text[:110] + ("…" if len(text) > 110 else "")
    kicker = f"{meta.blog_name} · 네이버 블로그" if meta.blog_name else "네이버 블로그"
    meta_line = " · ".join(esc(x) for x in (meta.author, meta.date_label, meta.category) if x)
    tags = ("<div class=\"tags\">" + "".join(f"<span>{esc(t)}</span>" for t in meta.tags) + "</div>") if meta.tags else ""
    return PAGE.substitute(
        title=esc(meta.title), description=esc(description), kicker=esc(kicker), meta_line=meta_line,
        url=esc(meta.url), author=esc(meta.author), body=body_html, tags=tags,
        converted=dt.datetime.now(KST).strftime("%Y-%m-%d %H:%M"),
    )


def default_filename(meta: PostMeta) -> str:
    """Follow the 'YYMMDD_제목.html' naming used for files shared in KakaoTalk."""
    day = (meta.date or dt.datetime.now(KST)).strftime("%y%m%d")
    title = re.sub(r'[\\/:*?"<>|\x00-\x1f]', "", meta.title).strip()
    title = re.sub(r"\s+", "_", title)[:40].rstrip("_.") or "naver_blog"
    return f"{day}_{title}.html"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="네이버 블로그 글을 본문만 담은 단일 HTML 파일로 저장합니다.")
    ap.add_argument("url", help="네이버 블로그 글 주소 (m.blog.naver.com/<ID>/<글번호> 등)")
    ap.add_argument("-o", "--output", help="저장할 파일 경로 (기본: YYMMDD_제목.html)")
    ap.add_argument("--input", help="이미 저장해 둔 글 페이지 HTML (지정하면 글을 다시 내려받지 않음)")
    ap.add_argument("--max-width", type=int, default=1080, help="이미지 최대 가로 픽셀 (기본 1080)")
    ap.add_argument("--quality", type=int, default=85, help="JPEG 품질 1-95 (기본 85)")
    ap.add_argument("--no-embed", action="store_true", help="이미지를 파일에 넣지 않고 원본 주소로 연결")
    args = ap.parse_args(argv)

    blog_id, log_no = parse_post_url(args.url)
    session = requests.Session()
    if args.input:
        page_html, source = Path(args.input).read_text(encoding="utf-8", errors="replace"), args.input
    else:
        page_html, source = fetch_post(session, blog_id, log_no)

    soup = BeautifulSoup(page_html, "lxml")
    selector, body = find_body(soup)
    if body is None:
        sys.exit("본문 영역을 찾지 못했습니다. 비공개 글이거나 지원하지 않는 형식입니다.")
    meta = extract_meta(soup, blog_id, log_no)
    conv = Converter(session, meta.url, args.max_width, args.quality, embed=not args.no_embed)
    body_html = conv.convert_se_one(body) if selector == "div.se-main-container" else conv.convert_generic(body)

    out = Path(args.output) if args.output else Path(default_filename(meta))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_document(meta, body_html), encoding="utf-8")

    components = {k.split(":", 1)[1]: v for k, v in conv.stats.items() if k.startswith("component:")}
    print(f"원문      : {source}")
    print(f"제목      : {meta.title}")
    print(f"작성자    : {meta.author}" + (f" ({meta.blog_name})" if meta.blog_name else ""))
    print(f"작성일    : {meta.date_label or '(찾지 못함)'}")
    print(f"태그      : {' '.join(meta.tags) or '-'}")
    print(f"본문 구성 : {selector} · " + (", ".join(f"{k} {v}" for k, v in components.items()) or "-"))
    print(f"이미지    : 파일에 포함 {conv.stats['images_embedded']}개"
          f" ({conv.stats['image_bytes'] / 1024 / 1024:.1f} MB), 원본 주소 연결 {conv.stats['images_linked']}개")
    for warning in dict.fromkeys(conv.warnings):
        print(f"주의      : {warning}")
    print(f"저장      : {out} ({out.stat().st_size / 1024 / 1024:.2f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
