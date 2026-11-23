# Kozu Group component reference

[Interactive guide](../web/guide.html) · [Foundations](foundations.md) · [Platforms](platforms.md) · [Patterns](patterns.md) · [Tokens](../Kozu.tokens.json) · [Editable kit](../Kozu%20Universal%20UI%20Kit.figcraft)

Use these entries to choose a component, specify its behavior, and check its implementation. On the web, load `kozu.css`, `palette.css`, and `components.css` in that order. Copy the native HTML structure in each example and connect it to application state. For dot grids, also load `web/dot-grid.js` with `defer`. A CSS class supplies appearance. The example identifies behavior that needs a browser or application handler. Test with the real label, content, locale, and screen size you ship.

Use a 48-unit minimum touch target by default. A compact pointer target may be 32 units when the host has no touch requirement. Let targets grow with text, keep focus visible through tone and weight, and keep reading order consistent with the visual layout. Verify at 200% text size, with keyboard and assistive technology, with reduced motion, and against both Paper and Ink. Place product navigation, drawers, and dismiss controls inside the host safe area.

## Foundations

### Color and surfaces

**Choose.** Use Paper for light reading surfaces and Ink for dark workspaces. Use Blue for general action and information, Orange for attention, and Green for recovery. Reserve Gold, Violet, and Rose for comparative series. Graphite is the neutral ramp.

**Anatomy.** Each of the seven ramps publishes eleven steps: 50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950. Reference semantic roles in product surfaces so foreground, tint, action, and focus change together. In a chart, use primitives when the same series must remain recognizable across contexts.

**Variants and states.** Nest one raised surface over the canvas when grouping clarifies reading order. Style hover, pressed, selected, and keyboard focus as distinct conditions. Pair attention, recovery, and information tones with a word or a distinct mark.

**Input and accessibility.** Measure text contrast against its actual background in both roles. Check the boundary of every necessary control and data mark. Verify foreground/background pairs separately on tinted, frosted, selected, and focused surfaces.

**Implementation.** Apply a surface role to the document or a contained workspace. Load the shared CSS before using these roles.

```html
<section data-theme="dark" class="kozu-surface">
  <h2>Activity</h2>
  <p>Three transfers completed.</p>
</section>
```

**Pitfall.** A well-contrasted color in the palette can become unreadable when composited over a material. Measure the final pixels.

### Typography

**Choose.** Use Inter for reading, controls, and financial values. Set compact display or voice headings in Helvetica Neue with Inter and system sans as fallbacks. Use Menlo for telemetry and preserve the native system face in platform chrome.

**Anatomy.** Align measures and values on one baseline and use tabular lining figures. For a split balance, keep fractional digits legible and retain a complete localized currency string for assistive technology.

**Variants and states.** Use size and weight to order headings. Use secondary ink for supporting text. Allow labels and text blocks to expand before tightening their measure or changing the layout.

**Input and accessibility.** Preserve semantic heading order at every width. In web layouts use relative font sizes and test 200% text and 320 CSS pixels with long localized labels. Preserve system text settings on native platforms.

**Implementation.** Apply the role classes to existing semantic elements.

```html
<h2 class="kozu-display">Account balance</h2>
<p class="kozu-numeral">$12,480.75</p>
<p class="kozu-telemetry"><time datetime="14:32:00">14:32 UTC</time></p>
```

**Pitfall.** Fixed-height controls clip ascenders, long labels, or the second line when text size increases.

### Spacing and shape

**Choose.** Use spacing to show which label, value, control, or row belongs together. Use a continuous sheet for a connected task and group independent summaries in cards.

**Anatomy.** Start with 8 units between related controls, 16 at panel edges and between groups, and 24 for larger breaks. A 24-unit outer radius and 8-unit inset yield a 16-unit inner radius. For a smaller inset surface use `max(0, outerRadius - inset)`.

**Variants and states.** Increase outer padding on wider layouts while keeping row density readable. Reflow side-by-side controls into rows when text consumes the available measure.

**Input and accessibility.** Leave room for a 48-unit touch target and the focused fill. Keep DOM order aligned with visual order across breakpoints. Avoid containers that clip focus or text.

**Implementation.** Use the shared stack and row classes with native content.

```html
<div class="kozu-stack">
  <h2>Transfer details</h2>
  <div class="kozu-row"><span>Total</span><strong>$120.00</strong></div>
</div>
```

**Pitfall.** Assigning the same radius to inset and outer panels makes their corners diverge visually.

### Icons

**Choose.** Use a familiar glyph to aid recognition or add a redundant status cue. Keep a visible label for unfamiliar commands, and group utility icons where users can predict their purpose.

**Anatomy.** Use the supplied Lucide library on a 24-unit grid at 1.8-unit source stroke. Center visible ink within the control. In a text button, scale the ink to the label’s cap height and balance the slots around the label.

**Variants and states.** Pair the selection check and the status glyph with labels or structural semantics. Match glyph color to the adjacent text when both carry the same meaning.

**Input and accessibility.** Mark redundant graphics decorative. Give the enclosing button a concise accessible action name. Give standalone meaningful graphics text or an accessible equivalent.

**Implementation.** Use the shared icon sizing inside an icon button and reference the bundled artwork. Preserve its license when redistributing.

```html
<button class="kozu-button kozu-icon-button" type="button" aria-label="Add item">
  <svg class="kozu-glyph" viewBox="0 0 24 24" aria-hidden="true">
    <path d="M5 12h14M12 5v14"/>
  </svg>
</button>
```

