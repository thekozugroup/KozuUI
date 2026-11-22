# Kozu fonts

Inter is the default for display, headings, body text, numbers and controls. The repository includes one optional font for financial numbers and editorial headings. Its portable name is **Source Serif 4**. The included version 4.004 variable Roman file uses the internal family name **RR Serif**.

Page 48 uses Helvetica Neue for the task list, voice input and agent monitor. The family and spacing were matched to the supplied Synq images. The source pack does not identify its original typeface. The macOS menu clock uses SF Pro. FigCraft uses locally available faces for this study. If Helvetica Neue is unavailable, use Roboto and recheck line breaks and control widths. The PDF and PNG previews preserve the reviewed appearance.

## Setup after cloning

1. Make **Inter** available to FigCraft or your app. Obtain Inter separately. For the web, load a variable face or the weights your site uses.
2. To view or author a serif example in FigCraft, install `Kozu-SourceSerif4.ttf` with your system font manager. Reopen FigCraft if needed and check that the example resolves to **RR Serif**. Stock Source Serif 4 registers under a different name.
3. On the web, load the serif face only where you use the optional treatment. [Web setup and examples](../web/README.md#typography)

## Contents and license

- `Kozu-SourceSerif4.ttf`: optional variable Roman font, with weight 200–900 (default 400) and optical size 8–60 (default 20).
- `OFL-SourceSerif4.txt`: the complete, unchanged official Adobe license from the version 4.004 source tag.
- `SourceSerif4.source.json`: embedded names, variable axes, source references, license evidence and SHA-256 hashes.

The font is distributed under the **SIL Open Font License 1.1**. Keep the included copyright notice and license with redistributed copies. The license permits bundling and redistribution, including renamed derivatives, but prohibits selling the font by itself and reserves the primary font name “Source.” The bundled primary family is RR Serif. See the [version-matched Adobe license](https://github.com/adobe-fonts/source-serif/blob/a41b27ad8146dbe8d43e387b8183f000a8254939/LICENSE.md) for the complete terms. The font remains under OFL-1.1 independently of the kit's other files.

## Integrity and limits

The packaged font's SHA-256 is `85a36b2d243f1ccb5901a7a5c6fcc2d68dc5d500db3fe248009cf9e5a4578c1f`. Packaging changes no bytes, metrics, names, glyphs or variation data. The existing alias predates this packaging step; the package is not claimed to be byte-identical to an unmodified upstream release. No fresh-machine rendering test or font installation was performed for this packaging pass.
