const all = (selector, root = document) => [...root.querySelectorAll(selector)];
const byId = (id) => document.getElementById(id);

const appearance = document.querySelector("[data-appearance]");
const systemDark = matchMedia("(prefers-color-scheme: dark)");
const appearanceName = () => (document.documentElement.dataset.theme || (systemDark.matches ? "dark" : "light"));
try {
  const preference = localStorage.getItem("kozu-guide-appearance");
  if (preference === "light" || preference === "dark") document.documentElement.dataset.theme = preference;
} catch {
  // The browser may disallow storage for local files.
}
function describeAppearance() {
  const isInk = appearanceName() === "dark";
  appearance.lastElementChild.textContent = isInk ? "Ink" : "Paper";
  appearance.querySelector("use").setAttribute("href", `#guide-icon-${isInk ? "moon" : "sun"}`);
  appearance.setAttribute("aria-label", isInk ? "Ink appearance. Switch to Paper." : "Paper appearance. Switch to Ink.");
}
describeAppearance();
systemDark.addEventListener("change", describeAppearance);
appearance.addEventListener("click", () => {
  const next = appearanceName() === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = next;
  try {
    localStorage.setItem("kozu-guide-appearance", next);
  } catch {
    // The current appearance works without storage.
  }
  describeAppearance();
});

const navLinks = all("[data-guide-nav]");
const guideGroups = all(".guide-group");
let currentGuideLocation;
function setGuideLocation(href) {
  if (currentGuideLocation === href) return;
  currentGuideLocation = href;
  for (const link of navLinks) {
    if (link.hash === href) link.setAttribute("aria-current", "location");
    else link.removeAttribute("aria-current");
  }
}
function guideLocation() {
  const section = byId(location.hash.slice(1))?.closest(".guide-group");
  setGuideLocation(section ? `#${section.id}` : "#overview");
}
guideLocation();
window.addEventListener("hashchange", guideLocation);

let navigationFrame;
window.addEventListener("scroll", () => {
  if (navigationFrame) return;
  navigationFrame = requestAnimationFrame(() => {
    navigationFrame = undefined;
    const active = guideGroups.findLast((group) => group.getBoundingClientRect().top < 148);
    setGuideLocation(active ? `#${active.id}` : "#overview");
  });
}, { passive: true });
document.querySelector(".guide-mobile-nav").addEventListener("click", (event) => {
  const link = event.target.closest("a");
  if (link) link.closest("details").open = false;
});

