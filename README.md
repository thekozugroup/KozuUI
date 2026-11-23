# Kozu UI

Kozu UI is one interface system for Accounts, Tasks and Activity. Blue-to-jade materials and dark navy and white surfaces connect the three destinations. Inter sets body text, controls and financial values. Helvetica Neue sets compact display and voice headings. Menlo sets telemetry, and native chrome uses the system face.

[Open the FigCraft kit](Kozu%20Universal%20UI%20Kit.figcraft) · [Review the PDF](Kozu%20Universal%20UI%20Kit.pdf) · [Open the interactive web prototype](web/index.html)

![Kozu UI cover](Previews/01%20Kozu%20UI.png)

## Design handbook

[Foundations](docs/foundations.md) · [Platform adaptation](docs/platforms.md) · [Patterns](docs/patterns.md) · [Components](docs/components.md) · [Interactive handbook](web/guide.html)

## Explore the kit

| FigCraft page | What to try |
| --- | --- |
| 01 · Kozu UI | Inspect the workspace overview or jump to foundations, components and platform layouts. |
| 02 · Materials and typography | Compare shared background fields, glass, type and surface treatments. |
| 03 · Accounts | Open Account home, compare time ranges in Analytics, and try Pay and Request. |
| 04 · Tasks | Stop a listening session, review and queue a task, and expand an agent. |
| 05 · Activity | Follow a checkout latency incident from command through investigation and recovery. |
| 06 · Activity and progress | Compare animated and reduced-motion listening states. Check how [fixed-pitch dot matrices](docs/foundations.md#dot-matrices) adapt to width and fill by whole dots while progress keeps its exact percentage. |
| 07 · Component catalog | Find reusable controls, destination components and adaptive examples. |
| 08 · Platform adaptations | Inspect TV, watch, widget and wide desktop layouts. |
| 09 · Icon library | Inspect the Lucide icons and their geometry. |
| 10 · Foundations | Compare all seven ramps, semantic roles, type, geometry and six frost treatments. |
| 11 · Core controls | Inspect button, field, selection and range variants. |
| 12 · Core patterns | Explore collections, overlays, navigation and data components. |
| 13 · Apple platform refinements | Review host sizing and focus, then compare adaptive listening with Reduce Motion. |

[03 Accounts — Account home](Previews/03%20Accounts%20%E2%80%94%20Account%20home.png) · [13 Tasks — Listening](Previews/13%20Tasks%20%E2%80%94%20Listening.png) · [22 Activity — Resolved incident](Previews/22%20Activity%20%E2%80%94%20Resolved%20incident.png)

Component specimen pages follow the icon library. The [component inventory](Component%20inventory.json) lists the masters and their boards. The [portable tokens](Kozu.tokens.json) define the shared styles and interaction values. [SwiftUI and Compose templates](platforms/README.md) implement progress and listening. The [palette exporter](tools/export_colors.py) synchronizes the web, Apple and Android color assets. The [web implementation](web/README.md) includes plain CSS, Tailwind mappings and local sample interactions.

Static backgrounds and fictional portraits are embedded in FigCraft and bundled in [Assets](Assets). Controls, charts, labels and progress marks are editable. [Font setup and licenses](Fonts/README.md) · [Lucide license](Icons/LICENSE.txt) · [Platform guidance](Platform%20references.json)

## Verification

Run these checks from the checkout. The browser check uses a disposable local directory for its Chrome profile.

```sh
python3 -B tools/verify_geometry.py --self-test
python3 -B tools/verify_geometry.py
python3 -B tools/verify_system.py
python3 -B tools/export_colors.py --check
node web/check.mjs /path/to/task-scratch
```

The [QA record](Design%20QA.json) lists the exported boards and test scope. The prototypes use sample data. Verify accessibility, host sizing, keyboard, remote and rotary input, and blur performance in the shipping app.
