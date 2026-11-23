# Kozu native activity

Add the [SwiftUI source](apple/KozuActivity.swift) to an iOS 16+ or macOS 13+ target. Add the [Compose source](android/KozuActivity.kt) to an Android module with Compose Foundation, Animation and Material 3. Use the host theme for foreground colors and surfaces. The progress caption accepts a scaling font or text style from the host.

- `KozuListening` displays the caller's `isListening` state and requests a start or stop through `onListeningChange`. Supply translated labels from the host. The waveform adds columns as width grows. When the row cannot fit, or accessibility text sizes are active, the label, dots and action stack. Allow at least 48 points or dp for the action and room for the stack to grow vertically.
- `KozuProgress` takes a localized label and a whole `percent`, clamped to 0–100. It places the label, two-row meter and percentage in one row with 20-unit outer insets and balanced end slots. Compact widths and large text stack the three elements. The visible percentage and native accessibility value stay exact.

Both grids use a pitch of 8 and a diameter of 4 in points or dp. The grid draws zero columns below 4 units of width. Otherwise it centers `1 + floor((width - 4) / 8)` complete columns. Each dot is either lit or dimmed. The dots are decorative.

Progress lights `floor(totalVisibleDots * percent / 100)` whole dots from leading to trailing, top then bottom in each column. At 0% every dot is dim. At 100% every dot is lit. A 20-dot meter at 65% lights six columns and the top dot of the seventh.

Listening uses SwiftUI Reduce Motion and Compose's system animation duration scale. On Android, the host can also pass `reduceMotion = true` for an in-app preference. See the [portable feedback tokens](../Kozu.tokens.json) for the default row counts.
