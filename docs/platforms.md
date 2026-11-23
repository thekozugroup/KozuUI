# Platform adaptation

Preserve the task, vocabulary, order of information and state as Kozu moves between platforms. Use the host’s navigation, text scaling, focus model and accessibility settings. [Foundations](foundations.md) defines shared specs. [Platform guidance](../Platform%20references.json) collects official platform documentation.

## Adaptive layout

Choose a layout using the available app window and its safe content area. Evaluate narrow windows, rotation, split screen, keyboard insets, foldable hinges and larger text. Keep navigation and reading order logical as panels move. Apple recommends adapting to window and system characteristics and using system-defined safe areas, margins and guides. [Apple HIG layout](https://developer.apple.com/design/human-interface-guidelines/layout)

| Usable width | Kozu layout |
| --- | --- |
| Below 600 units | Compact navigation. Use one main pane. Push or present detail using the host convention. |
| 600 and above | Where Kozu custom navigation applies, use a 72-unit floating rail centered in the usable height, 16 units from the leading safe edge. Use 8 units of padding, 56-unit targets and 8-unit gaps. When the rail cannot fit vertically, use compact navigation. |
| 720 and above | Show two panes when both can support their content and controls. At larger text sizes or constrained heights, return to one pane. |
| 840 and above | Introduce a sidebar where it improves access to destinations or sections. Keep content to a readable measure and reserve room for the detail pane. |

Use leading and trailing edges for right-to-left layout. Keep the same selected destination, item, scroll position and draft when crossing a layout threshold. Move focus to the equivalent control when the active element changes shape. Keep a detail view accessible after its companion list collapses. Test the boundary values on both sides of each threshold and resize during an active task.

For [dot matrices](foundations.md#dot-matrices), measure the space left after labels, controls and padding. Recompute the whole-column count when that space changes. Use the same 4-unit diameter and 8-unit pitch on both axes, and split unused width equally. Keep progress values and listening controls available even when the matrix fits zero columns.

Kozu thresholds describe custom layouts. Native iPad apps can use a host tab bar or an adaptable sidebar. Android’s published window classes use width boundaries at 600 dp and 840 dp for compact, medium and expanded layouts. Use Android classes alongside content-fit checks, and use the Kozu 720-unit threshold to evaluate the two-pane layout. [Apple HIG tab bars](https://developer.apple.com/design/human-interface-guidelines/tab-bars) · [Android window size classes](https://developer.android.com/develop/adaptive-apps/guides/use-window-size-classes)

## Targets and scaling

Kozu’s regular touch target is at least **48 × 48** logical units. The **32 × 32** compact pointer minimum applies to a dense pointer presentation. The default sibling gap is **8** units between hit regions. Use more space for significant focus effects, destructive actions next to routine ones and adjacent controls with small rendered labels. Keep touch targets at regular size on mixed-input devices.

Apple’s accessibility guidance lists these platform-specific recommended sizes in points. Use the Apple values when evaluating native controls and accommodate the larger size where a Kozu control also follows a larger platform default. Apple’s general button guidance calls for a 44 × 44 pt hit region, or 60 × 60 pt in visionOS. Its accessibility guidance also gives approximate padding recommendations around bezeled and borderless elements. Review the actual native control and the distance between effective hit regions. [Apple HIG accessibility](https://developer.apple.com/design/human-interface-guidelines/accessibility) · [Apple HIG buttons](https://developer.apple.com/design/human-interface-guidelines/buttons)

| Apple platform | Apple default | Apple listed minimum |
| --- | --- | --- |
| iOS and iPadOS | 44 × 44 pt | 28 × 28 pt |
| macOS | 28 × 28 pt | 20 × 20 pt |
| tvOS | 66 × 66 pt | 56 × 56 pt |
| watchOS | 44 × 44 pt | 28 × 28 pt |
| visionOS | 60 × 60 pt | 28 × 28 pt |

Apple’s typography chapter lists default and minimum text sizes of 17 and 11 pt for iOS and iPadOS, 13 and 10 pt for macOS, 29 and 23 pt for tvOS, and 16 and 12 pt for watchOS. Use the host’s native type roles for chrome. Kozu prefers 17 logical units for app prose where it fits the platform and reading context. [Apple HIG typography](https://developer.apple.com/design/human-interface-guidelines/typography)

Test Kozu’s primary content and controls through at least **200%** text size, and at larger native accessibility settings wherever supported. The Kozu watch baseline is **140%**. On watchOS, support the largest Dynamic Type category or its equivalent for primary content. Apple describes that largest size as above 140% and uses support for it in its Larger Text evaluation. On tvOS, test the largest native category and seating distance. Apple evaluates tvOS at its largest category or equivalent. [Apple Larger Text evaluation criteria](https://developer.apple.com/help/app-store-connect/manage-app-accessibility/larger-text-evaluation-criteria)

## Apple platforms

- **iPhone and iPad.** Use native navigation, sheet dismissal, menus and safe areas. Install Inter for app content and scale custom text by role with relative SwiftUI fonts or `UIFontMetrics` in UIKit. Let the tab or sidebar use system type. At larger settings, stack inline labels with values, wrap actions and keep focused fields above the keyboard. Exercise VoiceOver, Voice Control, Full Keyboard Access and system accessibility settings on supported devices. [Apple HIG layout](https://developer.apple.com/design/human-interface-guidelines/layout) · [Apple custom fonts in SwiftUI](https://developer.apple.com/documentation/swiftui/applying-custom-fonts-to-text) · [Apple UIFontMetrics](https://developer.apple.com/documentation/uikit/uifontmetrics)
- **Mac.** Use native window chrome, menus, dialogs and keyboard shortcuts. Default to regular targets on shared layouts and use the compact pointer density for utility controls or dense data views. macOS lacks Dynamic Type. Provide app-level text scaling where needed for primary content and check window resizing and full keyboard operation. [Apple HIG typography](https://developer.apple.com/design/human-interface-guidelines/typography) · [Apple HIG focus and selection](https://developer.apple.com/design/human-interface-guidelines/focus-and-selection)
- **Apple TV.** Use remote directional focus. Keep the focused object obvious across a room, leave space for its enlarged shape and keep selection visually distinct. Start focus at the most meaningful visible action, and recover it predictably when a focused item disappears. Keep primary content within host safe areas. Apple’s TV layout guidance specifies 60 pt top and bottom and 80 pt horizontal insets for primary content. [Apple HIG layout](https://developer.apple.com/design/human-interface-guidelines/layout#tvOS) · [Apple HIG focus and selection](https://developer.apple.com/design/human-interface-guidelines/focus-and-selection#tvOS)
- **Apple Watch.** Give the first screen one useful value or status and one obvious next action. Use stack layouts, short copy and a readable tonal background. Respect the rectangular display’s corner insets. Keep scrolling and the Digital Crown usable at maximum text size. Use native control and complication semantics, and test on the smallest supported watch. [Apple HIG designing for watchOS](https://developer.apple.com/design/human-interface-guidelines/designing-for-watchos)

## Android platforms

- **Phone, tablet and foldable.** Apply system insets for bars, the IME and separating display features. Keep meaningful content and targets clear of screen cutouts. Test multitasking, a folded or unfolded window and the landscape keyboard. Use `sp` for text and test Android’s nonlinear scaling at 200% where available. Keep label containers flexible. [Android adaptive layouts](https://developer.android.com/develop/adaptive-apps/guides/use-window-size-classes) · [Android font scaling](https://developer.android.com/about/versions/14/features#non-linear-font-scaling)
- **Google TV and Android TV.** Make every action reachable with D-pad direction, Select and Back. Prefer a predictable grid or list and leave room for focus effects. Test focus during scrolling, filtering and returning from detail. Use large text and judge the layout at viewing distance. [Android TV focus system](https://developer.android.com/design/ui/tv/guides/styles/focus-system) · [Android TV navigation](https://developer.android.com/design/ui/tv/guides/foundations/navigation-on-tv)
- **Wear OS.** Keep content and controls inside the usable round region on round watches. Use a tonal surface, a short hierarchy and native scroll, rotary and accessibility behavior. Put long histories and complex input on the paired app or a full watch app screen. Check truncation, hit regions and input at the smallest supported viewport and largest available type. [Wear OS common layouts](https://developer.android.com/design/ui/wear/guides/foundations/common-layouts) · [Wear OS app quality](https://developer.android.com/develop/adaptive-apps/quality-guidelines/wear-app-quality)

## Widgets

Start with a single glanceable value and its label. Add a timestamp if the value goes stale, and one clear deep link or action if the host supports it. Preserve the value, status and destination across sizes. Expand through a tested sequence such as value, then trend, then detail. Fit the actual allocation and its margins.

- **WidgetKit.** Use the supported family, host margins and container background. Apple recommends a 16-pt margin for most widgets and documents exceptions for tighter groups and certain hosts. Check full-color, accented and other applicable host rendering modes. Status must stay understandable when the host recolors the content. [Apple HIG widgets](https://developer.apple.com/design/human-interface-guidelines/widgets) · [Apple WidgetKit rendering modes](https://developer.apple.com/documentation/widgetkit/optimizing-your-widget-for-accented-rendering-mode-and-liquid-glass)
- **Android app widgets.** Treat grid span as a placement request and respond to the launcher’s allocated bounds. Select a supported layout for that size. Use host corners and inner radii, and test on a real launcher at small, wide and large sizes. [Android widget sizing](https://developer.android.com/design/ui/mobile/guides/widgets/sizing) · [Android app widget layouts](https://developer.android.com/develop/ui/views/appwidgets/layouts)

## Web

Use [palette variables](../web/palette.css) with [base styles](../web/kozu.css) and [component primitives](../web/components.css). Use semantic HTML for buttons, links, form controls, sections and headings. Expose name, role, value and state for custom interactions. Match DOM order to visual reading order. Use CSS logical properties, fluid sizing, relative type and browser zoom support.

Test with keyboard and screen reader at baseline and enlarged text. Verify reflow at the equivalent of a 320 CSS-pixel viewport as described by WCAG, including when dense content needs a specific exception. Keep focused controls visible above fixed navigation and overlays. Respond to reduced motion, provide a solid treatment for reduced transparency and verify controls with browser-forced colors. [WCAG reflow](https://www.w3.org/TR/WCAG22/#reflow) · [WCAG focus visibility](https://www.w3.org/TR/WCAG22/#focus-visible) · [WCAG focus not obscured](https://www.w3.org/TR/WCAG22/#focus-not-obscured-minimum)

## Release verification

| Check | Evidence to capture |
| --- | --- |
| Layout and input | Smallest and largest supported sizes, both sides of responsive thresholds, supported orientations, live resize, touch, pointer and keyboard. For TV and watch, include remote or rotary input. |
| Accessibility | Names, roles, values, focus and return order with a screen reader and physical keyboard where supported. Include largest native text, 200% text or watch baseline, right-to-left, a long locale, contrast, reduced motion and opaque surfaces. |
| Dot matrices | Check widths immediately below, at and above 4 and 12 units and at a wider layout. Verify whole circles, 8-unit horizontal and vertical pitch, equal margins, and the row count for each variant. For progress, verify 0%, 100% and an intermediate value that lights an odd number of dots. Count trailing dim dots in static specimens and check that each column fills top then bottom from the leading edge. Confirm that resizing preserves the exact visible and accessible percentage. |
| Workflows | Run the Accounts, Tasks and Activity entry points through success, loading, empty and error. Verify pending and retry behavior with real navigation and state, including back and restore. |
| Performance | On representative shipping hardware, scroll text across glass, open an overlay, and run listening or progress while work updates. Compare the brightest and darkest reachable backdrop crops against the opaque fallback. Inspect frame timing and responsiveness. Repeat with an opaque surface when evaluating a glass regression. |
| Adapter parity | Compare role aliases, palette steps, target geometry and behavior across the native specimen and affected adapters. Capture host differences that change layout or input. |

From the checkout, run the geometry self-test, geometry verification and system verification. Run the web check with an existing local task scratch directory and exercise changed interactions in the [interactive handbook](../web/guide.html). Record the build, host or browser, viewport, settings, workflow and result in the QA evidence. A static export verifies visual layout. Test host input, assistive technology and blur performance in the running implementation.

```sh
python3 -B tools/verify_geometry.py --self-test
python3 -B tools/verify_geometry.py
python3 -B tools/verify_system.py
node web/check.mjs /path/to/task-scratch
```