**Pitfall.** An unlabelled button can expose only the icon file name or announce “button” without the action.

### Motion and materials

**Choose.** Use static directional light, grain, or matte surfaces to establish depth. Use motion for a running process, an immediate state change, or continuity between two positions.

**Anatomy.** Use 28 units of backdrop blur on frosted controls, cards, and toolbars, and 40 on overlays. Start with light #FCFCFC at 42% for controls, 52% for cards and toolbars, and 70% for overlays. Start with dark #0D1726 at 34%, 44%, and 60% respectively. Keep the underlying texture visible and limit blur to the area behind the floating surface.

**Variants and states.** Provide an opaque surface equivalent for reduced transparency. Use opaque sheets for dense reading and compare frosted and opaque samples over the same texture. Test text and control contrast against the brightest and darkest crop before releasing. Use short easing for optional transitions and keep a steady waveform or static busy mark under reduced motion.

**Input and accessibility.** Honor reduced-motion preferences and preserve the visible state, stop control, focus position, and completion message. Test moving and static examples with the same reading order.

**Implementation.** Offer the opaque surface as the base and enable frosted rendering as an enhancement.

```html
<section class="kozu-surface kozu-material" aria-labelledby="workspace-title">
  <h2 id="workspace-title">Workspace</h2>
</section>
```

**Pitfall.** Stacking several full-width layers of backdrop blur raises rendering cost and makes the foreground harder to measure.

## Actions

### Button

**Choose.** Use a button for a command, submission, or state change. Give the primary action to the most important next step. Use a link for navigation to a URL.

**Anatomy.** Use an action label, balanced inline padding, and a 48-unit minimum target. When an icon appears with text, center the label within the whole control and keep enough room at both ends.

**Variants and states.** Use filled for primary, tonal for secondary, and quiet for tertiary. Keep a disabled reason nearby if users can resolve it. Use a busy label and block repeat submissions while a request runs.

**Input and accessibility.** Use a native button. Space and Enter activate it. Give ordinary commands `type="button"`, and set `type="submit"` only for the action that submits the form. Toggle buttons expose `aria-pressed`.

**Implementation.** Connect the button to exactly one user action. Update status separately when completion is asynchronous.

```html
<button class="kozu-button kozu-primary" type="submit">Save changes</button>
```

**Pitfall.** Several filled actions compete for priority and weaken the next step.

### Icon button

**Choose.** Use for a familiar or repeated command in a tight toolbar. Add visible text when the icon can reasonably have two meanings.

**Anatomy.** Center a 24-unit glyph inside the 48-unit target. Use a pill or round fill and keep neighboring targets clear of the icon’s hit area.

**Variants and states.** Use tonal or quiet styles for utilities. For a mute or pin toggle, keep the accessible name stable and signal its pressed state.

**Input and accessibility.** Use a native button, keyboard activation, and an action name such as “Copy link”. Decorative icon children stay out of the accessible name.

**Implementation.** Provide a tooltip only when explanation helps and retain the action name on the button.

```html
<button class="kozu-button kozu-icon-button" type="button" aria-label="Pin item" aria-pressed="false">
  <svg class="kozu-glyph" viewBox="0 0 24 24" aria-hidden="true">
    <path d="M6 4h12v16l-6-4-6 4z"/>
  </svg>
</button>
```

**Pitfall.** Shrinking the hit area to the visible glyph makes adjacent actions hard to distinguish by touch.

## Inputs

### Text field

**Choose.** Use a single line for a name, code, amount, or other short answer. Set the specific `type`, `autocomplete`, and `inputmode` that match the value.

**Anatomy.** Stack a persistent label, a filled control at least 48 units tall, and helper or error text. Use 6–8 units between label and control, with another 6–8 before help.

**Variants and states.** Support empty, filled, focused, invalid, disabled, and read-only. Keep a read-only value selectable. Give invalid fields a localized error that describes the correction.

**Input and accessibility.** Associate the label and descriptions by IDs. Use a solid focus fill with paired ink and preserve native input affordances. Set `aria-invalid` when validation finds an error. Preserve caret movement, selection, paste, and autofill.

**Implementation.** Keep instructions adjacent and include the error ID in `aria-describedby` when it appears.

```html
<div class="kozu-field">
  <label for="reference">Payment reference</label>
  <input class="kozu-input" id="reference" name="reference" aria-describedby="reference-help">
  <small id="reference-help">Appears on the recipient’s statement.</small>
</div>
```

**Pitfall.** Placeholder-only labels disappear just when the user needs to confirm the field’s purpose.

### Search field

**Choose.** Use to query a collection or a destination index. Use a regular text field when collecting a value for a form.

**Anatomy.** Pair a labelled 48-unit input with a search icon when useful, an optional clear or submit action, and an adjacent result area. Keep both inset slots balanced if the input has a leading and trailing action.

**Variants and states.** Support empty, querying, no results, populated, and error states. Keep the query visible after submission. For local filtering, show the matching count after an update.

**Input and accessibility.** Use `type="search"` with an associated label. Announce concise count changes with a polite status, and keep focus in the field during filtering. If adding an ARIA combobox, implement its complete keyboard and active-option model.

**Implementation.** Wrap a submitted query with a search landmark or use the same labelled input to filter results in place.

```html
<form role="search" action="/search" class="kozu-field">
  <label for="query">Search projects</label>
  <input class="kozu-input" type="search" id="query" name="q">
</form>
```

**Pitfall.** Replacing or focusing the results on each keystroke interrupts typing and assistive announcements.