const searchTrigger = document.querySelector("[data-guide-search]");
const searchDialog = byId("guide-search");
const query = byId("guide-query");
const results = searchDialog.querySelector(".guide-search-results");
const resultStatus = searchDialog.querySelector(".guide-search-status");
const searchIndex = [
  ...all(".guide-entry").map((entry) => ({
    title: entry.querySelector("h3").textContent,
    href: `#${entry.id}`,
    group: entry.closest(".guide-group").querySelector("h2").textContent,
    keywords: entry.dataset.search,
  })),
  ...all(".guide-start-card, .guide-footer a[href='index.html'], .guide-footer a[href$='.json'], .guide-footer a[href$='.figcraft']").map((link) => ({
    title: link.querySelector("strong")?.textContent ?? link.textContent.trim(),
    href: link.getAttribute("href"),
    group: "Reference",
    keywords: link.querySelector("small")?.textContent ?? "",
  })),
];
function renderSearch() {
  const term = query.value.trim().toLowerCase();
  const words = term.split(/s+/).filter(Boolean);
  const matching = words.length
    ? searchIndex.filter(({ title, group, keywords }) =>
        words.every((word) => `${title} ${group} ${keywords}`.toLowerCase().includes(word)))
    : [];
  matching.sort((first, second) => {
    const rank = ({ title }) => (title.toLowerCase() === term ? 0 : title.toLowerCase().startsWith(term) ? 1 : 2);
    return rank(first) - rank(second);
  });
  results.replaceChildren(...matching.map(({ title, group, href }) => {
    const row = document.createElement("li");
    const link = document.createElement("a");
    const label = document.createElement("span");
    const family = document.createElement("small");
    link.href = href;
    label.textContent = title;
    family.textContent = group;
    link.append(label, family);
    row.append(link);
    return row;
  }));
  resultStatus.textContent = words.length
    ? (matching.length === 1 ? "1 result" : `${matching.length} results`)
    : "Search by component, material, or reference name.";
}
let searchReturn;
let searchDestination;
function openSearch() {
  if (searchDialog.open) return;
  searchReturn = document.activeElement;
  renderSearch();
  searchDialog.showModal();
  query.focus();
  query.select();
}
searchTrigger.addEventListener("click", openSearch);
query.addEventListener("input", renderSearch);
query.addEventListener("keydown", (event) => {
  if (event.isComposing) return;
  if (event.key === "Escape") {
    event.preventDefault();
    searchDialog.close();
    return;
  }
  const firstResult = results.querySelector("a");
  if (!firstResult) return;
  if (event.key === "Enter") {
    event.preventDefault();
    firstResult.click();
  }
  if (event.key === "ArrowDown") {
    event.preventDefault();
    firstResult.focus();
  }
});
results.addEventListener("keydown", (event) => {
  const links = all("a", results);
  const index = links.indexOf(document.activeElement);
  if (index < 0) return;
  if (event.key === "ArrowDown") {
    event.preventDefault();
    links[Math.min(index + 1, links.length - 1)].focus();
  }
  if (event.key === "ArrowUp") {
    event.preventDefault();
    (links[index - 1] || query).focus();
  }
});
results.addEventListener("click", (event) => {
  const link = event.target.closest("a");
  if (!link || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
  searchDestination = link.hash && byId(link.hash.slice(1));
  searchDialog.close();
});
searchDialog.addEventListener("close", () => {
  if (searchDestination) {
    searchDestination.focus({ preventScroll: true });
    searchDestination.scrollIntoView({ block: "start" });
  } else {
    (searchReturn?.matches("body") ? searchTrigger : searchReturn)?.focus();
  }
  searchDestination = null;
});
document.addEventListener("keydown", (event) => {
  if (event.defaultPrevented || event.isComposing || document.querySelector("dialog[open]")) return;
  const editable = event.target.closest?.("input, textarea, select, [contenteditable]");
  const slash = event.key === "/" && !event.metaKey && !event.ctrlKey && !event.altKey && !editable;
  const shortcut = event.key.toLowerCase() === "k" && (event.metaKey || event.ctrlKey) && !event.altKey;
  if (!slash && !shortcut) return;
  event.preventDefault();
  openSearch();
});

const swatches = all(".guide-swatch");
const readout = document.querySelector(".guide-swatch-readout");
const palette = document.querySelector(".guide-ramp-region");
for (const swatch of swatches) {
  swatch.tabIndex = swatch.getAttribute("aria-pressed") === "true" ? 0 : -1;
}
function focusSwatch(swatch) {
  for (const item of swatches) item.tabIndex = item === swatch ? 0 : -1;
  swatch.focus();
}
palette.addEventListener("click", (event) => {
  const swatch = event.target.closest(".guide-swatch");
  if (!swatch) return;
  const key = swatch.dataset.swatch;
  const value = getComputedStyle(swatch).getPropertyValue(key).trim().toUpperCase();
  const label = `${swatch.closest("tr").querySelector("th").textContent} ${swatch.textContent.trim()}`;
  for (const item of swatches) item.setAttribute("aria-pressed", String(item === swatch));
  focusSwatch(swatch);
  readout.firstElementChild.style.setProperty("--swatch", `var(${key})`);
  readout.querySelector("strong").textContent = label;
  readout.querySelector("code").textContent = key;
  readout.lastElementChild.textContent = value;
});
palette.addEventListener("keydown", (event) => {
  const button = event.target.closest(".guide-swatch");
  if (!button) return;
  const index = swatches.indexOf(button);
  const columns = button.closest("tr").cells.length - 1;
  const firstInRow = index - (index % columns);
  const rtl = getComputedStyle(palette).direction === "rtl";
  const next = {
    ArrowDown: index + columns, ArrowUp: index - columns,
    ArrowLeft: index + (rtl ? 1 : -1), ArrowRight: index + (rtl ? -1 : 1),
    Home: firstInRow, End: firstInRow + columns - 1,
  }[event.key];
  if (next === undefined) return;
  event.preventDefault();
  if (swatches[next]) focusSwatch(swatches[next]);
});

function report(target, message) {
  target.closest(".guide-stage").querySelector(".guide-output").textContent = message;
}
for (const button of all("[data-report]")) {
  button.addEventListener("click", () => report(button, button.dataset.report));
}
for (const button of all("[data-toggle], [data-filter]")) {
  button.addEventListener("click", () => {
    const active = button.getAttribute("aria-pressed") !== "true";
    button.setAttribute("aria-pressed", String(active));
    if (button.hasAttribute("data-filter")) {
      const count = all('[data-filter][aria-pressed="true"]', button.closest(".guide-stage")).length;
      report(button, `${count} ${count === 1 ? "filter" : "filters"} active.`);
    } else {
      report(button, button.dataset.toggle.split("|")[active ? 0 : 1]);
    }
  });
}

const localSearch = document.querySelector("[data-local-search]");
localSearch.addEventListener("input", () => {
  const term = localSearch.value.trim().toLowerCase();
  const rows = all(".kozu-list-row", localSearch.parentElement);
  for (const row of rows) row.hidden = !row.textContent.toLowerCase().includes(term);
  const total = rows.filter((row) => !row.hidden).length;
  report(localSearch, `${total} ${total === 1 ? "project" : "projects"}`);
});

const choices = document.querySelector("[data-check-group]");
const selectAll = choices.querySelector("[data-check-all]");
const members = all("input:not([data-check-all])", choices);
function syncCheckGroup() {
  selectAll.checked = members.every((input) => input.checked);
  selectAll.indeterminate = !selectAll.checked && members.some((input) => input.checked);
}
syncCheckGroup();
choices.addEventListener("change", (event) => {
  if (event.target === selectAll) {
    for (const member of members) member.checked = selectAll.checked;
  }
  syncCheckGroup();
});
const weekly = document.querySelector("[data-switch]");
weekly.addEventListener("change", () => report(weekly, `Weekly reminders ${weekly.checked ? "on" : "off"}.`));
const range = document.querySelector("[data-range]");
range.addEventListener("input", () => { range.nextElementSibling.textContent = `${range.value}%`; });

for (const tablist of all('[role="tablist"]')) {
  const tabs = all('[role="tab"]', tablist);
  function activate(tab) {
    for (const item of tabs) {
      const selected = item === tab;
      item.setAttribute("aria-selected", String(selected));
      item.tabIndex = selected ? 0 : -1;
      byId(item.getAttribute("aria-controls")).hidden = !selected;
    }
  }
  tablist.addEventListener("click", (event) => {
    const tab = event.target.closest('[role="tab"]');
    if (tab) activate(tab);
  });
  tablist.addEventListener("keydown", (event) => {
    const index = tabs.indexOf(event.target);
    if (index < 0) return;
    const rtl = getComputedStyle(tablist).direction === "rtl";
    const steps = {
      ArrowLeft: index + (rtl ? 1 : -1), ArrowRight: index + (rtl ? -1 : 1),
      Home: 0, End: tabs.length - 1,
    };
    if (!Object.hasOwn(steps, event.key)) return;
    event.preventDefault();
    const tab = tabs[(steps[event.key] + tabs.length) % tabs.length];
    activate(tab);
    tab.focus();
  });
}

for (const nav of all("[data-demo-nav], [data-demo-breadcrumb]")) {
  const links = all("a", nav);
  nav.addEventListener("click", (event) => {
    const link = event.target.closest("a");
    if (!link || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    for (const item of links) {
      if (!nav.hasAttribute("data-demo-breadcrumb")) {
        if (item === link) item.setAttribute("aria-current", "location");
        else item.removeAttribute("aria-current");
      }
      byId(item.hash.slice(1)).hidden = item !== link;
    }
    if (nav.hasAttribute("data-demo-breadcrumb")) {
      report(nav, `${link.textContent.trim()} opened.`);
    } else {
      byId(link.hash.slice(1)).focus();
    }
  });
}

const pages = document.querySelector("[data-pages]");
const pageRows = ["Studio, Archive, Review", "Roadmap, Delivery, Research", "Ledger, Metrics, Toolkit"];
let currentPage = 1;
pages.addEventListener("click", (event) => {
  const button = event.target.closest("[data-page]");
  if (!button) return;
  const pressed = button.dataset.page;
  currentPage = pressed === "prev" ? currentPage - 1 : pressed === "next" ? currentPage + 1 : Number(pressed);
  const activePage = pages.querySelector(`[data-page="${currentPage}"]`);
  for (const item of all("button", pages)) {
    if (item === activePage) item.setAttribute("aria-current", "page");
    else item.removeAttribute("aria-current");
  }
  pages.firstElementChild.disabled = currentPage === 1;
  pages.lastElementChild.disabled = currentPage === pageRows.length;
  if (button.disabled) activePage.focus();
  report(pages, `Showing projects ${currentPage * 3 - 2}–${currentPage * 3} of 9 · ${pageRows[currentPage - 1]}`);
});

const sort = document.querySelector("[data-sort]");
sort.addEventListener("click", () => {
  const heading = sort.closest("th");
  const rows = sort.closest("table").tBodies[0];
  const descending = heading.getAttribute("aria-sort") === "ascending";
  heading.setAttribute("aria-sort", descending ? "descending" : "ascending");
  sort.lastElementChild.textContent = descending ? "↓" : "↑";
  rows.append(...all("tr", rows).sort((a, b) => (Number(a.dataset.amount) - Number(b.dataset.amount)) * (descending ? -1 : 1)));
});

for (const mark of all(".kozu-needle")) {
  mark.addEventListener("click", () => {
    for (const item of all(".kozu-needle", mark.parentElement)) item.setAttribute("aria-pressed", String(item === mark));
    mark.closest("figure").querySelector("[data-chart-value]").textContent = mark.dataset.value;
  });
}

for (const trigger of all("[data-dialog]")) {
  const dialog = byId(trigger.dataset.dialog);
  trigger.addEventListener("click", () => {
    dialog.returnValue = "";
    dialog.showModal();
  });
  dialog.addEventListener("close", () => {
    const responses = { archive: "Report archived.", export: "Export prepared." };
    report(trigger, responses[dialog.returnValue] || "No changes made.");
    trigger.focus();
  });
}
const menu = byId("sample-menu");
menu.addEventListener("click", (event) => {
  const button = event.target.closest("[data-menu-action]");
  if (!button) return;
  menu.hidePopover();
  report(menu, button.dataset.menuAction);
  menu.previousElementSibling.focus();
});
const tooltip = document.querySelector(".kozu-tip-wrap");
function resetTooltipDismissal() {
  requestAnimationFrame(() => {
    if (!tooltip.matches(":hover, :focus-within")) delete tooltip.dataset.dismissed;
  });
}
tooltip.addEventListener("pointerleave", resetTooltipDismissal);
tooltip.addEventListener("focusout", resetTooltipDismissal);
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && tooltip.matches(":hover, :focus-within")) tooltip.dataset.dismissed = "";
});

