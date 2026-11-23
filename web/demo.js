"use strict";

const byId = (id) => document.getElementById(id);
const money = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD" });

function wireTabs(tablist, activate) {
  const tabs = Array.from(tablist.querySelectorAll('[role="tab"]'));

  for (const [index, tab] of tabs.entries()) {
    tab.addEventListener("click", () => {
      for (const candidate of tabs) {
        const selected = candidate === tab;
        candidate.setAttribute("aria-selected", String(selected));
        candidate.tabIndex = selected ? 0 : -1;
      }
      activate(tab);
    });
    tab.addEventListener("keydown", (event) => {
      const last = tabs.length - 1;
      const destinations = {
        ArrowLeft: (index + last) % tabs.length,
        ArrowRight: (index + 1) % tabs.length,
        Home: 0,
        End: last,
      };
      if (tablist.getAttribute("aria-orientation") === "vertical") {
        destinations.ArrowUp = destinations.ArrowLeft;
        destinations.ArrowDown = destinations.ArrowRight;
      }
      const destination = destinations[event.key];
      if (!Number.isInteger(destination)) return;
      event.preventDefault();
      tabs[destination].focus();
      tabs[destination].click();
    });
  }
}

function wirePanels(tablist) {
  const panels = Array.from(tablist.querySelectorAll('[role="tab"]'), (tab) => byId(tab.getAttribute("aria-controls")));
  wireTabs(tablist, (tab) => {
    const active = byId(tab.getAttribute("aria-controls"));
    for (const panel of panels) panel.hidden = panel !== active;
  });
}

const workspaceTabs = document.querySelector(".workspace-tabs");
const tabletRail = matchMedia("(600px <= width < 1024px)");
function setTabOrientation() {
  workspaceTabs.setAttribute("aria-orientation", tabletRail.matches ? "vertical" : "horizontal");
}
tabletRail.addEventListener("change", setTabOrientation);
setTabOrientation();

wirePanels(workspaceTabs);
wirePanels(document.querySelector(".accounts-dock"));

const ledgerToggle = byId("ledger-toggle");
const olderTransactions = byId("older-transactions");
ledgerToggle.addEventListener("click", () => {
  olderTransactions.hidden = !olderTransactions.hidden;
  ledgerToggle.setAttribute("aria-expanded", String(!olderTransactions.hidden));
  ledgerToggle.textContent = olderTransactions.hidden ? "Show all" : "Show less";
});

const periods = {
  week: {
    caption: "Nov 16–22, 2026", basis: "day",
    groups: [
      [16, 16, "Mon"], [17, 17, "Tue"], [18, 18, "Wed"], [19, 19, "Thu"],
      [20, 20, "Fri"], [21, 21, "Sat"], [22, 22, "Sun"],
    ],
  },
  month: {
    caption: "Nov 1–22, 2026", basis: "week",
    groups: [[1, 7, "1–7"], [8, 14, "8–14"], [15, 21, "15–21"], [22, 22, "22"]],
  },
};
const spending = new Map();
for (const row of document.querySelectorAll("[data-spend]")) {
  const day = Number(row.dataset.day.slice(-2));
  const cents = Math.round(Number(row.dataset.spend) * 100);
  spending.set(day, (spending.get(day) ?? 0) + cents);
}
const periodButtons = document.querySelectorAll("[data-period]");

function showSpending(period) {
  const { caption, basis, groups } = periods[period];
  const values = groups.map(([firstDay, lastDay]) => {
    let total = 0;
    for (let day = firstDay; day <= lastDay; day += 1) total += spending.get(day) ?? 0;
    return total;
  });
  const max = Math.max(1, ...values);
  const chart = byId("spending-chart");

  for (const button of periodButtons) {
    button.setAttribute("aria-pressed", String(button.dataset.period === period));
  }
  byId("spending-total").textContent = money.format(values.reduce((sum, value) => sum + value, 0) / 100);
  byId("spending-date").textContent = caption;
  byId("spending-selection").textContent = "Nov " + groups.at(-1)[1] + " · " + money.format(values.at(-1) / 100);
  chart.setAttribute("aria-label", "Spending by " + basis);
  chart.replaceChildren(...groups.map(([, , label], index) => {
    const item = document.createElement("li");
    const bar = document.createElement("span");
    const barLabel = document.createElement("span");
    const amount = document.createElement("span");
    bar.className = "chart-bar";
    bar.style.setProperty("--bar-height", (values[index] / max * 100) + "%");
    bar.setAttribute("aria-hidden", "true");
    barLabel.textContent = label;
    amount.className = "kozu-sr";
    amount.textContent = " " + money.format(values[index] / 100);
    item.title = label + " · " + money.format(values[index] / 100);
    item.append(bar, barLabel, amount);
    return item;
  }));
}

