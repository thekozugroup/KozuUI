# Kozu UI

A project-agnostic universal app UI kit with expressive shapes, frosted controls, near-white surfaces, one app accent by default, and native platform adaptations.

Open **[Kozu Universal UI Kit.figcraft](Kozu%20Universal%20UI%20Kit.figcraft)** in [FigCraft](https://github.com/storytold/figcraft). Review the [PDF](Kozu%20Universal%20UI%20Kit.pdf) or individual [previews](Previews).

The kit includes 39 editable reference boards: foundations, component states, adaptive phone/tablet/desktop layouts, creative tools, Android and Apple widgets, TV, Wear OS and Apple Watch.

- [Review guide](Review%20guide.txt): page map, review instructions and limitations.
- [Tokens](Kozu.tokens.json): portable color, typography, material, geometry and platform rules.
- [Component inventory](Component%20inventory.json): native masters and exposed properties.
- [Design standards](AGENTS.md): implementation requirements.
- [QA evidence](Design%20QA.json): measured checks, critique and outstanding validation.
- [Platform references](Platform%20references.json): primary documentation.

Default type: Source Serif 4 headings and Inter controls/body. The current FigCraft file uses the installed heading-family alias `RR Serif`; portable font packaging is still under review. Icons come from [Aria Icons](https://icons.leularia.com/) using Lucide geometry; licenses are retained in [Icons](Icons).

This is an editable design reference, not production app code. Native accessibility, remote focus, watch scrolling, text scaling and device blur need runtime validation. The current review checkpoint is still being refined for the latest paired-icon and card-corner requirements.

Geometry verification uses Python's standard library and an installed FigCraft CLI:

```sh
python3 tools/verify_geometry.py --self-test
python3 tools/verify_geometry.py --cli /path/to/figcraft-cli
```
