import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { mkdtemp, readFile, rm, writeFile } from "node:fs/promises";
import { join, resolve } from "node:path";
import { setTimeout } from "node:timers/promises";

const scratch = process.argv[2];
assert(scratch, "Pass an existing task scratch directory outside cloud sync.");
const capture = process.argv.includes("--capture");
const profile = await mkdtemp(join(resolve(scratch), "kozu-chrome-"));
const chrome = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const browser = spawn(chrome, [
  "--headless", "--disable-background-networking", "--disable-component-update", "--disable-sync",
  "--no-default-browser-check", "--no-first-run", "--remote-debugging-port=0",
  "--user-data-dir=" + profile, "about:blank",
], { stdio: "ignore" });
let socket;
const stopped = new Promise((done) => {
  browser.once("close", done);
  browser.once("error", done);
});

try {
  let port;
  for (let attempt = 0; !port && attempt < 80; attempt += 1) {
    try {
      [port] = (await readFile(join(profile, "DevToolsActivePort"), "utf8")).split("\n");
    } catch (error) {
      if (error.code !== "ENOENT") throw error;
      await setTimeout(125);
    }
  }
  assert(port, "Chrome did not expose a local debugger port. Check CHROME and the browser profile path.");
  const targets = await fetch("http://127.0.0.1:" + port + "/json/list").then((response) => response.json());
  socket = new WebSocket(targets.find((target) => target.type === "page").webSocketDebuggerUrl);
  await new Promise((done, fail) => {
    socket.addEventListener("open", done, { once: true });
    socket.addEventListener("error", fail, { once: true });
  });

  let commandId = 0;
  const pending = new Map();
  const requests = [];
  socket.addEventListener("message", ({ data }) => {
    const message = JSON.parse(data);
    if (message.method === "Network.requestWillBeSent") requests.push(message.params.request.url);
    const callback = pending.get(message.id);
    if (!callback) return;
    pending.delete(message.id);
    callback(message);
  });

  const send = (method, params = {}) => new Promise((done, fail) => {
    const id = ++commandId;
    pending.set(id, (message) => {
      if (message.error) fail(new Error(JSON.stringify(message.error)));
      else done(message.result);
    });
    socket.send(JSON.stringify({ id, method, params }));
  });
  const read = async (expression) => {
    const result = await send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
    if (result.exceptionDetails) throw new Error(result.exceptionDetails.exception.description);
    return result.result.value;
  };
  const press = async (key, virtualKey) => {
    const fields = { key, code: key, windowsVirtualKeyCode: virtualKey };
    await send("Input.dispatchKeyEvent", { ...fields, type: "rawKeyDown" });
    await send("Input.dispatchKeyEvent", { ...fields, type: "keyUp" });
  };
  let touch = false;
  const clickAt = async (selector) => {
    const [x, y] = await read(`(() => {
      const rect = $(${JSON.stringify(selector)}).getBoundingClientRect();
      return [rect.x + rect.width / 2, rect.y + rect.height / 2];
    })()`);
    if (touch) {
      await send("Input.dispatchTouchEvent", { type: "touchStart", touchPoints: [{ x, y }] });
      await send("Input.dispatchTouchEvent", { type: "touchEnd", touchPoints: [] });
      return;
    }
    await send("Input.dispatchMouseEvent", { type: "mousePressed", x, y, button: "left", clickCount: 1 });
    await send("Input.dispatchMouseEvent", { type: "mouseReleased", x, y, button: "left", clickCount: 1 });
  };
  const viewport = async (width, height, mobile = false) => {
    touch = mobile;
    await send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile });
    await send("Emulation.setTouchEmulationEnabled", { enabled: mobile });
  };
  const shot = async (name) => {
    if (!capture) return;
    const { data } = await send("Page.captureScreenshot", { format: "png" });
    await writeFile(join(scratch, name + ".png"), Buffer.from(data, "base64"));
  };

  const assertDotGrid = async (selector, rows, value) => {
    const geometry = await read(`new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(() => {
      const grid = document.querySelector(${JSON.stringify(selector)});
      const outer = grid.getBoundingClientRect();
      const style = getComputedStyle(grid);
      const scale = grid.currentCSSZoom;
      const inset = side => parseFloat(style['padding' + side]) + parseFloat(style['border' + side + 'Width']);
      const left = inset('Left'), right = inset('Right'), top = inset('Top'), bottom = inset('Bottom');
      const dots = [...grid.children].map(dot => {
        const rect = dot.getBoundingClientRect();
        return {
          x: (rect.x + rect.width / 2 - outer.x) / scale - left,
          y: (rect.y + rect.height / 2 - outer.y) / scale - top,
          width: rect.width / scale, height: rect.height / scale,
          on: dot.hasAttribute('data-dot-on'),
          mask: getComputedStyle(dot).maskImage,
        };
      });
      resolve({ width: outer.width / scale - left - right, height: outer.height / scale - top - bottom, rtl: style.direction === "rtl", dots });
    })))`);
    const { width, height, rtl, dots } = geometry;
    const columns = Math.max(0, 1 + Math.floor((width - 4) / 8));
    assert.equal(dots.length, columns * rows, selector + " fitted dot count at " + width + "px");
    if (!columns) return geometry;
    const firstX = (width - 8 * (columns - 1)) / 2;
    const firstY = (height - 8 * (rows - 1)) / 2;
    const near = (actual, expected, message) => assert(Math.abs(actual - expected) < 0.04, message);
    for (const [index, dot] of dots.entries()) {
      const row = Math.floor(index / columns);
      const column = index % columns;
      near(dot.x, firstX + 8 * (rtl ? columns - 1 - column : column), selector + " horizontal pitch and centered gutters");
      near(dot.y, firstY + 8 * row, selector + " vertical pitch and centered gutters");
      near(dot.width, 4, selector + " dot width");
      near(dot.height, 4, selector + " dot height");
      assert.equal(dot.mask, "none");
      if (value !== undefined) assert.equal(dot.on, column * rows + row < Math.floor(dots.length * value / 100));
    }
    return geometry;
  };

  const testDotGridHelper = async () => {
    await read(`window.dotFixture = document.createElement('div');
      dotFixture.style.cssText = 'position:fixed;inset:0 auto auto 0;visibility:hidden;inline-size:min-content';
      dotFixture.innerHTML = '<div id="dot-fixture" data-dot-grid="progress" data-dot-value="0"></div>';
      document.body.append(dotFixture);`);
    const fixture = "#dot-fixture";
    assert.equal((await assertDotGrid(fixture, 2, 0)).width, 4, "An intrinsic-width grid reserves a full dot");
    for (const zoom of [1, 1.25]) {
      for (const width of [0, 3.875, 4, 11.875, 12, 12.125, 287.5]) {
        await read(`dotFixture.style.zoom = '${zoom}'; dotFixture.style.inlineSize = '${width}px'`);
        await assertDotGrid(fixture, 2, 0);
      }
    }
    await read("dotFixture.style.zoom = '1.25'; dotFixture.firstChild.dataset.dotValue = '65'");
    await assertDotGrid(fixture, 2, 65);
    await read(`dotFixture.dir = 'rtl';
      dotFixture.style.setProperty('--kozu-dot-active', 'linear-gradient(90deg, blue, green)');`);
    await assertDotGrid(fixture, 2, 65);
    assert.match(await read("getComputedStyle($('#dot-fixture [data-dot-on]')).backgroundImage"), /^linear-gradient/);
    await read("dotFixture.firstChild.dataset.dotValue = '100'");
    await assertDotGrid(fixture, 2, 100);
    await read("dotFixture.firstChild.dataset.dotGrid = 'waveform'");
    const waveform = await assertDotGrid(fixture, 7);
    assert(waveform.dots.some(dot => dot.on) && waveform.dots.some(dot => !dot.on));
    await read("dotFixture.remove(); delete window.dotFixture");
  };

  const assertAgentAndWaveform = async (width) => {
    const layout = await read(`(() => {
      const box = (selector) => $(selector).getBoundingClientRect();
      const name = box('.agent-identity');
      const meter = box('.agent-meter');
      const percent = box('.agent-percent');
      const waveform = box('[data-dot-grid=listening]');
      const left = box('#listen');
      const right = box('.composer-actions button:last-child');
      return {
        leftInset: meter.left - name.right, rightInset: percent.left - meter.right,
        rail: meter.width, name: name.width, percent: percent.width,
        waveform: waveform.width, available: window.innerWidth < 600
          ? box('.composer-actions').width : right.left - left.right - 16,
      };
    })()`);
    assert.equal(layout.leftInset, 8);
    assert.equal(layout.rightInset, 8);
    assert(layout.rail > Math.max(layout.name, layout.percent), "Progress meter is too short at " + width);
    assert(layout.waveform >= 96 && Math.abs(layout.waveform - layout.available) < 1, "Waveform does not fill available space at " + width);
    await assertDotGrid(".agent-meter", 2, 74);
    await assertDotGrid("[data-dot-grid=listening]", 3);
  };

  const assertGlassContrast = async (selector, inset, minimum, label) => {
    const { x, y, width, height, ink } = await read(`(() => {
      const element = $(${JSON.stringify(selector)});
      const text = ${JSON.stringify(label ?? "")};
      const ink = getComputedStyle(text ? element.querySelector(text) : element).color;
      const rect = element.getBoundingClientRect();
      return { x: Math.ceil(rect.x) + ${inset}, y: Math.ceil(rect.y) + ${inset},
        width: Math.floor(rect.width) - ${inset * 2}, height: Math.floor(rect.height) - ${inset * 2}, ink };
    })()`);
    await read(`[...$(${JSON.stringify(selector)}).children].forEach(child => child.style.visibility = 'hidden')`);
    const { data } = await send("Page.captureScreenshot", { format: "png", clip: { x, y, width, height, scale: 1 } });
    await read(`[...$(${JSON.stringify(selector)}).children].forEach(child => child.style.removeProperty('visibility'))`);
    const crop = await read(`(async () => {
      const image = new Image();
      image.src = 'data:image/png;base64,${data}';
      await image.decode();
      const canvas = document.createElement('canvas');
      canvas.width = image.width;
      canvas.height = image.height;
      const context = canvas.getContext('2d');
      context.drawImage(image, 0, 0);
      const { data } = context.getImageData(0, 0, image.width, image.height);
      const linear = (channel) => channel <= 10.31475 ? channel / 3294.6 : ((channel / 255 + .055) / 1.055) ** 2.4;
      const luminance = (r, g, b) => .2126 * linear(r) + .7152 * linear(g) + .0722 * linear(b);
      const text = luminance(...${JSON.stringify(ink)}.match(/[0-9]+/g).map(Number));
      let darkest = 1;
      let brightest = 0;
      for (let index = 0; index < data.length; index += 4) {
        const pixel = luminance(data[index], data[index + 1], data[index + 2]);
        darkest = Math.min(darkest, pixel);
        brightest = Math.max(brightest, pixel);
      }
      return [darkest, brightest].map(pixel => (Math.max(text, pixel) + .05) / (Math.min(text, pixel) + .05));
    })()`);
    assert(crop.every((ratio) => ratio >= minimum), selector + " contrast on darkest and brightest pixels: " + crop.join(", "));
    console.log(selector + " contrast on darkest and brightest rendered pixels: " + crop.map((ratio) => ratio.toFixed(2)).join(", "));
  };

  await send("Network.enable");
  await send("Page.enable");
  await viewport(1440, 960);
  await send("Page.navigate", { url: new URL("./index.html", import.meta.url).href });
  for (let attempt = 0; attempt < 80; attempt += 1) {
    if (await read("document.readyState === 'complete' && document.querySelector('#run-log li') !== null")) break;
    await setTimeout(100);
  }
  assert(await read("document.readyState === 'complete'"));
  await read("Promise.all([...document.images].map((photo) => photo.decode())).then(() => true)");
  await read("document.fonts.ready.then(() => true)");
  assert(await read("[...document.fonts].some(face => face.family === 'Inter' && face.status === 'loaded' && face.weight === '100 900')"), "The bundled Inter face did not load");

  await read(`window.$ = (selector) => document.querySelector(selector);
    window.click = (selector) => $(selector).click();
    window.text = (selector) => $(selector).textContent;
    window.activeView = () => $('.workspace-tabs [aria-selected=true]').getAttribute('aria-controls');
    window.paint = (selector, property) => {
      const sample = document.createElement('span');
      sample.style.color = 'var(' + property + ')';
      $(selector).append(sample);
      const color = getComputedStyle(sample).color;
      sample.remove();
      return color;
    };`);

  assert.equal(await read("activeView()"), "accounts");
  assert.equal(await read("text('.workspace-brand')"), "Kozu");
  assert.equal(await read("text('.workspace-guide')"), "Design guide");
  assert.equal(await read("$('.workspace-guide').getAttribute('href')"), "guide.html");
  const { nodes } = await send("Accessibility.getFullAXTree");
  assert(nodes.some(node => node.role?.value === "link" && node.name?.value === "Design guide"), "Design guide lacks an accessible link name");
  assert(nodes.some(node => node.name?.value === "117,450 dollars and 17 cents"), "Balance lacks an accessible amount");
  assert.equal(await read("getComputedStyle($('[data-transfer=pay]')).backgroundColor"), await read("paint('[data-transfer=pay]', '--kz-action')"));
  assert.deepEqual(await read("[...document.querySelectorAll('.ledger-photo + div > strong')].map(name => name.textContent)"), ["Morgan Lee", "Sam Rivera"]);
  const workspaceMaterial = await read("getComputedStyle(document.body).backgroundImage");
  const headingMaterial = await read("getComputedStyle($('.view-heading')).backgroundImage");
  const assertWorkspace = async (id) => {
    assert.equal(await read("activeView()"), id);
    assert.equal(await read("document.querySelectorAll('main > [role=tabpanel]:not([hidden])').length"), 1);
    assert.equal(await read("getComputedStyle(document.body).backgroundImage"), workspaceMaterial);
    assert.equal(await read(`getComputedStyle($('#${id} .view-heading')).backgroundImage`), headingMaterial);
    assert.deepEqual(await read("[...document.querySelectorAll('.workspace-tabs > button')].filter(el => el.tabIndex === 0 && el.getAttribute('aria-selected') === 'true').map(el => el.id)"), ["tab-" + id]);
  };
  await assertWorkspace("accounts");
  await testDotGridHelper();
  assert.equal(await read("text('.balance-amount')"), "$117,450.17");
  assert.equal(await read("getComputedStyle($('.balance-cents')).color"), await read("paint('.balance-value', '--kz-secondary')"));
  assert.equal(await read("getComputedStyle($('.kozu-skip')).clipPath"), "inset(50%)");
  assert.equal(await read("$('.kozu-symbols').getBoundingClientRect().height"), 0);
  assert.equal(await read("getComputedStyle($('#listen-status')).clipPath"), "inset(50%)");
  assert.equal(await read("[...document.images].filter(photo => photo.naturalWidth > 0).length"), 3);
  assert.equal(await read("getComputedStyle(document.body).fontFamily.split(',')[0]"), "Inter");
  await assertGlassContrast(".account-chip", 14, 4.5);
  await shot("accounts-desktop");
  await clickAt("#ledger-toggle");
  assert.equal(await read("$('#older-transactions').hidden"), false);
  await read("click('#ledger-toggle'); $('#dock-home').focus()");
  await press("ArrowRight", 39);
  assert.equal(await read("document.activeElement.id"), "dock-analytics");
  assert.equal(await read("$('#accounts-home').hidden"), true);
  assert.equal(await read("text('#spending-total')"), "$2,174.80");
  assert.equal(await read("text('#spending-selection')"), "Nov 22 · $751.75");
  assert.equal(await read("getComputedStyle(document.activeElement).outlineStyle"), "none");
  assert.equal(await read("getComputedStyle(document.activeElement).backgroundColor"), await read("paint('#dock-analytics', '--kz-focus')"));
  assert(await read("[...document.querySelectorAll('.chart-bar')].some(bar => bar.clientHeight > 20)"));
  assert.equal(await read("getComputedStyle($('.chart-bar')).backgroundColor"), await read("paint('#spending-chart', '--kz-graphite-500')"));
  await read('click(\'[data-period="month"]\')');
  assert.equal(await read("text('#spending-total')"), "$4,535.80");
  await press("End", 35);
  assert.equal(await read("$('#accounts-update').hidden"), false);
  await shot("accounts-update-desktop");
  await read("click('#dock-home'); $('[data-transfer=pay]').focus(); click('[data-transfer=pay]')");
  assert.equal(await read("$('#transfer-dialog').open"), true);
  assert.equal(await read("getComputedStyle($('#transfer-dialog'), '::backdrop').backdropFilter"), "blur(40px)");
  assert.equal(await read("getComputedStyle($('#transfer-dialog')).backgroundColor"), await read("paint('#transfer-dialog', '--kz-frost-overlay')"));
  await assertGlassContrast("#transfer-dialog", 22, 4.5, "h2");
  await shot("accounts-overlay");
  await press("Escape", 27);
  assert.equal(await read("$('#transfer-dialog').open"), false);
  assert.equal(await read("document.activeElement.matches('[data-transfer=pay]')"), true);
  await read(`click('[data-transfer=pay]');
    $('[name=recipient]').value = 'Sample business';
    $('[name=amount]').value = '24.50';
    $('#transfer-form').requestSubmit();`);
  assert.match(await read("text('#transfer-result')"), /24\.50 payment to Sample business/);

  await read("$('#tab-accounts').focus()");
  await press("ArrowRight", 39);
  await assertWorkspace("tasks");
  assert.equal(await read("document.activeElement.id"), "tab-tasks");
  assert.deepEqual(await read("[...document.querySelectorAll('.agent-identity strong')].map(name => name.textContent)"), ["Inbox", "Flow", "Scout"]);
  assert.equal(await read("getComputedStyle(document.body).fontFamily.split(',')[0]"), "Inter");
  assert.match(await read("getComputedStyle($('#composer-heading')).fontFamily"), /^"Helvetica Neue"/);
  assert.equal(await read("getComputedStyle($('#new-task')).backdropFilter"), "blur(28px)");
  await read(`click('details[open] [data-agent-action=pause]')`);
  assert.equal(await read("text('details[open] .agent-state')"), "Paused");
  assert.equal(await read("$('details[open] [data-agent-action=advance]').disabled"), true);
  await read(`click('details[open] [data-agent-action=pause]'); click('details[open] [data-agent-action=advance]')`);
  assert.equal(await read("text('details[open] .agent-percent')"), "51%");
  await read("click('#new-task')");
  assert.equal(await read("document.activeElement.id"), "task-input");
  await read("click('#listen')");
  assert.equal(await read("text('.listening-label')"), "Listening");
  assert.equal(await read("$('#listen').getAttribute('aria-label')"), "Stop listening");
  await assertAgentAndWaveform(1440);
  await assertDotGrid("details[open] .agent-meter", 2, 51);
  assert(await read("$('[data-dot-grid=listening]').getAnimations({ subtree: true }).length > 0"));
  await assertGlassContrast(".agents", 22, 4.5, ".panel-note");
  assert.equal(await read("getComputedStyle($('#composer-heading')).color"), await read("paint('.task-composer', '--kz-ink')"));
  await read("document.activeElement.blur()");
  await shot("tasks-desktop");
  await send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-motion", value: "reduce" }] });
  assert.equal(await read("$('[data-dot-grid=listening]').getAnimations({ subtree: true }).length"), 0);
  const still = await assertDotGrid("[data-dot-grid=listening]", 3);
  assert(still.dots.some(dot => dot.on) && still.dots.some(dot => !dot.on), "Reduced motion keeps the listening pattern");
  await send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-transparency", value: "reduce" }] });
  assert.equal(await read("getComputedStyle($('#new-task')).backdropFilter"), "none");
  assert.equal(await read("getComputedStyle($('.agents')).backgroundColor"), "rgb(13, 23, 38)");
  await shot("tasks-opaque");
  await send("Emulation.setEmulatedMedia", { features: [] });
  await read("click('#listen'); $('#task-form').requestSubmit()");
  assert.match(await read("text('#queued-tasks')"), /prepare a briefing/);

  await read("$('#tab-tasks').focus()");
  await press("ArrowRight", 39);
  await assertWorkspace("activity");
  assert.equal(await read("document.activeElement.id"), "tab-activity");
  assert.match(await read("getComputedStyle($('#run-log time')).fontFamily"), /^Menlo/);
  assert.equal(await read("getComputedStyle(document.body).fontFamily.split(',')[0]"), "Inter");
  assert.equal(await read("text('#incident-id')"), "INC-3318");
  assert.equal(await read("$('#run-log').children.length"), 5);
  assert.deepEqual(await read("[...document.querySelectorAll('.run-log use')].map(icon => icon.getAttribute('href'))"),
    ["#icon-alert", "#icon-search", "#icon-check"]);
  await read("document.activeElement.blur()");
  await shot("activity-desktop");
  await read("$('#replay-step').focus()");
  await press("ArrowLeft", 37);
  assert.equal(await read("$('#run-log').children.length"), 4);
  assert.equal(await read("$('#replay-step').getAttribute('aria-valuetext')"), "Event 4 of 5");
  assert(await read("$('.terminal-bars .is-future') !== null"));
  await read("$('#tab-eu').focus()");
  await press("End", 35);
  assert.equal(await read("text('#incident-id')"), "INC-3324");
  assert.equal(await read("$('#incident-view').getAttribute('aria-labelledby')"), "tab-stage");
  await read("click('#report-toggle')");
  assert.equal(await read("$('#incident-report').hidden"), false);
  assert.match(await read("text('#report-copy')"), /staging configuration/);
  await read("click('#report-toggle'); click('#tab-eu'); click('#tab-tasks')");
  assert.equal(await read("text('details[open] .agent-percent')"), "51%");

  await read("$('#transfer-result').textContent = ''; $('#task-input').value = ''; document.activeElement.blur()");
  for (const width of [390, 320, 600, 768]) {
    await viewport(width, 844, width < 600);
    const orientation = width < 600 ? "horizontal" : "vertical";
    for (let attempt = 0; attempt < 20 && await read("$('.workspace-tabs').getAttribute('aria-orientation')") !== orientation; attempt += 1) {
      await setTimeout(25);
    }
    assert.equal(await read("$('.workspace-tabs').getAttribute('aria-orientation')"), orientation);
    if (orientation === "vertical") {
      await read("$('#tab-accounts').focus()");
      await press("ArrowDown", 40);
      await assertWorkspace("tasks");
      assert.equal(await read("$('.workspace-tabs').getBoundingClientRect().width"), 72);
      assert.equal(await read("$('.workspace-tabs').getBoundingClientRect().x"), 16);
      assert.equal(await read("$('.workspace-tabs > button').getBoundingClientRect().height"), 56);
    }
    for (const id of ["accounts", "tasks", "activity"]) {
      await read("window.scrollTo(0, 0)");
      await clickAt("#tab-" + id);
      await assertWorkspace(id);
      assert.equal(await read("document.documentElement.scrollWidth"), width, id + " overflow at " + width);
      const edges = await read(`[...document.querySelectorAll('button, input, textarea, summary, dialog, .kozu-card, .kozu-frost')].filter(el => el.getClientRects().length).some(el => ['Top','Right','Bottom','Left'].some(side => parseFloat(getComputedStyle(el)['border' + side + 'Width']) > 0))`);
      assert(!edges, id + " rendered an element border");
      if (width < 600) {
        const smallTargets = await read(`[...document.querySelectorAll('a.workspace-guide, button, summary, input, textarea')]
          .filter(el => el.checkVisibility() && !el.disabled)
          .filter(el => el.getBoundingClientRect().width < 48 || el.getBoundingClientRect().height < 48)
          .map(el => el.getAttribute('aria-label') || el.textContent || el.id)`);
        assert.deepEqual(smallTargets, [], id + " at " + width + " has small touch targets");
      }
      if (id === "tasks") {
        await read("click('#listen')");
        await assertAgentAndWaveform(width);
      }
      if (width === 390) {
        await shot(id + "-mobile");
        if (id === "tasks" && capture) {
          await read("$('.task-composer').scrollIntoView({ block: 'center' })");
          await shot("tasks-listening-mobile");
        }
      }
      if (id === "tasks") await read("click('#listen')");
    }
  }

  await read("document.documentElement.style.fontSize = '200%'");
  for (const width of [320, 390, 768]) {
    await viewport(width, 844, width < 600);
    for (const id of ["accounts", "tasks", "activity"]) {
      await read("click('#tab-" + id + "')");
      const scrollWidth = await read("document.documentElement.scrollWidth");
      if (scrollWidth > width) {
        const overflowing = await read(`[...document.body.querySelectorAll('*')]
          .filter(el => el.getBoundingClientRect().right > ${width}).slice(0, 8)
          .map(el => el.id || el.className || el.tagName)`);
        assert.fail(id + " overflow at 200% text and " + width + "px: " + overflowing.join(", "));
      }
    }
  }
  await read("document.documentElement.style.fontSize = ''");

  const materials = ["blue"];
  assert(requests.some((url) => url.endsWith("/Fonts/InterVariable.woff2")));
  for (const image of materials) {
    assert(requests.some((url) => url.endsWith("/Assets/Materials/" + image + ".jpg")), image + " was not requested");
  }
  assert(await read(`Promise.all(${JSON.stringify(materials)}.map(name => {
    const image = new Image();
    image.src = '../Assets/Materials/' + name + '.jpg';
    return image.decode();
  })).then(() => true)`));
  assert(!requests.some((url) => /^https?:/.test(url)), "The local reference made a remote request");
  await viewport(390, 844, true);
  await read("window.scrollTo(0, 0)");
  await clickAt(".workspace-guide");
  const guideReady = "location.pathname.endsWith('/guide.html') && document.querySelector('h1')?.textContent.includes('Kozu')";
  for (let attempt = 0; attempt < 40 && !await read(guideReady); attempt += 1) await setTimeout(50);
  assert(await read(guideReady), "Design guide did not open from the mobile workspace");
  const guideProgress = "#progress-indicator [data-dot-grid]";
  const guideListening = "#listening-indicator [data-dot-grid]";
  const guideValue = await read(`Number(document.querySelector(${JSON.stringify(guideProgress)}).dataset.dotValue)`);
  await assertDotGrid(guideProgress, 2, guideValue);
  await assertDotGrid(guideListening, 3);
  await read("document.querySelector('#listening-indicator [data-wave-mode]').click()");
  await assertDotGrid(guideListening, 7);
  console.log("Chrome passed workspace interactions, shared demo and guide dot geometry, glass contrast, accessibility preferences and adaptive layouts.");
} finally {
  socket?.close();
  browser.kill();
  await stopped;
  await rm(profile, { recursive: true, force: true });
}
