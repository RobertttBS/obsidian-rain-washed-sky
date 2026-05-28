# Project Rules

## theme.css — Do NOT read in full

`theme.css` contains embedded base64 text fonts, pushing the file over 10 MB. Reading it whole will blow up the context window.

**Always extract only what you need via shell or Python.** Never use the `Read` tool on `theme.css` without a tight `offset`/`limit`, and never `cat` the whole file.

### Safe ways to inspect it

Strip the font data blocks first, then grep / view:

```bash
# View only non-font lines (skip base64 data: URIs)
grep -v "data:font" theme.css | head -c 4000

# Find a selector or rule
grep -n "your-selector" theme.css | head -c 4000

# Show a specific line range
sed -n '120,180p' theme.css | head -c 4000

# File size / line count sanity check
wc -l theme.css
```

Python equivalent when you need structured extraction:

```python
import re, pathlib
css = pathlib.Path("theme.css").read_text()
# Drop embedded font payloads so the rest is manageable
stripped = re.sub(r"url\(data:font[^)]+\)", "url(<FONT>)", css)
print(stripped[:4000])
```

### Rule of thumb

If a command's output could still be huge, cap it: `COMMAND 2>&1 | head -c 4000`.