for (const button of periodButtons) button.addEventListener("click", () => showSpending(button.dataset.period));
showSpending("week");

const transfer = byId("transfer-dialog");
const transferForm = byId("transfer-form");
const recipientInput = transferForm.elements.namedItem("recipient");
const amountInput = transferForm.elements.namedItem("amount");

for (const button of document.querySelectorAll("[data-transfer]")) {
  button.addEventListener("click", () => {
    transferForm.reset();
    recipientInput.setCustomValidity("");
    transfer.dataset.mode = button.dataset.transfer;
    const payment = transfer.dataset.mode === "pay";
    byId("transfer-title").textContent = payment ? "Pay" : "Request";
    byId("transfer-submit").textContent = payment ? "Preview payment" : "Preview request";
    if (payment) amountInput.max = "117450.17";
    else amountInput.removeAttribute("max");
    transfer.showModal();
  });
}
recipientInput.addEventListener("input", () => recipientInput.setCustomValidity(""));
byId("transfer-close").addEventListener("click", () => transfer.close());
transferForm.addEventListener("submit", (event) => {
  event.preventDefault();
  const recipient = recipientInput.value.trim();
  if (!recipient) {
    recipientInput.setCustomValidity("Enter a person or business.");
    recipientInput.reportValidity();
    return;
  }

  const payment = transfer.dataset.mode === "pay";
  const amount = money.format(amountInput.valueAsNumber);
  const action = payment ? amount + " payment to " : amount + " request from ";
  byId("transfer-result").textContent = action + recipient + " (preview).";
  transfer.close();
});

const agents = Array.from(document.querySelectorAll(".agent"));
function renderAgent(agent) {
  const percent = Number(agent.dataset.progress);
  const paused = agent.dataset.paused === "true";
  const complete = percent === 100;
  const state = complete ? "Complete" : paused ? "Paused" : "In progress";

  agent.querySelector(".agent-percent").textContent = percent + "%";
  agent.querySelector(".agent-meter").dataset.dotValue = String(percent);
  agent.querySelector(".agent-state").textContent = state;

  const inlineState = agent.querySelector(".agent-inline-state");
  inlineState.textContent = state;
  inlineState.hidden = state === "In progress";

  const pause = agent.querySelector('[data-agent-action="pause"]');
  const advance = agent.querySelector('[data-agent-action="advance"]');
  pause.textContent = paused ? "Resume" : "Pause";
  advance.textContent = percent >= 90 ? "Finish" : "+10 points";
  pause.disabled = complete;
  advance.disabled = complete || paused;

  const tasks = Array.from(agent.querySelectorAll(".agent-tasks li"));
  const completed = Math.floor(percent / 100 * tasks.length);
  for (const [index, task] of tasks.entries()) {
    const done = index < completed;
    const active = index === completed;
    const status = done ? "Done" : active ? (paused ? "Paused" : "In progress") : "Queued";
    task.firstElementChild.classList.toggle("complete", done);
    task.firstElementChild.classList.toggle("working", active && !paused);
    task.lastElementChild.textContent = status;
  }
  const inProgress = agents.filter((item) => item.dataset.paused !== "true" && item.dataset.progress !== "100").length;
  byId("agent-count").textContent = inProgress + " in progress";
  return state;
}

