"""Shrink the base64 fonts embedded in theme.css to common characters (Obsidian limit: 5 MB).

  python3 -m pip install fonttools brotli
  python3 scripts/subset-fonts.py

Rewrites theme.css in place, so it is safe to re-run. Glyphs that were cut are gone from
the file. To widen the charset, restore the full fonts first:
  git show 1023312:theme.css > theme.css
"""
import base64, io, re, sys
from pathlib import Path
from fontTools import subset
from fontTools.ttLib import TTFont

CSS = Path(__file__).resolve().parent.parent / "theme.css"
LIMIT = 5_000_000
LOCAL = {"400": "Regular", "600": "SemiBold"}


def dbcs(enc, hi, lo):
    out = set()
    for h in range(hi[0], hi[1] + 1):
        for l in range(lo[0], lo[1] + 1):
            try:
                out.add(bytes([h, l]).decode(enc))
            except UnicodeDecodeError:
                pass
    return out


BASE = {chr(c) for r in ((0x20, 0x7F), (0x3000, 0x3040), (0xFF00, 0xFFF0)) for c in range(*r)} | set("‘’“”—…·")
CHARS = {
    "TC": BASE | dbcs("big5", (0xA1, 0xA3), (0x40, 0xFE)) | dbcs("big5", (0xA4, 0xC6), (0x40, 0xFE)),  # Big5 symbols + 常用字
    "SC": BASE | dbcs("gb2312", (0xA1, 0xA9), (0xA1, 0xFE)) | dbcs("gb2312", (0xB0, 0xD7), (0xA1, 0xFE)),  # GB2312 symbols + 一級字
}


TC_COVERED = set()  # filled by the TC blocks, which come first in theme.css


def rebuild(m):
    block = m.group(0)
    fam = re.search(r"font-family:\s*'([^']+)'", block).group(1)
    weight = re.search(r"font-weight:\s*(\d+)", block).group(1)
    font = TTFont(io.BytesIO(base64.b64decode(re.search(r"base64,([A-Za-z0-9+/=]+)", block).group(1))))
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]
    opts.name_IDs = ["*"]
    sub = subset.Subsetter(opts)
    region = fam[-2:]
    # --user-font-text lists TC before SC, so SC only renders what TC lacks; this is what lets both SC weights fit.
    text = CHARS[region] - TC_COVERED if region == "SC" else CHARS[region]
    sub.populate(text="".join(text))
    sub.subset(font)
    if region == "TC":
        TC_COVERED.update(chr(c) for c in font.getBestCmap() if chr(c) not in BASE)
    buf = io.BytesIO()
    font.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    style = LOCAL[weight]
    src = (f"src: local('{fam} {style}'), local('{fam.replace(' ', '')}-{style}'),\n"
           f"       url('data:font/woff2;base64,{b64}') format('woff2');")
    return re.sub(r"src:.*?format\([^)]*\);", lambda _: src, block.rstrip(), count=1, flags=re.S) + "\n\n"


css = CSS.read_text()
css = re.sub(r"@font-face\s*\{.*?\}\n*", rebuild, css, flags=re.S)
CSS.write_text(css)
size = CSS.stat().st_size
print(f"theme.css: {size:,} bytes")
sys.exit(0 if size < LIMIT else f"over {LIMIT:,} bytes")