const toastButton = document.querySelector("[data-toast]");
const toast = toastButton.parentElement.querySelector(".kozu-toast");
let toastTimer;
toastButton.addEventListener("click", () => {
  clearTimeout(toastTimer);
  toast.textContent = "Draft saved.";
  toastTimer = setTimeout(() => { toast.textContent = ""; }, 5000);
});

const progressInput = document.querySelector("[data-progress]");
const progress = progressInput.closest(".guide-stage").querySelector(".kozu-progress");
progressInput.addEventListener("input", () => {
  const value = Number(progressInput.value);
  const label = `${value}%`;
  progress.querySelector("progress").value = value;
  progress.querySelector("[data-progress-text]").textContent = label;
  progress.querySelector("[data-dot-grid]").dataset.dotValue = String(value);
});

const spinnerButton = document.querySelector("[data-spinner]");
spinnerButton.addEventListener("click", () => {
  const stage = spinnerButton.closest(".guide-stage");
  const spinner = stage.querySelector(".kozu-spinner");
  const status = stage.querySelector("[data-spinner-status]");
  if (spinnerButton.getAttribute("aria-disabled") === "true") return;
  spinnerButton.setAttribute("aria-disabled", "true");
  spinner.hidden = false;
  status.textContent = "Preparing preview…";
  setTimeout(() => {
    status.textContent = "Preview ready.";
    spinner.hidden = true;
    spinnerButton.removeAttribute("aria-disabled");
  }, 1800);
});

const listening = document.querySelector(".kozu-listening");
const listen = listening.querySelector("[data-listen]");
listen.addEventListener("click", () => {
  const active = listening.dataset.listening !== "true";
  listening.dataset.listening = String(active);
  listen.textContent = active ? "Stop" : "Start";
  listening.querySelector('[role="status"]').textContent = active ? "Listening" : "Stopped";
});

const waveMode = document.querySelector("[data-wave-mode]");
waveMode.addEventListener("click", () => {
  const isWide = waveMode.getAttribute("aria-pressed") !== "true";
  listening.querySelector("[data-dot-grid]").dataset.dotGrid = isWide ? "waveform" : "listening";
  waveMode.setAttribute("aria-pressed", String(isWide));
});
