# Kozu web reference

Open [index.html](index.html) in a browser. The page runs directly from disk using HTML, CSS and JavaScript. Keep `web/` next to the checkout’s `Assets/` and `Fonts/` directories. The core experience uses local assets and requires no build, account or network.

- **Paylane** has a blue grain masthead and a continuous paper sheet. Use the dock to switch between Home, Analytics and the weekly update. Expand the ledger to see older transactions and switch Analytics between week and month. Pay and Request open local previews.
- **Synq** uses Helvetica Neue and a blue smoke field. Expand an agent to pause, resume or advance its progress. Enter a task to queue it. Listen previews a 3×9 dot matrix and supplies a sample transcription when stopped with an empty composer.
- **Nightshift** uses an acid-green pixel field and a dark timestamped terminal. Switch environments, scrub the replay with the range control and open the incident report.

The sample date is Sunday, November 22, 2026. The Paylane balance is **$117,450.17**. Spending totals come from the sample ledger. All actions use in-page sample data and reset on reload.

## Keyboard and motion

Use Tab to move through controls, Left and Right to switch tabs, and Home and End to jump to the first or last tab. Enter or Space opens an agent, Escape closes a payment preview, and the replay range supports arrow keys. Focus uses a tonal fill or a text underline. System reduced motion keeps the Listening dots steady. Controls use 28px backdrop blur where frosted, and the demo dialog backdrop uses 40px.

## CSS

Link [kozu.css](kozu.css) for plain CSS. Set `data-surface="paylane"`, `"synq"` or `"nightshift"` on the root or a themed region. Use the semantic custom properties for canvas, panel, ink, muted text, accent, control and focus. Paylane and Nightshift use bundled Inter with a system sans fallback. See the [Inter license](../Fonts/OFL-Inter.txt). Synq prefers Helvetica Neue.

For a project already using Tailwind CSS v4, import [kozu.tailwind.css](kozu.tailwind.css) after Tailwind. It includes the plain CSS and exposes utilities such as `bg-kozu-panel`, `text-kozu-ink`, `font-kozu`, `rounded-kozu` and `backdrop-blur-kozu-overlay`. Theme values resolve at the component from the closest surface.

| Role | Paylane | Synq | Nightshift |
| --- | --- | --- | --- |
| Canvas | `#F7F7F7` | `#090F19` | `#020908` |
| Panel | `#FFFFFF` | `#1B2634` | `#17231A` |
| Ink | `#090B14` | `#F5F7FC` | `#F1F5F1` |
| Muted | `#575A64` | `#BAC6DA` | `#ACBCB5` |
| Accent | `#345A98` | `#D4E6FF` | `#BFDF38` |
| Accent ink | `#FFFFFF` | `#152239` | `#1A240D` |
| Focus | `#172F58` | `#E5EFFF` | `#EFFFD0` |

Paylane's balance uses `#090B14` with `#646B70` cents. Synq uses `#101A2AC2` for frost. Nightshift uses `#041916CD` for frost. The main control target is 48 CSS pixels.

Blue, story, smoke, agents, acid and night are the shared local material images. Paylane uses three generated portraits from `Assets/People/`. The layout, text, charts and controls are editable HTML and CSS. Lucide symbols derive from the adjacent [icon sources and license](../Icons/LICENSE.txt).

## Browser regression checks

Run `node web/check.mjs /path/to/task-scratch` with Node.js 22+ and Chrome. Set `CHROME` to the browser binary on hosts where Chrome uses a different installation path. The test opens the actual `file:` entry, checks keyboard and pointer-driven interactions, and verifies layouts at 320px, 390px, 768px and 1440px, including 200% text at 390px. Add `--capture` to write desktop and mobile screenshots to the supplied scratch directory. The test deletes its temporary Chrome profile on exit.
