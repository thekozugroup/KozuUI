# Kozu UI

An editable interface system built from three QClay references. Paylane uses blue grain and white sheets for finance. Synq uses directional blue light behind translucent workspaces. Nightshift uses a green halftone field behind a dark incident console. All three share control geometry, type roles, focus behavior and progress indicators.

[Open the FigCraft kit](Kozu%20Universal%20UI%20Kit.figcraft) · [Review the 31-board PDF](Kozu%20Universal%20UI%20Kit.pdf) · [Open the interactive web prototype](web/index.html)

![Kozu UI cover showing the three product materials](Previews/01%20Kozu%20UI.png)

## Explore the kit

| FigCraft page | What to open |
| --- | --- |
| 01 · Kozu UI | Choose a product on the cover. |
| 02 · Materials and typography | Compare the six background fields, glass, type and color treatments. |
| 03 · Paylane | Explore Account home, Analytics, the weekly update, account actions and home-screen widgets. |
| 04 · Synq | Stop a listening session, review a task, queue it and expand an agent. |
| 05 · Nightshift | Follow checkout latency from the command prompt through investigation and recovery. |
| 06 · Activity and progress | Inspect the listening animation, its reduced-motion state and the numeric progress grids. |
| 07 · Component catalog | Find the reusable finance, agent, console and adaptive components. |
| 08 · Platform adaptations | Inspect the TV console, watch and widget layouts, and wide desktop workspace. |
| 09 · Icon library | Inspect the Lucide geometry and source symbols. |

The native file contains 110 component masters and 42 variables. The [component inventory](Component%20inventory.json) names each master and its board. The [portable tokens](Kozu.tokens.json) define material, color, typography, spacing, interaction and feedback. The [web reference](web/README.md) includes plain CSS, Tailwind v4 mappings and local interactions.

The six background images and three fictional portraits are embedded in FigCraft and supplied separately in [Assets](Assets). Controls, charts, labels and progress marks remain editable. [Asset provenance](Assets/Source%20notes.json) · [Font setup](Fonts/README.md) · [Design references](Platform%20references.json)

## Verification

From the checkout, run the two geometry checks and the system check. The browser check takes a disposable local directory for its temporary Chrome profile.

```sh
python3 -B tools/verify_geometry.py --self-test
python3 -B tools/verify_geometry.py
python3 -B tools/verify_system.py
node web/check.mjs /path/to/task-scratch
```

The [QA record](Design%20QA.json) lists the exported artboards, counts, review findings and test scope. Payments, listening, agent work and incident recovery use sample data. Check native accessibility, host sizing, remote or rotary input and glass performance in the shipping app.

Edition 1.0 replaces the previous component IDs and palette. Existing consumers can retrieve the 0.7 kit and its review history from [the previous edition](https://github.com/thekozugroup/KozuUI/tree/058cfd5acc777748e5b04c94c436ab1c96f4ebf0).
