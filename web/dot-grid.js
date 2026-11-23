"use strict";

(() => {
  const diameter = 4;
  const pitch = 8;
  const modes = new Map([["progress", 2], ["listening", 3], ["waveform", 7]]);
  const selector = "[data-dot-grid]";
  const grids = new WeakMap();

  function render(grid, state) {
    const mode = grid.dataset.dotGrid;
    const rows = modes.get(mode);
    const columns = Math.max(0, 1 + Math.floor((state.width - diameter) / pitch));

    if (mode !== state.mode || columns !== state.columns) {
      const dots = document.createDocumentFragment();
      for (let index = 0; index < rows * columns; index += 1) {
        const dot = document.createElement("span");
        dot.className = "kozu-dot";
        if (mode !== "progress") {
          const row = Math.floor(index / columns);
          const column = index % columns;
          let active = row === 1;
          if (mode === "waveform") {
            const position = (column + 0.5) / columns;
            const pulse = 0.65 + 0.35 * Math.cos(6 * Math.PI * position);
            const radius = Math.round(3 * Math.sin(Math.PI * position) * pulse);
            active = Math.abs(row - 3) <= radius;
          }
          dot.toggleAttribute("data-dot-on", active);
          dot.style.animationDelay = -((row * 2 + column) % 7) * 0.13 + "s";
        }
        dots.append(dot);
      }
      grid.style.setProperty("--kozu-dot-tracks", columns ? `repeat(${columns}, ${diameter}px)` : "none");
      grid.replaceChildren(dots);
      state.mode = mode;
      state.columns = columns;
    }

    if (mode === "progress") {
      const value = Math.max(0, Math.min(100, Number(grid.dataset.dotValue) || 0));
      const filled = Math.floor(rows * columns * value / 100);
      for (const [index, dot] of Array.from(grid.children).entries()) {
        const row = Math.floor(index / columns);
        const column = index % columns;
        dot.toggleAttribute("data-dot-on", column * rows + row < filled);
      }
    }
  }

  const resize = new ResizeObserver((entries) => {
    for (const entry of entries) {
      const state = grids.get(entry.target);
      if (!state) continue;
      state.width = entry.contentBoxSize?.[0]?.inlineSize ?? entry.contentRect.width;
      render(entry.target, state);
    }
  });

  function observe(grid) {
    if (!modes.has(grid.dataset.dotGrid) || grids.has(grid)) return;
    grids.set(grid, { width: 0 });
    resize.observe(grid);
  }

  function forget(grid) {
    if (!grids.delete(grid)) return;
    resize.unobserve(grid);
  }

  function visit(node, callback) {
    if (!(node instanceof Element)) return;
    if (node.matches(selector)) callback(node);
    if (node.childElementCount) node.querySelectorAll(selector).forEach(callback);
  }

  document.querySelectorAll(selector).forEach(observe);
  new MutationObserver((records) => {
    for (const record of records) {
      if (record.type === "attributes") {
        const grid = record.target;
        if (!modes.has(grid.dataset.dotGrid)) {
          if (!grids.has(grid)) continue;
          forget(grid);
          grid.replaceChildren();
          grid.style.removeProperty("--kozu-dot-tracks");
          continue;
        }
        observe(grid);
        render(grid, grids.get(grid));
      } else {
        for (const node of record.addedNodes) visit(node, observe);
        for (const node of record.removedNodes) visit(node, (grid) => {
          if (!grid.isConnected) forget(grid);
        });
      }
    }
  }).observe(document.documentElement, {
    subtree: true,
    childList: true,
    attributes: true,
    attributeFilter: ["data-dot-grid", "data-dot-value"],
  });
})();