### Text area

**Choose.** Use for notes, descriptions, and messages expected to span several lines.

**Anatomy.** Use the same label and description structure as a text field. Give the editable region about three visible lines at first and preserve vertical resizing or comfortable growth.

**Variants and states.** Provide empty, filled, read-only, invalid, and disabled states. If the service has a length limit, show it near the field and report the remaining count at useful intervals.

**Input and accessibility.** Preserve newline, selection, paste, and input-method composition. Keep Enter available for a newline. Document any optional send shortcut adjacent to the editor.

**Implementation.** Set an initial row count and connect the help to the field.

```html
<div class="kozu-field">
  <label for="note">Handoff note</label>
  <textarea class="kozu-input" id="note" name="note" rows="3" aria-describedby="note-help"></textarea>
  <small id="note-help">Include the decision and its owner.</small>
</div>
```

**Pitfall.** Intercepting plain Enter for submission can send incomplete text and break input methods.

### Select

**Choose.** Use for one choice from a known list when a radio group would consume too much space. Use a searchable picker when the list is long and typing would materially help.

**Anatomy.** Provide a persistent label, selected value or prompt, disclosure marker, and the native option list. Keep the closed control at least 48 units tall.

**Variants and states.** Support optional and required selection, disabled options, and grouped options. Include an empty choice for optional data users may need to clear.

**Input and accessibility.** Prefer the native select so the platform controls arrows, type-ahead, dismissal, and mobile pickers. Associate the label. Put instructions outside the option text.

**Implementation.** Match the stored value with the option’s stable value. Localize the visible wording independently.

```html
<div class="kozu-field">
  <label for="format">Export format</label>
  <select class="kozu-input" id="format" name="format">
    <option value="csv">CSV</option>
    <option value="pdf">PDF</option>
  </select>
</div>
```

**Pitfall.** A custom menu styled like a select often loses native type-ahead and form semantics.

### Checkbox

**Choose.** Use for independent options or multi-selection. A grouped control may represent all, some, or none of its descendants.

**Anatomy.** Center the mark beside its label within a 48-unit labelled row. Keep related options in one fieldset. Use a check mark for selected and a dash for mixed.

**Variants and states.** Support unchecked, checked, mixed, focused, and disabled. Assign the native `indeterminate` property from child state and update it whenever the group changes.

**Input and accessibility.** Let the entire label activate the control. Space toggles the focused native checkbox. Use a visible legend to name the group.

**Implementation.** Give each checkbox a stable value. Browser form submission includes the checked values.

```html
<fieldset class="kozu-options">
  <legend>Include in export</legend>
  <label class="kozu-choice"><input type="checkbox" name="include" value="notes"> Notes</label>
</fieldset>
```

**Pitfall.** A mixed visual mark alone leaves assistive technology reporting the wrong state.

### Radio button

**Choose.** Use when exactly one of a few options can be selected and the user benefits from comparing all choices.

**Anatomy.** Place a selected-dot mark and label in a 48-unit row. Keep a shared legend and consistent alignment across options.

**Variants and states.** Support selected, unselected, focused, and disabled. Preselect a safe default if the product has one. Use a separate explicit “None” option when the user can clear the choice.

**Input and accessibility.** Give radios in one group the same name and distinct values. The browser handles Tab into the group and arrow movement among options.

**Implementation.** Use one labelled native input per choice.

```html
<fieldset class="kozu-options">
  <legend>Update frequency</legend>
  <label class="kozu-choice"><input type="radio" name="frequency" value="daily" checked> Daily</label>
  <label class="kozu-choice"><input type="radio" name="frequency" value="weekly"> Weekly</label>
</fieldset>
```

**Pitfall.** Reusing a name across unrelated choices in the same form merges the groups.

### Switch

**Choose.** Use for a setting that turns on or off immediately. Use a checkbox when a choice is saved later with the rest of a form.

**Anatomy.** Use a stable setting label and a track with a moving thumb. The track is about 42 × 26 units inside a labelled target at least 48 units tall.

**Variants and states.** Support off, on, focused, pending, and disabled. If saving fails, revert to the confirmed value and report the failure.

**Input and accessibility.** Use a checkbox with `role="switch"`. Its native checked state is the source of truth. Space changes the setting. Keep the name stable in both states.

**Implementation.** Listen for the checkbox’s change event and persist the new state with your application.

```html
<label class="kozu-switch">
  <input type="checkbox" role="switch" name="reminders">
  <span class="kozu-switch-track" aria-hidden="true"></span>
  <span>Weekly reminders</span>
</label>
```

**Pitfall.** Changing the name from “Enable alerts” to “Disable alerts” mixes the setting’s identity with its state.

### Segmented control

**Choose.** Use for a short mutually exclusive choice within one task, such as a time scale. Use tabs when the chosen item owns a distinct content panel.

**Anatomy.** Use a tonal track with a 4-unit inset, 48-unit option targets, and similarly weighted labels. Let longer labels or options wrap as a group.

**Variants and states.** Support selected, unselected, focused, and disabled. Apply the selected condition with a local fill and weight. A layout may wrap the segments where required.

**Input and accessibility.** Use visually styled radios for a single selection and retain their arrow behavior. Name the group. A focused selected option needs a distinct visible treatment.

**Implementation.** Use one name across the group and apply the selected style through the native checked state.

```html
<fieldset class="kozu-options">
  <legend>Time range</legend>
  <div class="kozu-segmented">
    <label><input type="radio" name="period" value="week" checked><span>Week</span></label>
    <label><input type="radio" name="period" value="month"><span>Month</span></label>
  </div>
</fieldset>
```

