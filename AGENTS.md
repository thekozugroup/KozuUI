# Kozu app system defaults

Read `~/.config/ai-development/maintenance-policy.md` before development or system maintenance on this Mac. Use the canonical checkout at `/Users/michaelwong/Developer/KozuUI`. The user authorizes work on `main`. Keep dependencies, builds and scratch work outside the synced Documents review folder.

## Design sources

Use `Kozu Universal UI Kit.figcraft` as the editable design reference, `Kozu.tokens.json` as the portable contract and `web/kozu.css` for web implementation. Page 02 defines materials and type. Pages 03–05 show product behavior, page 06 defines activity indicators, page 07 contains reusable components, and page 08 applies the system across platforms. See `Platform references.json` for the supplied visual sources and platform guidance.

- Use Paylane's blue grain, white sheets and blue gradient actions for finance. Show aligned balances in Inter with tabular figures and keep the fractional amount legible on the same baseline. Preserve a complete localized currency value for assistive technology.
- Use Synq's directional blue light, translucent charcoal surfaces and Helvetica Neue for voice and agent work. Keep the light visible through workspace layers while maintaining readable text. Pair the listening matrix with a visible state and Stop. Pair determinate progress with its exact numeric value. Preserve native system typography for platform chrome.
- Use Nightshift's green halftone and dark glass for incident tools. Set event times and command fragments in Menlo or a platform monospace. Pair orange alerts, blue investigation events and green recovery events with a glyph and a status word. Keep command, evidence and outcome in reading order.
- Keep background fields static. Use the bundled originals in `Assets/Materials` and the local portraits in `Assets/People`. Prefer semantic variables and existing master instances. On import, check variable definitions and remap imported IDs against the destination document.

## Controls and layout

- Use fill, opacity, space and type weight to separate surfaces and show state. Keep surfaces and controls borderless. Preserve icon strokes, data marks, selection checks and functional console separators. Use the 28-unit blur on frosted controls and 40-unit blur on overlays. Provide opaque panel equivalents for reduced transparency.
- Use Lucide from Aria Icons on a 24-unit grid with a 1.8-unit source stroke. Preserve its upstream license. In text buttons, match the icon's visible ink to label cap height. Center the ink in the rounded endcap and center the text within the entire button with balanced slots. Icon-only touch targets default to 48 units.
- Derive adjacent nested radii with `max(0, outerRadius - inset)`. Center chip contents, avoid clipping focus or text, and keep both ends of floating bars balanced. The compact pointer target minimum is 32 units. Show focus with tone and text emphasis independently of selection. Preserve native keyboard, remote and reduced-motion behavior.
- Below 600 units use compact navigation. At 600 introduce the tablet rail. Float its 72-unit capsule 16 units from the leading safe edge, with 8-unit padding, 56-unit targets and 8-unit gaps. Center it vertically. Introduce two panes from 720 when they fit, and a sidebar from 840. Preserve selection, scroll and input as the viewport changes.
- Use the 3×9 dot grid for listening and a steady waveform under reduced motion. Use a 2×10 dot grid for determinate work with the exact percentage beside it. The financial goal bar encodes saved amount divided by target and shows both amounts.
- Use native safe areas, widget bounds, text scaling, wear targets and TV focus navigation in applications. Prefer tonal surfaces on Wear OS and Android widgets. Keep wearable content round-safe or rectangular according to the host. Use a tonal or host-provided widget background appropriate to the platform.

## Verification

After changing the native kit, run `python3 -B tools/verify_geometry.py --self-test`, `python3 -B tools/verify_geometry.py` and `python3 -B tools/verify_system.py`. Update the affected native exports, portable tokens, inventories and web implementation together. Test the web entry with `node web/check.mjs /path/to/task-scratch`. Confirm accessible names, focus return, keyboard traversal, 200% text and actual blur performance on each shipping platform.