for (const agent of agents) {
  const inlineState = document.createElement("span");
  inlineState.className = "agent-inline-state";
  agent.querySelector(".agent-caption").append(inlineState);
  renderAgent(agent);

  for (const button of agent.querySelectorAll("[data-agent-action]")) {
    button.addEventListener("click", () => {
      if (button.dataset.agentAction === "pause") agent.dataset.paused = String(agent.dataset.paused !== "true");
      else agent.dataset.progress = String(Math.min(100, Number(agent.dataset.progress) + 10));
      const state = renderAgent(agent);
      const name = agent.querySelector(".agent-identity strong").textContent;
      byId("agent-announcement").textContent = name + ". " + agent.dataset.progress + "% complete. " + state + ".";
      if (button.disabled) agent.querySelector("summary").focus();
    });
  }
}

const taskInput = byId("task-input");
const listen = byId("listen");
const listeningIndicator = document.querySelector(".listening-indicator");

byId("new-task").addEventListener("click", () => taskInput.focus());
taskInput.addEventListener("input", () => taskInput.setCustomValidity(""));
listen.addEventListener("click", () => {
  const start = listeningIndicator.hidden;
  listeningIndicator.hidden = !start;
  byId("listen-label").textContent = start ? "Stop" : "Listen";
  listen.setAttribute("aria-label", start ? "Stop listening" : "Listen");
  byId("listen-status").textContent = start ? "Listening demo started." : "Listening demo stopped.";
  if (!start && !taskInput.value.trim()) {
    taskInput.setCustomValidity("");
    taskInput.value = "Gather the documents for my upcoming meetings and prepare a briefing for each.";
  }
});

byId("task-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const description = taskInput.value.trim();
  if (!description) {
    taskInput.setCustomValidity("Enter a task description.");
    taskInput.reportValidity();
    return;
  }

  const task = document.createElement("li");
  const marker = document.createElement("span");
  const text = document.createElement("span");
  marker.className = "dot";
  marker.setAttribute("aria-hidden", "true");
  text.textContent = description;
  task.append(marker, text);
  const list = byId("queued-tasks");
  list.prepend(task);
  list.hidden = false;
  byId("listen-status").textContent = "Task queued. " + description;
  taskInput.value = "";
});

const incidents = {
  eu: {
    id: "INC-3318", title: "Checkout latency spike", services: 214, resolved: "6 min",
    summary: "Checkout slowed after a deploy in Frankfurt. Rolling back the deploy restored service.",
    label: "checkout.p95 · 30 min", result: "2.41 s → 180 ms",
    report: "A slow database pool followed deploy #4182. Rolling back #4182 restored checkout p95 to 180 ms. No one was paged.",
    log: [
      ["02:14:03", "alert", "checkout.p95 at 2.41 s (target 400 ms)"],
      ["02:14:19", "trace", "Database pool saturated. 212 requests waiting."],
      ["02:14:20", "plan", "Roll back deploy #4182 in Frankfurt."],
      ["02:16:47", "apply", "Rollback complete. Checking checkout."],
      ["02:20:11", "fixed", "p95 180 ms. Incident closed."],
    ],
    values: [10, 8, 12, 9, 6, 11, 9, 13, 14, 20, 64, 87, 100, 92, 76, 46, 26, 20, 19, 18, 22, 16, 14, 13, 11, 18, 9, 14, 12, 17, 15, 13],
    peak: [10, 16], after: 23,
  },
  us: {
    id: "INC-3321", title: "Queue backlog", services: 196, resolved: "8 min",
    summary: "Email delivery queued in Virginia until two workers came back online.",
    label: "mail.queue · 30 min", result: "1,284 → 12 jobs",
    report: "Two mail workers failed their health checks. Replacing both workers drained the queue to 12 jobs. No one was paged.",
    log: [
      ["04:31:09", "alert", "Mail queue grew to 1,284 jobs."],
      ["04:31:33", "trace", "Two workers are failing health checks."],
      ["04:32:00", "plan", "Replace workers in Virginia."],
      ["04:35:18", "apply", "New workers are draining the queue."],
      ["04:39:22", "fixed", "Queue at 12 jobs. Incident closed."],
    ],
    values: [7, 6, 10, 8, 16, 19, 23, 28, 37, 50, 59, 68, 82, 94, 100, 94, 76, 67, 55, 42, 32, 19, 17, 13, 12, 9, 8, 7, 10, 12, 11, 7],
    peak: [9, 18], after: 23,
  },
  stage: {
    id: "INC-3324", title: "API error rate", services: 84, resolved: "5 min",
    summary: "A staging-only config change blocked API requests until the previous configuration was restored.",
    label: "api.errors · 30 min", result: "8.4% → 0.1%",
    report: "Restoring the previous staging configuration brought the error rate to 0.1%. Production was unaffected.",
    log: [
      ["06:05:12", "alert", "API error rate reached 8.4%."],
      ["06:05:24", "trace", "Errors begin after a staging config change."],
      ["06:06:03", "plan", "Restore the previous API configuration."],
      ["06:08:45", "apply", "Config restored. Monitoring errors."],
      ["06:10:18", "fixed", "Errors at 0.1%. Incident closed."],
    ],
    values: [4, 6, 8, 5, 7, 5, 8, 7, 10, 23, 29, 36, 88, 100, 80, 95, 85, 40, 32, 28, 16, 14, 9, 12, 7, 10, 5, 9, 7, 9, 4, 5],
    peak: [11, 18], after: 23,
  },
};