**Pitfall.** Treating selected segments as independent toggles lets two incompatible values appear active.

### Slider

**Choose.** Use for an approximate bounded value that can change continuously or in steps. Provide a number field when users often need an exact entry.

**Anatomy.** Include a label, track, thumb, min/max limits when useful, and a readable current value. Keep the interaction region at least 48 units tall.

**Variants and states.** Support continuous or stepped values, focus, dragging, and disabled. Align labels with the real min and max. Keep the current value synchronized on input.

**Input and accessibility.** Use a native range input. Keep the track and thumb distinct when focus changes the surrounding fill. The browser handles arrows and Home/End. Expose the unit in the label or set `aria-valuetext` when a bare number would be ambiguous.

**Implementation.** Use the same value to update the displayed output and the affected preview. Avoid announcing every pointer movement through a live region.

```html
<div class="kozu-field">
  <label for="volume">Volume, percent</label>
  <input class="kozu-range" id="volume" type="range" min="0" max="100" value="60">
  <output for="volume">60%</output>
</div>
```

**Pitfall.** A range labeled only at its ends leaves users guessing the current setting.

### Date picker

**Choose.** Use a native date field for one calendar date. For ranges, use separate start and end fields and validate their relationship. Provide a task-specific calendar only when the calendar context is essential.

**Anatomy.** Provide a persistent label, filled 48-unit control, and concise constraint text where useful. Distinguish the date from an instant. Store it as a calendar date.

**Variants and states.** Support empty, selected, constrained, invalid, and disabled. Make minimum and maximum requirements visible and ensure server and browser validation agree.

**Input and accessibility.** Use the native keyboard and calendar behavior. Let the platform render its locale format. Restore focus to the date field when a custom calendar closes.

**Implementation.** Set `min` to the first eligible date if the app has one.

```html
<div class="kozu-field">
  <label for="review-date">Review date</label>
  <input class="kozu-input" id="review-date" name="date" type="date" min="2026-01-01">
</div>
```

**Pitfall.** Converting a local calendar date to midnight UTC before formatting can shift the displayed day.

### Time picker

**Choose.** Use for a clock time. Pair it with a date and an explicit zone when it schedules an event across devices or locations.

**Anatomy.** Keep a persistent label, filled 48-unit input, and a visible zone or schedule note. Use `step` to communicate supported increments and explain them when needed.

**Variants and states.** Support unset, set, outside allowed hours, and disabled. For scheduling, handle times that are ambiguous or missing on a daylight-saving transition.

**Input and accessibility.** Let the platform provide clock or keyboard interaction and 12/24-hour presentation. Describe time zone and business rules alongside the field.

**Implementation.** Interpret the submitted wall time with the selected date and time zone in the application.

```html
<div class="kozu-field">
  <label for="review-time">Review time</label>
  <input class="kozu-input" id="review-time" name="time" type="time" aria-describedby="review-zone">
  <small id="review-zone">Time zone: America/New_York</small>
</div>
```

**Pitfall.** A time value without its intended zone can schedule the right wall time for the wrong audience.

### Chip

**Choose.** Use a chip for a compact filter, an applied value, or a removable token. Use a badge for passive information.

**Anatomy.** Center the label and optional mark in the rounded fill. Keep a 48-unit activation or removal target. If a token has separate actions, give each action its own sibling control.

**Variants and states.** Support unselected, selected with a check, removable, disabled, and focus. Allow chip groups to wrap within their container.

**Input and accessibility.** For independent filters use native buttons with `aria-pressed`. Name a remove action “Remove [value]” and focus the next available control after removal.

**Implementation.** Update `aria-pressed` and the result count from the same filter state.

```html
<button class="kozu-chip" type="button" aria-pressed="false">Unread</button>
```

**Pitfall.** A removal button nested inside a filter button invalidates the markup and makes activation ambiguous.

## Navigation

### Tabs

**Choose.** Use tabs for sibling panels within one task or record. Use page links for destinations with their own document or URL identity.

**Anatomy.** A labelled tablist leads a set of 48-unit tab targets. Pair each tab with its corresponding panel and use a selected fill or weight. The panel follows in reading order.

**Variants and states.** Show one active panel. Let labels wrap or the tab strip scroll within its own region, keeping the selected option visible.

**Input and accessibility.** Tab enters the active or currently roving tab. Left/Right move focus in a horizontal tablist. Home and End move to its bounds. Use Space or Enter to select if activation has a delay, and set `aria-selected` independently of focus.

**Implementation.** Apply the roving `tabindex` and update both panel visibility and selected state together. Use automatic activation only when switching panels is immediate.

```html
<div class="kozu-tablist" role="tablist" aria-label="Project details">
  <button id="summary-tab" role="tab" aria-selected="true" aria-controls="summary-panel">Summary</button>
</div>
<section id="summary-panel" role="tabpanel" aria-labelledby="summary-tab" tabindex="0">
  Project summary
</section>
```

**Pitfall.** Assigning every tab a Tab stop creates redundant keyboard traversal and leaves arrow-key users without the expected behavior.

### Navigation bar

**Choose.** Use a compact bar for a small set of stable top-level destinations below 600 units. Keep the same destination order when switching to the rail.

**Anatomy.** Balance the insets at both ends of the floating bar. Give each destination at least 48 units and use a selected capsule with a visible label. Apply safe-area insets before spacing the bar.

