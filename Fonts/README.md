# Kozu fonts

Paylane and the shared controls use Inter. Synq uses Helvetica Neue. Nightshift pairs Inter with Menlo for timestamps and commands. Changing and aligned financial values use tabular figures. Native platform chrome uses the system face.

## Inter

The local web prototype loads `InterVariable.woff2` with weights 100–900. The file and its license come from the same rsms/inter commit. To edit Inter text in FigCraft, make the desktop face available in the system font manager. [Upstream Inter source](https://github.com/rsms/inter/tree/353b61b9f4430d5f420d56605a6e7993e0941470) · [Bundled SIL Open Font License](OFL-Inter.txt)

## Platform fonts

FigCraft uses locally available faces for Helvetica Neue and Menlo. The web prototype provides fallbacks for these roles. Check wrapping and numeric alignment after substituting a font. The PDF and PNGs preserve the reviewed layout.

## Optional Source Serif 4

The retained Source Serif 4.004 Roman variable font registers as **RR Serif** in FigCraft. Its weight axis spans 200–900 and its optical-size axis spans 8–60. Install `Kozu-SourceSerif4.ttf` only where the optional editorial face is used. Its SHA-256 is `85a36b2d243f1ccb5901a7a5c6fcc2d68dc5d500db3fe248009cf9e5a4578c1f`. The [source record](SourceSerif4.source.json) describes the alias and file provenance. [Bundled SIL Open Font License](OFL-SourceSerif4.txt) · [Adobe's version-matched license](https://github.com/adobe-fonts/source-serif/blob/a41b27ad8146dbe8d43e387b8183f000a8254939/LICENSE.md)
