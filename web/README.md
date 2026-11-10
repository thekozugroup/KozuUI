# Kozu UI for the web

The same tokens as the FigCraft kit, for any website or web app. Pages 39 to 45 of `Kozu Universal UI Kit.figcraft` show the palette, the web foundations, the `Web / *` masters and four example sites.

| File | Use |
| --- | --- |
| `kozu.css` | CSS custom properties: the Kozu Spectrum ramps, Graphite, status ramps, surfaces, accent and focus roles, type, radius, blur and motion. Works in any stack. |
| `kozu.tailwind.css` | Tailwind CSS v4 theme on top of `kozu.css`: `bg-cobalt-600`, `text-lagoon-700`, `bg-accent`, `text-on-accent`, `text-accent-text`, `bg-canvas`, `text-ink`, `font-display`, `rounded-control`, `text-body`. |

The Spectrum follows Tailwind CSS v4's lightness and chroma step for step, so `cobalt-500` sits where `blue-500` would, a few degrees away in hue (a few role steps are nudged for contrast). Use the Kozu names and roles rather than raw Tailwind colors so the offsets and contrast nudges hold.

## Start

```css
/* app.css */
@import "tailwindcss";
@import "./kozu.css";
@import "./kozu.tailwind.css";
```

Without Tailwind, import `kozu.css` alone and use the variables (`var(--kz-accent-fill)`).

`kozu.tailwind.css` begins with `--color-*: initial;`, which removes Tailwind's default palette so only Kozu colors exist. While migrating an existing site, delete that line, move pages over, then restore it. Role colors live in `@theme inline`, so they resolve where they are used and follow nested themes and accents. Inline theme values are not emitted on `:root`, so custom CSS should use the `--kz-*` variables, not `--color-accent`. Roles already switch with the theme, so `dark:` variants are rarely needed.

Load Source Serif 4 (600) for display and section headings and Inter (400, 600) for everything else, and map them to `--kz-font-display` and `--kz-font-sans`. In Next.js, `next/font/google` can provide both.

## Accent and theme

```html
<html lang="en" data-accent="lagoon">
```

- `data-accent`: `cobalt` (default), `azure`, `lagoon`, `jade`, `fern`, `citron`, `saffron`, `tangerine`, `vermilion`, `berry`, `orchid` or `iris`. One family per site. It also works on a section.
- The theme follows `prefers-color-scheme`. `data-theme="dark"` or `data-theme="light"` on `<html>` or any element forces it for that subtree (a dark code block, an inverted section). Set it on `<html>` before first paint to avoid a flash.
- Theme-dependent tokens use `light-dark()` (Chrome and Edge 123, Firefox 120, Safari 17.5 or later). Older browsers get the light theme through an `@supports` fallback.
- `prefers-reduced-transparency: reduce` turns frost into solid surfaces in both themes.

| Variable | Light | Dark |
| --- | --- | --- |
| `--kz-accent-fill` | 500 for Tangerine, Saffron, Citron, Fern, Jade, Lagoon; 600 for the rest | step 300 or 400 |
| `--kz-accent-on-fill` | ink for the 500 families, white for the 600 families | ink |
| `--kz-accent-text` | the measured text step (700 for most, 800 Tangerine, 600 Iris) | the measured dark text step |
| `--kz-accent-link` | step 600 where it passes 4.5:1, else the text step | the dark text step |
| `--kz-accent-tint` | step 100 | step 900 |

Accent text uses `--kz-accent-text`, never the fill: fills often fail on tints. Supported pairs: accent text on canvas, container and tint; links on canvas and container. Accent text on input fills and links on tints are not supported.

## Mapping the masters

| FigCraft master | HTML |
| --- | --- |
| `Web / Button` Primary | `<button>` or `<a>`: `background: var(--kz-accent-fill); color: var(--kz-accent-on-fill); border-radius: 999px; min-height: var(--kz-target)` |
| `Web / Button` Tonal | `background: var(--kz-input); color: var(--kz-ink)` |
| `Web / Button` Quiet | no fill, `color: var(--kz-accent-text)` |
| Size M (40) | pointer-dense layouts only; phones and touch use L (48) |
| `Web / Nav / Desktop` | `<nav>` on the page ground, no bar; one action, which is quiet or tonal when the page has its own primary |
| `Web / Nav / Scrolled` | a sticky capsule: `background: var(--kz-frost-toolbar); backdrop-filter: blur(var(--kz-blur-control)); box-shadow: var(--kz-shadow-float)` |
| `Web / Field` | `<label>` above a filled `<input>` (`background: var(--kz-input)`, 17 px text), help or error text below with an icon |
| `Web / Option` | a radio group styled as capsules; selected uses `--kz-accent-tint`, an accent check and `--kz-accent-text` |
| `Web / Callout` | a tone step (`--kz-info-bg` or `--kz-warning-bg`) with an icon and a word, no side stripe |
| `Web / Code block` | `<pre data-theme="dark">`, horizontal scroll inside the block |

## Focus without outlines

Kozu replaces the outline with a change of tone and a lift. Every family's focused control differs from its resting fill by at least 3:1 in both themes (measured in `Kozu.tokens.json` `web.focus`).

```css
.kz-button { transition: transform 120ms var(--kz-ease-out), background-color 160ms ease; }
.kz-button--primary:focus-visible {
  outline: none;
  background: var(--kz-focus-fill);   /* light: ink; dark: the accent tint */
  color: var(--kz-on-focus);
}
.kz-button--tonal:focus-visible,
.kz-button--quiet:focus-visible,
a:focus-visible {
  outline: none;
  background: var(--kz-focus-fill-quiet); /* light: ink; dark: the accent fill */
  color: var(--kz-on-focus-quiet);
}
.kz-button:focus-visible { font-weight: 700; box-shadow: var(--kz-shadow-float); transform: translateY(-1px); }
.kz-button:active { transform: scale(0.98); }
@media (hover: hover) and (pointer: fine) {
  .kz-button:hover { filter: brightness(0.96); }
}
@media (prefers-reduced-motion: reduce) {
  .kz-button { transition: background-color 160ms ease; }
  .kz-button:focus-visible, .kz-button:active { transform: none; }
}
```

Check focus with a keyboard on the real site; static boards cannot prove it.

## Page rules

- Frames at 390, 768, 1024, 1440 and 1920 with 20, 32, 40, 40 and 40 px margins; one grid for the whole page, navigation included; content caps at 1760.
- From 768 up, the display is at least three times the 17 px body and section headings at most half the display; on phones the display is at least 2.5 times the body. Headlines run two lines or fewer at every width. Reading text is 60 to 72 characters wide; running text is 16 px or larger.
- Separate sections with grounds (`--kz-canvas`, `--kz-subtle`, an ink field, one accent field per page), not divider lines.
- Frost only for chrome that floats over content: the scrolled navigation, sheets, menus.