**Variants and states.** Support current, available, and focused destinations. Let labels wrap or offer a different layout for translated or enlarged text.

**Input and accessibility.** Use a labelled navigation landmark and real links. Mark the current page with `aria-current="page"`. Tab follows destination order and Enter navigates.

**Implementation.** Set `aria-current` from the route and retain destination state if the viewport changes.

```html
<nav class="kozu-nav" aria-label="Workspace">
  <a href="/overview" aria-current="page">Overview</a>
  <a href="/activity">Activity</a>
</nav>
```

**Pitfall.** Moving the same destinations into a tab panel changes both their semantics and expected keyboard behavior.

### Navigation rail

**Choose.** Introduce a vertical rail from 600 units when the workspace still benefits from a compact destination set. Introduce a sidebar from 840 when labels, hierarchy, and available width justify it.

**Anatomy.** Float a 72-unit capsule 16 units from the leading safe edge and center it vertically. Use 8-unit inner padding, 56-unit destination targets, and 8-unit gaps. Allow the rail to grow or change layout when labels or safe areas require it.

**Variants and states.** Support current and focused states independently. Use recognizable icons for compact destinations. Add a concise label or tooltip where the icon needs help.

**Input and accessibility.** Use real, named links in a navigation landmark. Preserve focus, selection, scroll, and text input when switching layout. On directional-input hosts, follow native remote focus conventions.

**Implementation.** Apply the rail layout to the route links. Use logical positioning for mirrored layouts.

```html
<nav class="kozu-nav kozu-rail" aria-label="Workspace">
  <a href="/overview" aria-current="page" aria-label="Overview">
    <svg class="kozu-glyph" viewBox="0 0 24 24" aria-hidden="true">
      <rect x="3" y="3" width="7" height="7" rx="1"/>
      <rect x="14" y="3" width="7" height="7" rx="1"/>
      <rect x="3" y="14" width="7" height="7" rx="1"/>
      <rect x="14" y="14" width="7" height="7" rx="1"/>
    </svg>
  </a>
</nav>
```

**Pitfall.** Remounting the navigation and content when the rail appears can erase scroll, edits, or focus.

### Breadcrumb

**Choose.** Use for the hierarchy leading to a page. Use a Back control when the important action is to return to the previous step or history entry.

**Anatomy.** Place a labelled navigation region above the page title. Use an ordered list with consistent separators. Let individual paths wrap at narrow widths.

**Variants and states.** Ancestor crumbs are links. The current item is text with `aria-current="page"`. A collapsed ancestor needs an accessible disclosure if the branch can be reopened.

**Input and accessibility.** Tab visits ancestor links in order. Separate separators from the accessible name. Use a literal label for the navigation region.

**Implementation.** Build ancestors from the content hierarchy and name the final item from the current route.

```html
<nav class="kozu-breadcrumb" aria-label="Breadcrumb">
  <ol><li><a href="/projects">Projects</a></li><li aria-current="page">Quarterly review</li></ol>
</nav>
```

**Pitfall.** A path built from session history can show a different hierarchy each time someone opens the same destination.

### Pagination

**Choose.** Use when a discrete, addressable page improves navigation or recovery. For exploration without a page concept, consider a Load more action with a stable position.

**Anatomy.** Include Previous and Next and a page index or current-range summary. Keep targets 48 units and permit wrapping or a compact arrangement at narrow widths.

**Variants and states.** Show the current page and handle first, intermediate, last, loading, and empty states. When filters shrink the collection, clamp or reset the page.

**Input and accessibility.** Use links for URL-backed pages and use `aria-current="page"` for the current link. On client-side updates, announce the loaded range and keep reading order predictable.

**Implementation.** If the list changes within the same document, update the query parameter, results, and current indicator from one page value.

```html
<nav class="kozu-pagination" aria-label="Result pages">
  <a href="?page=1">Previous</a>
  <a href="?page=2" aria-current="page" aria-label="Page 2">2</a>
  <a href="?page=3">Next</a>
</nav>
```

**Pitfall.** A focusable ellipsis styled like an enabled button promises a destination without providing one.

## Content

### Card

**Choose.** Use for a self-contained summary with independent content or action. Use a continuous sheet when adjacent content needs to be read as one sequence.

**Anatomy.** Use a surface, a heading, and a content area. Add media or actions only when needed. Start with a 24-unit radius and 16–24 units of padding.

**Variants and states.** Use passive, contained-action, or single-link cards. Use a frosted card over a field when depth has a purpose and contrast holds at both crop extremes. Make a selected state explicit when cards belong to a selectable set.

**Input and accessibility.** Use an article or section when content has its own heading. Keep nested actions as distinct targets. Make the interactive element a button or a link.

**Implementation.** Keep the heading and primary action in readable DOM order.

```html
<article class="kozu-card kozu-surface">
  <h3>Monthly report</h3>
  <p>Ready to review.</p>
  <a class="kozu-link" href="/reports/monthly">Open report</a>
</article>
```

**Pitfall.** A click handler on a whole card with nested buttons creates conflicting activation and ambiguous keyboard focus.

### List

**Choose.** Use for entities or events read row by row. Use a table when comparisons depend on stable columns.

**Anatomy.** Align the leading glyph, title and supporting text, and trailing value or action. Keep at least a 48-unit row target for interactive items. Use tabular figures for aligned times and financial values.

**Variants and states.** Support plain, linked, selectable, and grouped rows. Show a localized empty state with a useful action if one exists.

**Input and accessibility.** Use `ul` or `ol` for semantic grouping. Put controls inside the item. Preserve label-to-detail order and use visible focus on each real action.