const replay = byId("replay-step");
const report = byId("incident-report");
const reportToggle = byId("report-toggle");
let currentEnvironment = "eu";

function renderReplay() {
  const incident = incidents[currentEnvironment];
  const step = Number(replay.value);
  const eventMax = incident.log.length;
  const samplesSeen = Math.ceil(incident.values.length * step / eventMax);

  const statusIcons = { alert: "alert", trace: "search", fixed: "check" };
  byId("run-log").replaceChildren(...incident.log.slice(0, step).map(([timestamp, kind, message]) => {
    const row = document.createElement("li");
    const time = document.createElement("time");
    const type = document.createElement("span");
    const detail = document.createElement("span");
    time.dateTime = "2026-11-22T" + timestamp + "Z";
    time.textContent = timestamp;
    type.className = "log-kind log-" + kind;
    if (statusIcons[kind]) {
      const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      const use = document.createElementNS(svg.namespaceURI, "use");
      svg.setAttribute("class", "kozu-icon");
      svg.setAttribute("aria-hidden", "true");
      use.setAttribute("href", "#icon-" + statusIcons[kind]);
      svg.append(use);
      type.append(svg);
    }
    type.append(kind);
    detail.textContent = message;
    row.append(time, type, detail);
    return row;
  }));

  const bars = incident.values.map((height, index) => {
    const bar = document.createElement("i");
    bar.style.setProperty("--bar-height", height + "%");
    bar.classList.toggle("is-peak", index >= incident.peak[0] && index < incident.peak[1]);
    bar.classList.toggle("is-after", index >= incident.after);
    bar.classList.toggle("is-future", index >= samplesSeen);
    return bar;
  });
  byId("terminal-bars").replaceChildren(...bars);
  byId("terminal-chart-value").textContent = step === eventMax ? incident.result : "Through " + incident.log[step - 1][0];
  byId("replay-count").value = step + " / " + eventMax;
  replay.setAttribute("aria-valuetext", "Event " + step + " of " + eventMax);
}

function showIncident(environment) {
  currentEnvironment = environment;
  const incident = incidents[environment];
  byId("terminal-scope").textContent = incident.services + " services";
  byId("incident-id").textContent = incident.id;
  byId("incident-heading").textContent = incident.title;
  byId("time-to-fix").textContent = incident.resolved;
  byId("incident-summary").textContent = incident.summary;
  byId("report-copy").textContent = incident.report;
  byId("terminal-chart-label").textContent = incident.label;
  replay.max = incident.log.length;
  replay.value = replay.max;
  renderReplay();
}

wireTabs(document.querySelector(".terminal-tabs"), (tab) => {
  byId("incident-view").setAttribute("aria-labelledby", tab.id);
  showIncident(tab.dataset.env);
});
replay.addEventListener("input", renderReplay);
reportToggle.addEventListener("click", () => {
  report.hidden = !report.hidden;
  reportToggle.setAttribute("aria-expanded", String(!report.hidden));
  reportToggle.lastElementChild.textContent = report.hidden ? "View report" : "Hide report";
});
showIncident(currentEnvironment);
