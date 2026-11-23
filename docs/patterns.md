# Patterns

Use these patterns to assemble Kozu screens from the [component catalog](components.md). Keep the same task order, labels and outcome when adapting a flow to a different viewport or input. Pair each flow with [foundations](foundations.md) and the [platform release checks](platforms.md#release-verification).

## Page structure and navigation

Give the page a descriptive title and a clear first action or next decision. Put persistent destination navigation at the shell level. Use tabs or a segmented control inside a destination only for peer views or a bounded set of options, such as Analytics time ranges. Expose the selected value and keep keyboard focus distinct from selection.

Use a continuous sheet to group content that reads or scrolls together, such as an account summary and its transactions. Use layered content to keep the current task visible while showing related detail, such as a transcript and an agent inspector. Use compact rows for repeated items with consistent leading labels, trailing data or actions, and room for longer text. Give a row one clear primary activation. Use separate targets for secondary actions and expose their names.

Keep list selection, scroll, filters and unsaved input when navigation adapts or a user returns from detail. After an item disappears, move focus to a meaningful neighbor, the list heading or another stable target. Avoid moving focus when new data arrives during reading or entry. [Apple HIG layout](https://developer.apple.com/design/human-interface-guidelines/layout) · [Apple HIG focus and selection](https://developer.apple.com/design/human-interface-guidelines/focus-and-selection)

## Screen states

| State | Show | Behavior and verification |
| --- | --- | --- |
| Normal | Real content, context and the next action. | Enter, operate and leave with every supported input. Give selected, pressed and focused controls distinct treatment. |
| Initial loading | A status that names what is loading. Reserve space for the expected content when possible. | Keep useful navigation available. Hide decorative placeholders from assistive technology. Show progress only from a measurable numerator and total. |
| Refreshing | The last valid content with a refresh indicator. Include a freshness label when it affects decisions. | Preserve scroll, filters and focus. Replace data when the refresh completes. If it fails, retain the prior content and give a retry. |
| Empty | A specific description and an action when there is a useful next step. | Distinguish a new list from an empty search and a valid zero. Example first-run copy is “No tasks yet” with “New task”. A filtered result can offer “Clear filters”. |
| Error | The affected operation, its impact and a recovery action. | Keep input and last valid data where safe. Associate errors with the fields or region they affect. Use a page-level error for an unavailable page and a local message for a local failure. |
| Pending change | The affected item, its pending status and any available cancel action. | Prevent duplicates while a request is in flight. Keep keyboard focus stable and announce the confirmed outcome. |
| Success | The confirmed result near the affected content. | A brief confirmation can accompany an updated view. Keep receipts and outcomes available in their destination. Offer Undo when the change is safely reversible. |

Use polite status announcements for results and background updates. Reserve an assertive announcement or alert for urgent information. Keep the live region separate from frequently changing data. A reader should hear “Task queued” once without having focus taken away. Keep visible messages long enough to read and put persistent outcomes in the content. [Apple HIG feedback](https://developer.apple.com/design/human-interface-guidelines/feedback) · [W3C status messages](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html)

## Forms, actions and overlays

1. Give each field a visible label and programmatic association. Put instructions and formatting examples near the field. Keep entry intact when validation fails. Present errors beside the affected fields and use a linked summary for long forms.
2. Use an action label that names the operation, such as **Send payment**, **Queue task** or **Copy report**. For pending requests, show status close to the action and prevent repeat submission. Distinguish cancellation from a completed operation and distinguish an uncertain result from a confirmed failure.
3. Keep routine explanations and validation in context. Use a sheet or dialog when a focused decision, review step or consequential confirmation needs the user’s attention. Keep the task short, name the consequence plainly, and offer a clear route back.
4. Move focus into a modal on entry. Keep its background inactive and provide a visible dismiss action with the platform’s normal keyboard or remote equivalent. On dismissal, return focus to the invoking control or a logical successor if it has disappeared. For a consequential action, choose initial focus that lets people read the consequences and make a deliberate choice.

Use native modal and form controls wherever they provide the required behavior. In custom web dialogs, test Tab, Shift+Tab, Escape and focus return. Test dismissal with an incomplete draft and interruption during submission. [Apple HIG modality](https://developer.apple.com/design/human-interface-guidelines/modality) · [Apple HIG alerts](https://developer.apple.com/design/human-interface-guidelines/alerts) · [W3C modal dialog pattern](https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/)

## Accounts

### Balance and transactions

Start the account home with the account name, available balance and currency. Keep Pay and Request near the balance and make each target’s name unambiguous. Align transaction amounts in Inter with tabular figures. Format signs, decimal separators and currency by locale. If styling divides the amount, provide one complete accessible value in the natural reading order. Use Morgan Lee and Sam Rivera in sample transactions.

Group recent transactions under readable headings. Use continuous sheets with clear separation between balance, actions and history. Show an explicit stale timestamp when updating fails and keep the last known value identified as such. A zero balance is a real value. If there are no transactions, explain that state in the history section.

### Pay or request

Let people confirm the recipient, amount and currency before the final action. Show the actual effect and operation status on completion. If the result is uncertain, direct the person to the latest status before allowing another submission. Keep the entered data available on recoverable errors and ensure the recovery path preserves the transaction context.

### Analytics and goals

Use a time-ordered needle-bar chart. Indicate the selected interval with a distinct mark and show its date or range and numeric value beside the chart. Support touch and keyboard selection and expose the same selected value to assistive technology. Provide a readable summary or accessible list of data when needed. On a range change, preserve the selected date when it still exists. Otherwise choose a predictable interval and update its label and summary together.

A goal bar uses saved amount divided by target. Show both localized amounts and the resulting state. When a goal is exceeded, cap the visual fill at the full track while preserving the real amount in the label. When a target is missing or zero, offer the appropriate setup action and omit the ratio.

## Tasks

### Listening

Start listening from an explicit control. Request microphone access in the context of that action and explain the next step if it is denied or unavailable. While listening, show **Listening**, a visible **Stop** control and an adaptive [dot matrix](foundations.md#dot-matrices). Use three rows for compact activity and up to seven for a wide peak waveform. Let the track grow by whole columns while keeping the Stop target at least 48 units. Represent peaks with whole lit and unlit dots. Under reduced motion, keep the waveform steady and preserve the same label and control.

When listening ends, stop the animation and capture. Show the next valid state, such as a transcript, a draft to review or an actionable error. Preserve a usable draft when processing fails. Test repeated starts and stops, permission denial, and switching destinations while recording or processing.

### Review and queued work

Show what the task will do and any input that can be reviewed or edited before it is queued. Use **Inbox**, **Flow** and **Scout** as agent names and **Detailed** as the setting label. Keep the order of the transcript, review actions and agent details consistent when panels change. For a queued task, show the task name, current status and available actions. Expand details in place or open them using the host’s navigation at compact widths.

Use clear state names such as Draft, Queued, Running, Paused, Completed and Failed where the work supports those states. A completed state includes the result or a route to it. A failed state gives the next available action. A repeat after failure should produce a single intended task and preserve context.

### Progress

For measurable work, use a two-row [dot matrix](foundations.md#dot-matrices). Keep equal outer insets around the row, with the task label and exact percentage around the available track. Fit whole columns to that track. Apply the shared floor formula to all visible dots and fill from leading to trailing, top then bottom in each column. At 0% leave every dot dim. At 100% light every dot. Show the exact reported percentage separately and expose it once as the labeled progress value, including when the track fits zero columns. For unmeasurable work, name the current stage in an indeterminate state. Switch to determinate when the total becomes available. Announce meaningful stage changes without announcing every animated frame. [Apple HIG progress indicators](https://developer.apple.com/design/human-interface-guidelines/progress-indicators)

## Activity

Present the command, evidence and outcome in that reading order. Give incidents a clear name and status. Use Orange with a glyph and status word for attention, Blue for information and investigation, and Green for recovery. Use Menlo for timestamps and machine values. Use body typography for explanations.

Align histogram bins and events to the same time axis. Make the time zone and range clear when they affect interpretation. Keep selected markers and values identifiable with a glyph, label or pattern. Use consistent scales and labeled comparisons across views. Supply a readable event list or summary that carries the same essential information as the chart.

Distinguish no incidents from no results and from a feed that could not load. Keep the latest valid timeline visible during refresh or temporary failure. Show recovery evidence and any report action in the resolved state. Keep report success or failure near the action. On TV, pair this hierarchy with directional focus and distance-readable text.

## Content and localization

Use sentence case and consistent names across controls, descriptions and announcements. Use verb labels for actions, a clear noun for destinations and concise status names. Keep help within the same region as the control. A message such as “Couldn’t load activity. Try again.” gives both the effect and the recovery action.

Localize complete messages and format user data with locale-aware APIs. Keep machine strings selectable and preserve their direction. Give dates and numeric ranges explicit units where a change in scale could confuse readers. Test long labels, mixed-direction content and large text with actual sample data. [Apple HIG writing](https://developer.apple.com/design/human-interface-guidelines/writing) · [Apple HIG right to left](https://developer.apple.com/design/human-interface-guidelines/right-to-left)

## Pattern review

Walk the flow in the [interactive handbook](../web/guide.html) and the affected application. Capture the normal path and its most consequential alternate path. Include empty, stale or unavailable data, a failed request, a second attempt and a resize or navigation change during work. Verify full operation with supported input, focus return, spoken status, larger text and reduced motion. Record the build, context, steps and observed outcome in the QA evidence.