**Implementation.** Use `time` for timestamps and expose the same ordered content at every width.

```html
<ul class="kozu-list" role="list">
  <li class="kozu-list-row">
    <span>Deployment complete</span><time class="kozu-telemetry" datetime="14:32:00Z">14:32 UTC</time>
  </li>
</ul>
```

**Pitfall.** Using visual position alone to communicate the leading value can reverse the message when reflowing a row.

### Table

**Choose.** Use when users compare values across meaningful columns. Use a list for independent items without comparable attributes.

**Anatomy.** Include a caption and scoped column or row headers. Align numeric columns to the logical end and use tabular figures. Keep sort controls in their headers.

**Variants and states.** Support sorted, filtered, empty, and loading data. Contain horizontal overflow within the table region, keeping the page itself reflowable.

**Input and accessibility.** Use a native table. Set `aria-sort` on the currently sorted header and give the sort button a name. Keep individual cells outside the Tab order unless they contain a real control. A keyboard-focusable scroll region can highlight its caption and headers with focused fill and ink.

**Implementation.** Update row order and `aria-sort` from the same data operation.

```html
<div class="kozu-table-region" role="region" aria-label="Transfer details" tabindex="0">
  <table class="kozu-table">
    <caption>Recent transfers</caption>
    <thead><tr><th scope="col">Reference</th><th scope="col" data-numeric>Amount</th></tr></thead>
    <tbody><tr><th scope="row">Reserve</th><td data-numeric>$120.00</td></tr></tbody>
  </table>
</div>
```

**Pitfall.** Displaying a flattened card version by removing header associations makes the values harder to interpret.

### Accordion

**Choose.** Use to group optional information into named disclosures. Keep deadlines, required instructions, and current errors visible without opening a panel.

**Anatomy.** Each item has a summary at least 48 units high, a disclosure mark, and a content region. Keep summary text visible alongside the mark.

**Variants and states.** Support collapsed, expanded, and focused. Multiple open panels often help comparison. Use single-open behavior only where the relationship calls for it.

**Input and accessibility.** A native `details` and `summary` provide keyboard activation and expanded state. Keep the summary focused on toggle and follow it with the revealed content.

**Implementation.** Use independent native disclosure elements unless the task requires a shared accordion state.

```html
<details class="kozu-accordion">
  <summary>Billing details</summary>
  <p>Invoices appear after each billing period closes.</p>
</details>
```

**Pitfall.** Closing a section while focus remains inside its hidden content leaves keyboard users without a clear position.

### Avatar

**Choose.** Use to identify a person, team, or agent alongside their name. A passive avatar supplements nearby identity text.

**Anatomy.** Place a photo or initials in a circular crop and center the visible subject. Use 40 units for a standalone image by default. Place names adjacent when identity matters.

**Variants and states.** Support real image, initials fallback, and unknown identity. If the avatar opens a profile, give the enclosing link its own 48-unit target and visible focus.

**Input and accessibility.** Use empty alternative text when the adjacent visible name supplies identity. Give the link a clear name if the avatar is the only content.

**Implementation.** Keep a text identity alongside the image and substitute initials when the image is unavailable.

```html
<div class="kozu-row">
  <img class="kozu-avatar" src="../Assets/People/alex.jpg" alt="" width="40" height="40">
  <span>Alex Morgan</span>
</div>
```

**Pitfall.** Initials and an image’s redundant alternative text can make the same name appear twice in the reading order.

### Badge

**Choose.** Use for a brief status or count attached to an entity. Use a chip for a value the user can select or remove.

**Anatomy.** Pair compact wording with an optional distinctive mark. Use restrained tint, a pill shape, and enough padding for localized text to wrap without clipping.

**Variants and states.** Use neutral, informational, attention, and recovery treatments. For counts above a cap, expose the complete count where it matters.

**Input and accessibility.** Keep passive badges outside the Tab order. Include the badge meaning in the adjacent control’s name or description where needed. Announce changes only when the task benefits from them.

**Implementation.** Use a tone and plain-language state.

```html
<span class="kozu-badge" data-tone="success"><span aria-hidden="true">✓</span> Recovered</span>
```

**Pitfall.** An unlabeled orange dot can imply several different conditions without telling anyone which occurred.

### Chart

**Choose.** Use needle bars when selecting a precise period and value, dot matrices for discrete or normalized magnitude, and time-aligned histograms for operational frequency. Use a table to inspect and compare exact values.

**Anatomy.** Provide a title, units, time scale, and visible selected value. Align labels with tabular figures or Menlo for telemetry. Use comparable geometry and common time bins for related series. Dot matrices use whole dots on an 8-unit pitch on both axes, centered in available width.

**Variants and states.** Support selected, empty, no-data, and loading states. Distinguish zero from missing data. Use Blue for information, Orange for attention, and Green for recovery. Use Gold, Violet, and Rose only where an extra comparative series needs separation.

**Input and accessibility.** Give the figure a summary and an available table or text equivalent. Make interactive marks reachable with a keyboard and include the date, value, and unit in their accessible names. Pair colors with labels or distinctive shapes.

**Implementation.** Bind selection and text alternatives to the same data. A selected needle can be a toggle whose accessible name includes the exact value. Render a passive matrix with `data-dot-grid="progress"`, `data-dot-value` from 0 to 100, and separate visible units or counts.

