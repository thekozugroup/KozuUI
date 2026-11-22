# Kozu UI for the web

The same tokens as the FigCraft kit, for any website or web app. Pages 39 to 45 of `Kozu Universal UI Kit.figcraft` show the palette, web foundations, the `Web / *` masters and four example sites. Page 46 covers activity and connected sources. Pages 47 and 48 show financial typography and a multi-agent workspace.

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

## Typography

Load Inter as a variable face or supply the weights you use. The CSS applies the sans stack to body text and form controls. Headings inherit it. Both `--kz-font-sans` and `--kz-font-display` default to Inter, as do Tailwind's `font-sans` and `font-display`. Supply your loader's family name through `--kz-font-sans` on the root if needed.

Use Source Serif 4 only for an individual financial number or editorial heading. Apply `kz-financial-number` to the amount or `kz-editorial-heading` to the heading. With Tailwind, use `font-serif tabular-nums lining-nums` for the amount or `font-serif` for the editorial heading. Keep labels and explanatory text in Inter. For changing or aligned amounts in the default Inter face, use `font-variant-numeric: tabular-nums` or Tailwind's `tabular-nums`.

```html
<dl>
  <dt>Available balance</dt>
  <dd class="kz-financial-number">$2,450.00</dd>
</dl>
```

On pages using the optional face, the following rule loads the bundled variable font. Adjust the URL to the asset's deployed location. The family's fallback is Inter.

```css
@font-face {
  font-family: "Source Serif 4";
  src: url("../Fonts/Kozu-SourceSerif4.ttf") format("truetype");
  font-style: normal;
  font-weight: 200 900;
  font-display: swap;
}
```

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

## Activity and connections

Apply `kz-gradient-field` to the section that paints the page's accent field. Its `background-image` draws a stationary gradient from the local accent tint to the container color. The container color sits behind the gradient. Forced colors use a solid system surface. Put ink text directly on the field. Give links and controls their own supported surface.

```html
<section class="kz-gradient-field" aria-labelledby="activity-title">
  <h2 id="activity-title">Activity</h2>
  <p><span class="kz-dots" aria-hidden="true"></span> Queued</p>
  <label for="copy-progress">Files copied</label>
  <progress class="kz-progress" id="copy-progress" value="3" max="5"></progress>
  <span>3 of 5</span>
</section>

<p role="status">
  <span class="kz-listening" aria-hidden="true">
    <span></span><span></span><span></span><span></span><span></span>
  </span>
  Listening
</p>
```

Use the square dot group as a decorative companion to a label. For measured work, update the native progress value and the visible count together. The browser supplies the accessible range and draws the native indicator in forced colors. For listening, put the current state in the status text and update it when input stops. The waveform pulses briefly on entry and stays still under reduced motion. Expose an ordinary labeled button if the user can stop listening.

For `Connections / Source discs`, put the service marks beside one visible label naming all sources in reading order. Each 40 px disc centers a 24 px glyph. The next disc overlaps the previous one by 8 px, giving a 32 px center-to-center distance in either writing direction. Hide the marks from assistive technology so the source names are read once. Keep connection management in a separate labeled control.

```html
<span class="kz-source-group">
  <span class="kz-source-marks" aria-hidden="true">
    <span>
      <svg viewBox="0 0 24 24" focusable="false">
        <path d="m22 7-8.991 5.727a2 2 0 0 1-2.009 0L2 7"/>
        <rect x="2" y="4" width="20" height="16" rx="2"/>
      </svg>
    </span>
    <span>
      <svg viewBox="0 0 24 24" focusable="false">
        <path d="M6 22a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1 1.704.706l3.588 3.588A2.4 2.4 0 0 1 20 8v12a2 2 0 0 1-2 2z"/>
        <path d="M14 2v5a1 1 0 0 0 1 1h5"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>
      </svg>
    </span>
  </span>
  <span>Mail and files</span>
</span>
```

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
| `Web / Option` | a radio group styled as capsules. The selected capsule uses `--kz-accent-tint` with an accent check and `--kz-accent-text`. |
| `Web / Callout` | a tone step (`--kz-info-bg` or `--kz-warning-bg`) with an icon and a word, no side stripe |
| `Web / Code block` | `<pre data-theme="dark">`, horizontal scroll inside the block |

For standard checkbox and radio indicators, use a borderless tonal rounded square or circle. Leave the unchecked fill unmarked. Start with `--kz-ink-secondary` at 75% opacity on the indicator fill and check for at least 3:1 contrast against the actual surface. Use an accent tint with a check for a checked box, a dash for a mixed box and a dot for a selected radio. Keep native labeled inputs, checked or indeterminate state, and keyboard behavior when styling their indicators. Allow the browser's control appearance in forced colors.

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
