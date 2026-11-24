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

## Color palettes — light and dark must mirror each other

Palettes live in `theme.css`:

- Default (Rain-Washed Sky): `.theme-light` and `.theme-dark`, about line 144.
- Others: `.theme-light.rws-palette-<id>` and `.theme-dark.rws-palette-<id>`, after the "1b. Alternative Palettes" header.
- Find them with `grep -n "^/\* --- Palette\|^\.theme-" theme.css`.

### Mirror rule: swap base and accent

Each palette is built from two colors, A and B. Dark mode swaps their roles.

| Role | Variables | Light | Dark |
|------|-----------|-------|------|
| Base | `--user-bg-*`, `--user-canvas-bg`, `--user-active-line` | pale A | deep B |
| Accent | `--user-accent-main`, `--h1-gradient` to `--h3-gradient` | B | light A |

Examples already in the theme:

- Rain-Washed Sky: light uses a Ru-ware celadon base (`#F6F7F2`, leaning ivory) with blue-and-white accents (`#346c9c`). Dark uses a deep blue base (`#0F1626`) with celadon accents (`#7CC5C5`).
- Peach Blossom: light uses a pink base (`#FDF7F3`, leaning ivory) with a navy accent (`#2B4C7E`). Dark uses a navy base (`#0E1A2B`) with a pink accent (`#EFA3BA`).

Do not swap these. Keep the same hue in both modes and change only the lightness:

- `--user-accent-strong`: emphasis and alerts only.
- Callout colors: `--user-accent-tip`, `--user-accent-success`, `--user-accent-warning`, `--user-accent-info`, `--user-accent-error`, `--user-accent-quote`, `--user-accent-example`, `--user-accent-background`.

Nordic Espresso predates this rule. It keeps the same blue accent in both modes. Do not copy it for new palettes.

### Structure

- Light and dark blocks must define the same variable set. Copy an existing pair as the template, then change values only.
- Put a `/* --- Palette: <English name> --- */` header above the pair.
- Write one line in the light and dark `/* === 基底 === */` comments. The line names how A and B swap, as in 汝窯為體，青花為用 / 青花為海，汝瓷為星.

### Known pitfalls (active tab)

The active tab uses `box-shadow: var(--float-highlight)`. The note area below it draws no visible edge, so any side or bottom edge on the tab looks broken.

- Do not use a full ring such as `inset 0 0 0 1px ...` for `--float-highlight`. It draws a line under the active tab. If a palette needs one, add it to the `box-shadow: none` rule after `.mod-root .workspace-tab-header.is-active`.
- In light mode, keep `--float-highlight` top-only, for example `inset 0 1.5px 0 0 rgba(255,255,255,0.7)`.
- In dark mode, the tab shadow is already removed for all palettes.

### Adding a palette — checklist

1. Add an option under `id: rws-palette` in the `/* @settings` block. Use the format `label: English Name (中文名)` and `value: rws-palette-<id>`.
2. Add the light and dark blocks, following the mirror rule.
3. Check that both blocks define the same variables. For example, extract the `--` names of each block with Python and compare them.
4. Copy `theme.css` into the vault's `.obsidian/themes/Rain-Washed Sky/`, then switch to the palette in Style Settings.
5. Screenshot both modes. Check the active tab, headings, links, and callouts.