```html
<figure class="kozu-chart">
  <figcaption>Transfer volume in US dollars</figcaption>
  <output class="kozu-numeral">Wednesday · $360</output>
  <div class="kozu-chart-plot">
    <button class="kozu-needle" style="--level: .6" type="button" aria-pressed="true" aria-label="Wednesday, 360 dollars">Wed</button>
  </div>
</figure>
```

**Pitfall.** A tooltip as the only source of values prevents touch, keyboard, and assistive users from obtaining the same data.

## Overlays

### Dialog

**Choose.** Use a modal dialog when the user must resolve a focused choice before continuing. Use an inline control for light adjustments and a sheet for an extended related task.

**Anatomy.** Include a title, concise body, action group, and an explicit visible close or cancel control. Allow internal scrolling. Use a 40-unit backdrop blur on a frosted overlay and a solid equivalent.

**Variants and states.** Support confirm, destructive confirm, and short input. Show submitting and error states inside the dialog. Keep underlying content visually subordinate and inert.

**Input and accessibility.** Open a labelled native dialog with `showModal()`. Focus the safest meaningful control or a leading heading when content requires reading. Support Escape, keep Tab within the modal, and return focus to its trigger or the logical successor.

**Implementation.** Use `method="dialog"` for local responses. For requests, close after success and retain the response state when submission fails.

```html
<dialog class="kozu-dialog" id="archive" aria-labelledby="archive-title">
  <form method="dialog" class="kozu-stack">
    <h2 id="archive-title">Archive report?</h2>
    <div class="kozu-row">
      <button class="kozu-button" value="cancel" autofocus>Cancel</button>
      <button class="kozu-button kozu-primary" value="archive">Archive report</button>
    </div>
  </form>
</dialog>
```

**Pitfall.** Setting the `open` attribute directly renders the element without modal focus containment.

### Sheet

**Choose.** Use a sheet for a focused task that benefits from nearby context, such as export options or a multi-field edit. Use an inline panel for supplementary content that remains available as the user works elsewhere.

**Anatomy.** Anchor the surface to the chosen edge, preserve safe areas, and group the heading, scrollable body, and actions. Let the sheet expand with content up to the viewport limit.

**Variants and states.** Support modal bottom and wide side treatments, plus opaque and frosted surfaces. Preserve draft data on resize and provide clear close behavior when edits are pending.

**Input and accessibility.** Use native modal dialog behavior for a blocking sheet. Provide a visible close control, Escape, and focus return. Keep that control available when content scrolls and offer it alongside any gesture.

**Implementation.** Use the sheet modifier with a labelled dialog. Connect the result to application state after the dialog closes.

```html
<dialog class="kozu-dialog kozu-sheet" id="export" aria-labelledby="export-title">
  <form method="dialog" class="kozu-stack">
    <h2 id="export-title">Export options</h2>
    <button class="kozu-button" value="cancel" autofocus>Close</button>
  </form>
</dialog>
```

**Pitfall.** Swipe-only dismissal excludes keyboard users and can conflict with scrolling.

### Menu

**Choose.** Use for a short set of contextual actions opened from a trigger. Use select for a form value and a navigation list for page destinations.

**Anatomy.** Keep a named trigger, a packed surface, and rows of at least 48 units. Align labels consistently and allow the surface to move away from the viewport edge.

**Variants and states.** Support closed, open, focused, and unavailable actions. Use an explicit menu role only when supplying the complete desktop action-menu interaction model.

**Input and accessibility.** A popover of native buttons supports Tab and Escape and suits a small command list. For an ARIA menu, implement arrow navigation, Home/End, Escape, focus return, and the correct menu item roles.

**Implementation.** Open a native auto popover from its invoker and hide it after an action. For anchored placement, keep the popover near the invoker and within the viewport.

```html
<button class="kozu-button" type="button" popovertarget="actions">More actions</button>
<div class="kozu-menu" id="actions" popover>
  <button type="button">Duplicate</button>
  <button type="button">Rename</button>
</div>
```

**Pitfall.** Adding `role="menu"` to a regular button list changes keyboard expectations without supplying arrow behavior.

### Tooltip

**Choose.** Use for short, nonessential clarification of an already named control. Use a disclosure or help button for information that touch users need to complete the task.

**Anatomy.** Anchor a small text bubble near its trigger. Give it enough contrast, width to wrap, and space from viewport edges.

**Variants and states.** Show on hover and keyboard focus, and hide on Escape or after focus and pointer leave. Keep it visible while the pointer travels onto the tooltip itself.

**Input and accessibility.** Keep focus on the trigger. Refer to the tooltip with `aria-describedby` and use `role="tooltip"` on the text. Keep controls outside the tooltip.

**Implementation.** Apply the tooltip class to the described text and wire visibility and dismissal to its trigger. The guide demonstrates Escape and focus handling.

```html
<div class="kozu-tip-wrap">
  <button class="kozu-button" type="button" aria-describedby="export-tip">Export</button>
  <span class="kozu-tooltip" id="export-tip" role="tooltip">Includes visible rows.</span>
</div>
```

**Pitfall.** Essential instructions inside a hover tooltip are unavailable on touch and easy to miss with assistive technology.

## Feedback

### Banner

**Choose.** Use an in-flow banner for persistent, relevant information that affects a page or section. Use a toast for a short confirmation of an action.

**Anatomy.** Include a distinctive mark, a concise state and explanation, and one relevant action when useful. Use an 8–16-unit internal gap with room to wrap.

**Variants and states.** Use information, attention, or recovery. Keep a blocking message visible until the condition changes. A dismissible banner needs a named dismissal and a stable focus destination.

