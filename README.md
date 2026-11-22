# Kozu UI

A project-agnostic UI kit for apps and websites: expressive shapes, frosted controls, near-white surfaces, one accent family per app, its own color system (the Kozu Spectrum) and native platform adaptations.

Open **[Kozu Universal UI Kit.figcraft](Kozu%20Universal%20UI%20Kit.figcraft)** in [FigCraft](https://github.com/storytold/figcraft). Review the [PDF](Kozu%20Universal%20UI%20Kit.pdf) or individual [previews](Previews).

Edition 0.7 includes 49 editable reference boards. They cover foundations, the Kozu Spectrum palette, component states, adaptive phone/tablet/desktop layouts, creative tools, Android and Apple widgets, TV, Wear OS and Apple Watch. The web boards cover foundations, components and four website examples. Page 46 covers activity and connected sources, page 47 shows financial typography, and page 48 shows a multi-agent workspace.

- On page 48, present **Review an agent** to open Nova, Atlas, or Orion and inspect its work. **Voice request** demonstrates the listening, review and submission states. [Multi-agent workspace preview](Previews/48%20Multi-agent%20workspace.png)
- [Review guide](Review%20guide.txt): page map, review instructions and limitations.
- [Tokens](Kozu.tokens.json): portable color, typography, material, geometry, web and platform rules.
- [Web tokens](web): `kozu.css` (CSS custom properties, light/dark, `data-accent` families) and `kozu.tailwind.css` (Tailwind CSS v4 theme).
- [Component inventory](Component%20inventory.json): native masters and exposed properties.
- [Design standards](AGENTS.md): implementation requirements.
- [QA evidence](Design%20QA.json): measured checks, critique and outstanding validation.
- [Platform references](Platform%20references.json): primary documentation.

## Color: the Kozu Spectrum

Twelve accent families (Cobalt, Azure, Lagoon, Jade, Fern, Citron, Saffron, Tangerine, Vermilion, Berry, Orchid and Iris), a Graphite neutral and four status ramps. Each family follows a Tailwind CSS v4 family's lightness and chroma step for step (Cobalt on blue, Lagoon on cyan, Berry on pink and so on), turned plus or minus 2 to 4 degrees to its own hue: the median OKLab distance to the matching Tailwind step is 0.007. Roles are measured per family: bright families fill at 500 with an ink label, deep families at 600 with a white label, and accent text uses each family's measured text step. Every supported pair is at least 4.5:1: labels on fills, accent text on canvas, container and tint, and dark text on dark surfaces. On the web, keyboard focus changes a control by at least 3:1. Page 39 shows the ramps, live accent modes, the measured roles and color-vision-checked sets.

Unchecked checkboxes and radios use unmarked tonal fills. A rounded square identifies a checkbox and a circle identifies a radio. On selection, the accent tint carries a check or radio dot. A mixed checkbox carries a dash.

## Websites

Pages 40 and 41 hold the web foundations (frame and grid, type, section grounds, states, motion) and the `Web / *` masters. Pages 42 to 45 show them in use: a studio portfolio, the Paperboy landing page, a print store with a frosted bag sheet, and documentation with a changelog article, each at 1440 and 390. To use the tokens on a site:

```css
@import "./kozu.css";            /* any stack */
@import "./kozu.tailwind.css";   /* Tailwind CSS v4, after @import "tailwindcss" */
```

Set `data-accent="lagoon"` (or any family) on `<html>` or any section; `data-theme="dark"` or `"light"` forces a theme for that subtree. `kozu.tailwind.css` resets Tailwind's default colors so only Kozu values are available; remove its `--color-*: initial;` line while migrating an existing site.

## Fonts and icons

Inter is the default for all type, including display headings, controls and financial numbers. Source Serif 4 is optional for an individual financial number or editorial heading. FigCraft uses the bundled family name `RR Serif` for those examples. Page 48 uses Helvetica Neue for the task list, voice input and agent monitor. The family and spacing were matched to the supplied Synq images. The source pack does not identify its original typeface. The macOS menu clock uses SF Pro. [Font setup and license](Fonts/README.md)

Icons come from [Aria Icons](https://icons.leularia.com/) using Lucide geometry. [Icon assets, licenses and source IDs](Icons)

This is an editable design reference, not production app code. Native accessibility, remote focus, watch scrolling, text scaling, device blur and browser behavior need runtime validation.

Regenerate the Spectrum (for example after changing a family's Tailwind base or hue offset) with `python3 tools/kozu_spectrum.py`, which prints the palette JSON using only the standard library.

Geometry verification uses Python's standard library and an installed FigCraft CLI:

```sh
python3 tools/verify_geometry.py --self-test
python3 tools/verify_geometry.py --cli /path/to/figcraft-cli
```
