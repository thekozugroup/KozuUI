# Kozu heading font

`Kozu-SourceSerif4.ttf` provides the **RR Serif** family used by the editable Kozu kit. It is the existing renamed Source Serif 4 version 4.004 variable Roman font, copied unchanged from the authoring setup. The portable typography name remains Source Serif 4; the native file resolves its headings through RR Serif.

## Setup after cloning

1. Install `Kozu-SourceSerif4.ttf` with your operating system's font manager before opening the native kit. Skip duplicate installation if the same font is already available.
2. Reopen FigCraft if it does not detect the font. Confirm that heading layers resolve to **RR Serif**, rather than a fallback. Keep the native family's existing styles and weights.
3. Ensure **Inter** is available for body text and controls. This pack contains the heading font only; it does not bundle Inter.

Cloning the repository does not register fonts with the operating system. A stock Source Serif 4 installation has a different family name and does not by itself resolve the kit's RR Serif references. Do not rename the bundled family or substitute native text styles to work around a missing installation.

## Contents and license

- `Kozu-SourceSerif4.ttf`: variable Roman heading font, with weight 200–900 (default 400) and optical size 8–60 (default 20).
- `OFL-SourceSerif4.txt`: the complete, unchanged official Adobe license from the version 4.004 source tag.
- `SourceSerif4.source.json`: embedded names, variable axes, source references, license evidence and SHA-256 hashes.

The font is distributed under the **SIL Open Font License 1.1**. Keep the included copyright notice and license with redistributed copies. The license permits bundling and redistribution, including renamed derivatives, but prohibits selling the font by itself and reserves the primary font name “Source.” The bundled primary family is RR Serif. See the [version-matched Adobe license](https://github.com/adobe-fonts/source-serif/blob/a41b27ad8146dbe8d43e387b8183f000a8254939/LICENSE.md) for the complete terms. The font remains under OFL-1.1 independently of the kit's other files.

## Integrity and limits

The packaged font's SHA-256 is `85a36b2d243f1ccb5901a7a5c6fcc2d68dc5d500db3fe248009cf9e5a4578c1f`. Packaging changes no bytes, metrics, names, glyphs or variation data. The existing alias predates this packaging step; the package is not claimed to be byte-identical to an unmodified upstream release. No fresh-machine rendering test or font installation was performed for this packaging pass.