**Input and accessibility.** Use normal reading order for initially present messages. For a new nonurgent banner, update a status region. Reserve an alert for an urgent condition that merits interruption.

**Implementation.** Render the visible message and the action as siblings. Pair color with wording.

```html
<aside class="kozu-banner" data-tone="notice" aria-labelledby="offline-title">
  <span aria-hidden="true">!</span>
  <div><strong id="offline-title">Connection lost</strong><p>Edits are saved on this device.</p></div>
</aside>
```

**Pitfall.** Marking every persistent banner as an alert can repeatedly interrupt assistive output.

### Toast

**Choose.** Use for a short confirmation or an update that remains available in context. Put required actions or recovery in a persistent banner or inline state.

**Anatomy.** Place the message within safe margins and keep it clear of the current focus or bottom controls. Keep the text brief and support wrapping.

**Variants and states.** Stack or replace repeated confirmations deliberately. Keep interactive versions available until dismissed or provide the same action in a persistent location.

**Input and accessibility.** Keep the live region mounted and update its text after the action. Use polite status for routine confirmations and keep focus on the user’s current task.

**Implementation.** Populate the existing region on demand. Align visual dismissal with the availability of any action.

```html
<div class="kozu-toast" role="status" aria-atomic="true"></div>
```

**Pitfall.** Creating a populated status region at the same moment as the event can leave the message unannounced.

### Progress indicator

**Choose.** Use determinate progress whenever the completed fraction is known. Use a spinner when the app cannot measure completion.

**Anatomy.** Place a compact label and exact value at equal outer insets with a wide central data mark. Use two rows of dots for task completion or a bar for a continuous ratio. Dots have a 4-unit diameter and 8-unit pitch on both axes. A width W under 4 units gets zero columns. Otherwise use `1 + floor((W - 4) / 8)` columns and center the remaining space. Reflow the data mark to its own row when labels or text scaling need more space.

**Variants and states.** Support starting, progressing, paused, complete, and failed. Show the exact percentage beside the representation. Light `floor(totalVisibleDots * percent / 100)` whole dots. Fill from the leading column to the trailing column and fill the top cell before the bottom cell in each column. At 0% every cell is dim. At 100% every cell is lit. Label financial progress with both the saved and target amounts.

**Input and accessibility.** Use a labelled native progress element or a named progressbar with an exact value. Keep its decorative duplicate out of the accessible tree and announce useful milestones separately.

**Implementation.** Load `dot-grid.js` with `defer`. Give the decorative grid an empty element and set `dataset.dotValue` from 0 to 100. Update the native progress value and visible label from the same number. The shared helper lays out complete columns on resize.

```html
<div class="kozu-progress">
  <div class="kozu-indicator-layout">
    <span id="sync-label">Sync</span>
    <div data-dot-grid="progress" data-dot-value="72" aria-hidden="true"></div>
    <span class="kozu-numeral" aria-hidden="true">72%</span>
  </div>
  <progress class="kozu-sr" aria-labelledby="sync-label" value="72" max="100">72%</progress>
</div>
```

**Pitfall.** A clipped or partly filled dot distorts the grid. Fill whole dots, keep the semantic and visible percentages exact, and let additional width add complete columns.

### Spinner

**Choose.** Use for an active task with unknown duration. If work is likely to continue for a while, explain what is happening and offer cancellation where feasible.

**Anatomy.** Pair a compact busy mark with visible state text. Keep its placement stable so the layout does not shift when work starts or finishes.

**Variants and states.** Use loading, complete, and error states with distinct text. Under reduced motion show a static mark with the same label. Replace the busy state with a result or actionable error.

**Input and accessibility.** Hide the decorative spinner from assistive technology. Use a polite status for a meaningful state transition and `aria-busy` on content being refreshed as needed.

**Implementation.** Update status when the work starts and ends. Avoid delaying an immediate result just to show a spinner.

```html
<p class="kozu-row" role="status">
  <span class="kozu-spinner" aria-hidden="true"></span>
  <span>Generating export…</span>
</p>
```

**Pitfall.** An unlabeled spinner can leave users unable to tell which task is running or whether it can stop.

### Listening indicator

**Choose.** Use while an audio or voice session is actually listening. Include the state and an immediately available Stop action.

**Anatomy.** Give the compact label and trailing action equal outer insets around a wide, flexible central data mark. Use three rows of dots by default and a seven-row dot waveform when the layout has room. Both add complete columns on an 8-unit pitch as space grows and preserve the 48-unit Stop target. Place the waveform on its own row when text size or width requires more room.

**Variants and states.** Support idle, listening, stopped, and unavailable. When motion is reduced, use a steady waveform. Keep the state visible. Update the session and indicator together when the user stops.

**Input and accessibility.** Treat the waveform as decorative and announce state changes through concise visible text. Use a native Stop button and return focus to the start control if Stop leaves the view.

**Implementation.** Load `dot-grid.js` with `defer`. Use `data-dot-grid="listening"` for three rows and `data-dot-grid="waveform"` for the wide treatment. Bind the state and motion to the audio session. Handle Stop in the app before reflecting its confirmed state.

```html
<div class="kozu-listening" data-listening="true">
  <div class="kozu-indicator-layout">
    <span role="status">Listening</span>
    <div data-dot-grid="listening" aria-hidden="true"></div>
    <button class="kozu-button" type="button">Stop</button>
  </div>
</div>
```

**Pitfall.** Keeping an animated indicator visible after the session ends misrepresents recording state. Changing only the horizontal pitch with width distorts the waveform.
