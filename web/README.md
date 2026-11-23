# Kozu web workspace

Open [the workspace](index.html) or [the design guide](guide.html) in a browser. Keep `web/` next to `Assets/` and `Fonts/`. The workspace uses local sample data and resets on reload.

- **Accounts** includes balances, transactions, spending analytics and the weekly update. Pay and Request open previews. The spending view shows week or month totals and labels the final needle with its exact value.
- **Tasks** includes the composer and the Inbox, Flow and Scout agents. Expand an agent to pause, resume or advance it. Start and stop the listening preview to see the waveform and get a sample transcription.
- **Activity** includes the incident timeline, environment picker, replay control and report. Move the replay control to show a specific step in the incident.

## Shared materials and type

The workspace uses blue-to-jade textured fields, white reading surfaces and layered navy panels. In Accounts, compare the translucent account chip on the textured header with the opaque transaction sheet. In Tasks, compare the glass agent list with the white composer.

[The palette](palette.css) defines Orange, Green, Blue, Gold, Violet and Rose, and the neutral Graphite ramp. It supplies shared `--kz-*` interaction and status roles. Blue is used for action and information, orange for attention, and green for recovery. Gold, Violet and Rose are available for comparative series. The palette also defines focus colors for each context.

[The stylesheet](kozu.css) imports the palette. Choose `data-theme="light"` for white surfaces or `data-theme="dark" data-surface="navy"` for the workspace's navy surfaces. The semantic `--kozu-*` aliases supply the local action, control, focus and status colors. For Tailwind CSS v4 projects, import [kozu.tailwind.css](kozu.tailwind.css) after Tailwind.

Inter is used for body text, controls and financial values. Helvetica Neue is used for compact display and voice headings and falls back to Inter and system sans. Telemetry values use Menlo with a system monospace fallback. The bundled Inter and Lucide symbols retain their licenses. [Inter license](../Fonts/OFL-Inter.txt) · [Lucide license](../Icons/LICENSE.txt)

## Accessibility

Tab moves through controls. Left and Right move between tabs, Up and Down also work in the tablet rail, and Home and End jump to the first or last tab. Escape closes the transfer preview and restores focus. Mobile controls have at least 48 CSS pixels of target area. The workspace reflows for larger text and respects viewport safe areas. [Apple Human Interface Guidelines on accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility)

Glass uses 42% light or 34% dark fill for controls, 52% light or 44% dark fill for cards and toolbars, and 70% light or 60% dark fill for overlays. Controls, cards and toolbars use 28px backdrop blur. Overlays use 40px. Reduced transparency uses opaque fills. Reduced motion keeps the listening matrix steady.

## Dot grids

Load [dot-grid.js](dot-grid.js) with `defer` alongside `kozu.css`. Give the grid a width-constrained container. Leave the grid element empty and provide the accessible name, exact completion value or listening state separately.

```html
<div data-dot-grid="progress" data-dot-value="65" aria-hidden="true"></div>
<span>65%</span>
```

- Use `data-dot-grid="progress"` for two rows, `"listening"` for three and `"waveform"` for seven.
- Dots are 4 CSS pixels in diameter at an 8 CSS pixel pitch on both axes. The helper uses `max(0, 1 + floor((width - 4) / 8))` columns and centers the grid on the available content width. An intrinsically sized container reserves one 4 CSS pixel column. A specified width below 4 CSS pixels fits zero columns.
- Update `element.dataset.dotValue` with the exact percentage. Progress lights `floor(totalVisibleDots × percent / 100)` dots, from the leading column to the trailing column, top cell then bottom cell. At 0% the entire grid stays muted. At 100% every fitted dot is lit. Keep the independently displayed percentage in sync.
- Grids resize automatically and initialize when inserted. Listening and waveform animate dot opacity when motion is allowed. Both retain their complete geometry and static pattern with reduced motion. Set `--kozu-dot-active` and `--kozu-dot-muted` to customize dot paint.

## Browser regression

Run `node web/check.mjs /path/to/task-scratch` with Node.js 22+ and Chrome. Use `CHROME` to override the Chrome binary path. Add `--capture` for screenshots, including the same Tasks workspace with glass and with opaque fills. The test loads the local entry, measures contrast against the brightest and darkest rendered pixels in glass samples, checks keyboard and pointer interactions and dot geometry, and verifies adaptive layouts at 320px, 390px, 600px, 768px and 1440px. It also checks 200% text at compact and tablet widths. The temporary Chrome profile is removed on exit.
